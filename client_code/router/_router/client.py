# Copyright (c) 2024-2026 Anvil
# SPDX-License-Identifier: MIT

from time import sleep

import anvil
from anvil.history import history
from anvil.js import window
from anvil.js.window import WeakMap, clearTimeout

from .. import _navigate, _scroll
from .._cached import CACHED_FORMS
from .._context import RoutingContext
from .._exceptions import NotFound, Redirect
from .._loader import CACHED_DATA, load_data_promise
from .._logger import logger
from .._matcher import get_match, get_not_found_match
from .._meta import update_meta_tags
from .._navigate import navigate
from .._utils import (
    TIMEOUT,
    EventEmitter,
    Promise,
    await_promise,
    ensure_dict,
    setTimeout,
    timeout,
)
from .._view_transition import ViewTransition

__version__ = "0.7.0"

waiting = False
undoing = False
redirect = True
current = {"delta": None}

navigation_blockers = set()
before_unload_blockers = set()

form_to_context = WeakMap()


def get_context(form) -> RoutingContext:
    rv = form_to_context.get(form)
    if rv is None:
        raise ValueError(f"No context for form {form}")
    return rv


def _register_form_reloader(form, context):
    register = getattr(anvil, "_register_live_form_reloader", None)
    if register is None:
        return

    def prepare_reload(old_form):
        if (
            old_form is not anvil.get_open_form()
            or context is not RoutingContext._current
            or context.revalidating
            or waiting
        ):
            return None

        location_key = history.location.key

        def is_current(expected_context):
            return (
                history.location.key == location_key
                and anvil.get_open_form() is old_form
                and RoutingContext._current is expected_context
                and not waiting
                and not expected_context.revalidating
            )

        def reload_form():
            if not is_current(context):
                raise RuntimeError("Navigation changed while preparing Form reload")

            # Constructors register context listeners and blockers. A new context
            # gives the replacement its own registrations instead of retaining
            # callbacks into the outgoing Form.
            replacement_context = RoutingContext(
                match=context.match,
                data=context.data,
                nav_context=context.nav_context,
                form_properties=context.form_properties,
            )
            replacement_context._error = context.error
            from .._import_utils import import_form

            # Match normal navigation: constructors and helpers that ask the
            # router for its current context must see the replacement context.
            RoutingContext._current = replacement_context
            replacement = import_form(
                context.route.form,
                routing_context=replacement_context,
                **replacement_context.form_properties,
            )
            if not is_current(replacement_context):
                raise RuntimeError("Navigation changed during Form reload")

            for key, cached_form in list(CACHED_FORMS.items()):
                if cached_form is old_form:
                    CACHED_FORMS[key] = replacement
            form_to_context.set(replacement, replacement_context)
            form_to_context.delete(old_form)
            _register_form_reloader(replacement, replacement_context)
            return replacement

        return reload_form

    # This adapter repairs these caches, not arbitrary app globals retaining form.
    register(form, prepare_reload, [CACHED_FORMS, form_to_context])


class _NavigationEmitter(EventEmitter):
    _events = ["navigate", "pending", "idle"]


navigation_emitter = _NavigationEmitter()


def _beforeunload(e):
    e.preventDefault()  # cancel the event
    e.returnValue = ""  # chrome requires a returnValue to be set


class UnloadBlocker:
    def block(self):
        if not before_unload_blockers:
            window.addEventListener("beforeunload", _beforeunload)
        before_unload_blockers.add(self)

    def unblock(self):
        before_unload_blockers.remove(self)
        if not before_unload_blockers:
            window.removeEventListener("beforeunload", _beforeunload)


class NavigationBlocker:
    def __init__(self, warn_before_unload=False):
        self.warn_before_unload = warn_before_unload
        self.unload_blocker = UnloadBlocker()

    def __enter__(self):
        self.block()
        return self

    def __exit__(self, *args):
        self.unblock()
        return False

    def block(self):
        global waiting
        waiting = True
        navigation_blockers.add(self)
        if self.warn_before_unload:
            self.unload_blocker.block()

    def unblock(self):
        global waiting
        navigation_blockers.remove(self)
        waiting = bool(navigation_blockers)
        if self.warn_before_unload:
            self.unload_blocker.unblock()


def stop_unload():
    global undoing
    undoing = True
    delta = current.get("delta")
    if delta is not None:
        history.go(-delta)
    sleep(0)  # give control back to event loop


def gc():
    for key, cached in CACHED_DATA.copy().items():
        if cached._should_gc():
            logger.debug(f"releasing {key} from the cache for garbage collection")
            CACHED_DATA.pop(key, None)
            CACHED_FORMS.pop(key, None)


