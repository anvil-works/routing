# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.history import Location, history

from ._constants import NOT_FOUND
from ._exceptions import InvalidPathParams
from ._logger import logger
from ._segments import Segment
from ._utils import dumps, encode_query_params, ensure_dict, loads, url_encode

__version__ = "0.3.6"


def clean_path(path, params):
    if path is None:
        return history.location.path

    # remove leading dots
    segments = Segment.from_path(path)

    leading_dots = path.startswith(".")

    path = ""

    for segment in segments:
        if segment.is_static():
            path += "/" + url_encode(segment.value)
        elif segment.is_param():
            value = params.get(segment.value, NOT_FOUND)
            if value is NOT_FOUND:
                raise InvalidPathParams(f"No path param for {segment.value}")
            path += "/" + url_encode(str(value))

    if leading_dots:
        # remove the leasing slash
        path = path[1:]

    return path


def stringify_value(val):
    if not isinstance(val, str):
        return dumps(val)

    try:
        # this way strings are flat like foo=bar
        # and already jsonified strings are returned as is
        val = loads(val)
        return dumps(val)
    except Exception:
        return val


def clean_query_params(query):
    if not query:
        return {}

    if callable(query):
        from ._context import RoutingContext

        context = RoutingContext._current
        if context is None:
            prev = {}
        else:
            prev = context.query

        query = query(prev)

        query = ensure_dict(query, "query")

    real_query = {}
    keys = sorted(query.keys())
    for key in keys:
        real_query[key] = stringify_value(query[key])

    return real_query


def nav_args_to_location(*, path, query, params, hash):
    if path is not None:
        path = clean_path(path, params or {})
        query = clean_query_params(query)
        search = encode_query_params(query)
        return Location(path=path, search=search, hash=hash)

    if query is not None:
        # use the current location as the base
        path = history.location.path
        query = clean_query_params(query)
        search = encode_query_params(query)
        return Location(path=path, search=search, hash=hash)

    if hash is not None:
        return Location(
            path=history.location.path,
            search=history.location.search,
            hash=hash,
        )

    return history.location


def get_nav_location(context_or_path_or_url, *, path, query, params, hash):
    if context_or_path_or_url is not None:
        # do we need to worry about path params here?
        # currently we just ignore them
        # potentially we could do path params with a context
        # but we'd need to use the context.route.path

        from ._context import RoutingContext  # circular import

        if isinstance(context_or_path_or_url, RoutingContext):
            temp_location = context_or_path_or_url.location
        elif isinstance(context_or_path_or_url, str):
            temp_location = Location.from_url(context_or_path_or_url)
        else:
            raise TypeError(
                "location_or_url_or_path must be a string or a Routing Context"
            )

        if path is not None:
            raise TypeError("cannot set named argument path if a first argument is set")

        location = nav_args_to_location(
            path=temp_location.path,
            query=query,
            params=params,
            hash=hash,
        )

        # search params on a raw location are a bit gnarly
        # they are json stringified so we would be json stringifying again
        # let's not do that
        if hash is None and query is None:
            location.search = temp_location.search
            location.hash = temp_location.hash
        elif query is None:
            location.search = temp_location.search

    else:
        location = nav_args_to_location(
            path=path, query=query, params=params, hash=hash
        )

    return location


_current_nav_context = {}
_current_form_properties = {}


def navigate_with_location(
    location, replace=False, nav_context=None, form_properties=None
):
    global _current_nav_context, _current_form_properties

    nav_context = ensure_dict(nav_context, "nav_context")
    form_properties = ensure_dict(form_properties, "form_properties")

    _current_nav_context = nav_context
    _current_form_properties = form_properties
    current_location = history.location

    if (
        current_location.path == location.path
        and current_location.search == location.search
        and current_location.hash == location.hash
    ):
        logger.debug("unchanged navigation location - exiting")
        return

    if replace:
        history.replace(location)
    else:
        history.push(location)


def navigate(
    context_or_path_or_url=None,
    *,
    path=None,
    params=None,
    query=None,
    hash=None,
    replace=False,
    nav_context=None,
    form_properties=None,
):
    logger.debug(
        f"navigate called with: {context_or_path_or_url!r} path={path!r} "
        if path is not None
        else f"params={params!r} "
        if params is not None
        else f"query={query!r} "
        if query is not None
        else f"hash={hash!r} "
        if hash
        else f"replace={replace!r} "
        if replace
        else f"nav_context={nav_context!r} "
        if nav_context is not None
        else f"form_properties={form_properties!r} "
        if form_properties is not None
        else ""
    )
    location = get_nav_location(
        context_or_path_or_url, path=path, query=query, params=params, hash=hash
    )
    logger.debug(f"navigate location: {location}")

    nav_context = ensure_dict(nav_context, "nav_context")
    form_properties = ensure_dict(form_properties, "form_properties")

    return navigate_with_location(
        location,
        replace=replace,
        nav_context=nav_context,
        form_properties=form_properties,
    )
