from curses import window
from time import sleep

import anvil
from anvil.history import history
from anvil.js import window

from ..navigate import navigate
from ..redirect import Redirect
from ..context import Context
from ..utils import TIMEOUT, await_promise, timeout, Promise, encode_search_params
from ..routes import sorted_routes
from ..matcher import get_match
from ..loader import load_data, cache, load_data_promise, CachedData

waiting = False
undoing = False
redirect = True
current = {"delta": None}

navigation_blockers = set()
before_unload_blockers = set()


def _beforeunload(e):
    e.preventDefault()  # cancel the event
    e.returnValue = ""  # chrome requires a returnValue to be set


class NavigationBlocker:
    def __init__(self, warn_before_unload=False):
        self.warn_before_unload = warn_before_unload

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
            if not before_unload_blockers:
                window.addEventListener("beforeunload", _beforeunload)
            before_unload_blockers.add(self)

    def unblock(self):
        global waiting
        navigation_blockers.remove(self)
        waiting = bool(navigation_blockers)
        if self.warn_before_unload:
            before_unload_blockers.remove(self)
            if not before_unload_blockers:
                window.removeEventListener("beforeunload", _beforeunload)


def stop_unload():
    global undoing
    undoing = True
    delta = current.get("delta")
    if delta is not None:
        history.go(-delta)


def on_navigate():

    location = history.location
    key = location.key

    def is_stale():
        return key != history.location.key

    prev_context = Context._current
    if prev_context is not None:
        with NavigationBlocker():
            if prev_context._prevent_unload():
                stop_unload()

    if is_stale():
        return

    match = get_match(location)
    if match is None:
        raise Exception("No match")

    route = match.route
    pending_form = route.pending_form
    pending_delay = route.pending_delay

    try:
        route.before_load()
    except Redirect as r:
        return navigate(**r.__dict__, replace=True)

    context = Context._current = Context(match)
    # TODO: decide what to do if only search params change or only hash changes
    # if only search params change, we need to load data
    # but the form might be using navigate_on_search_change=False
    # so we need to emit the search_changed event
    # if hash changes, just emit the hash_changed event

    data_promise = load_data_promise(match)
    result = Promise.race([data_promise, timeout(pending_delay)])

    if is_stale():
        return

    if pending_form is not None and result is TIMEOUT:
        anvil.open_form(pending_form)
        sleep(pending_delay)

    data = await_promise(data_promise)
    if is_stale():
        return

    context.data = data

    form = route.form
    anvil.open_form(form, context=context)


def listener(args):
    global waiting, undoing, redirect, current

    if undoing:
        undoing = False
    elif waiting:
        delta = args.get("delta")
        if delta is not None:
            undoing = True
            history.go(-delta)
        else:
            # user determined to navigate
            history.reload()
    else:
        current = args

        if redirect:
            on_navigate()
        else:
            redirect = True


def create():
    from anvil.history import history
    from anvil.server import startup_data

    if startup_data is not None:
        startup_cache = startup_data.get("cache", {})
        cache.update(startup_cache)

    print("STARTUP DATA")
    if startup_data is not None:
        startup_cache = startup_data.get("cache", {})
        for key, val in startup_cache.items():
            print(key, repr(val.__dict__)[:20])

    history.listen(listener)
    on_navigate()
    # TODO navigate to the first page