def _do_navigate(context):
    match = context.match
    route = match.route
    location = context.location

    def is_stale():
        stale = location.key != history.location.key
        if stale:
            logger.debug(f"stale navigation detected exiting: {location}")
        return stale

    pending_form = route.pending_form
    pending_delay = route.pending_delay
    pending_min = route.pending_min

    def handle_error(form_attr, error):
        if is_stale():
            return
        logger.debug(f"navigation error: {error}")
        context.set_data(None, error)

        form = getattr(route, form_attr, None)
        if form is None:
            raise error

        with ViewTransition():
            return route.load_form(form, context)

    try:
        nav_context = route.before_load(**context._loader_args)
        nav_context = ensure_dict(nav_context, "before_load")
        context.nav_context.update(nav_context)
    except Redirect as r:
        return navigate(**r.__dict__, replace=True)
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    # Optimistically update meta tags before opening the form
    meta = route.meta(**context._loader_args)
    meta = ensure_dict(meta, "meta")
    update_meta_tags(meta)

    logger.debug(f"Match key {match.key}")
    # don't do this because it prevents reloading the same form
    # if prev_context is not None and match.key == prev_context.match.key:
    #     form = anvil.get_open_form()
    #     if form is not None and form_to_context.get(form) is prev_context:
    #         prev_context._update(context)
    #         logger.debug(f"navigation would return the same form: {form}")
    #         return

    if match.key in CACHED_FORMS:
        form = CACHED_FORMS[match.key]
        logger.debug(f"found a cached form for this location: {form}")
        cached_context = get_context(form)
        logger.debug(f"updating cached form context: {cached_context.location}")
        cached_context._update(context)
        RoutingContext._current = cached_context
        if anvil.get_open_form() is form:
            logger.debug(f"cached form is already open: {form}")
            return form
        return match.route.load_form(form, cached_context)

    # TODO: how does cached forms work with cache modes for data?
    data_promise = load_data_promise(context)

    try:
        result = Promise.race([data_promise, timeout(pending_delay)])
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    if is_stale():
        return

    if pending_form is not None and result is TIMEOUT:
        logger.debug(
            f"exceeded pending delay: {pending_delay},"
            f" loading pending form {pending_form!r}"
        )
        with ViewTransition():
            route.load_form(pending_form, context)
        sleep(pending_min)

    try:
        data, error = await_promise(data_promise)
        context.set_data(data, error)
        # if it failed we can't be using the cached data
        if error is not None:
            raise error
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    if is_stale():
        return

    form = route.form
    try:
        with ViewTransition():
            rv = route.load_form(form, context)
        form_to_context.set(rv, context)
        if route.cache_form:
            CACHED_FORMS[match.key] = rv
        # A custom load_form can own a nested page or a different reconstruction
        # boundary; only the ordinary top-level route delegates reload here.
        from .._route import Route

        if type(route).load_form is Route.load_form:
            _register_form_reloader(rv, context)
        return rv

    except Exception as e:
        return handle_error("error_form", e)


def on_navigate():
    location = history.location
    logger.debug("navigating")
    nav_context = _navigate._current_nav_context
    form_properties = _navigate._current_form_properties

    prev_context = RoutingContext._current
    if prev_context is not None:
        with NavigationBlocker(True):
            if prev_context._prevent_unload():
                logger.debug(f"navigation blocked by {prev_context.location}")
                stop_unload()
                return

    match = get_match(location)
    found = match is not None
    if not found:
        from .._route import default_not_found_route_cls

        if default_not_found_route_cls is not None:
            match = get_not_found_match(location, default_not_found_route_cls)
        else:
            raise NotFound(f"No match for '{location}'")

    context = RoutingContext(
        match=match, nav_context=nav_context, form_properties=form_properties
    )
    if not found:
        context.set_data(None, NotFound(f"No match for '{location}'"))

    scroll_navigation = _scroll.ScrollNavigation(context)
    RoutingContext._current = context

    gc()

    kws = {**context._loader_args, "routing_context": context}
    setTimeout(lambda: navigation_emitter.raise_event("navigate", **kws))
    pending = setTimeout(lambda: navigation_emitter.raise_event("pending", **kws))
    try:
        form = _do_navigate(context)
        if form is not None:
            scroll_navigation.commit(form)
        else:
            scroll_navigation.cancel()
    except Exception:
        scroll_navigation.cancel()
        raise
    finally:
        clearTimeout(pending)
        setTimeout(lambda: navigation_emitter.raise_event("idle", **kws))


def listener(**listener_args):
    global waiting, undoing, redirect, current

    if undoing:
        undoing = False
    elif waiting:
        delta = listener_args.get("delta")
        if delta is not None:
            undoing = True
            history.go(-delta)
        else:
            # user determined to navigate
            history.reload()
    else:
        current = listener_args

        if redirect:
            on_navigate()
        else:
            redirect = True


def launch():
    from anvil.history import history
    from anvil.server import startup_data

    from .._import_utils import import_routes

    import_routes()

    if startup_data is not None:
        startup_cache = startup_data.get("cache", {})
        CACHED_DATA.update(startup_cache)
        logger.debug(f"startup data: {startup_cache}")

    _scroll.setup()
    history.listen(listener)
    on_navigate()
