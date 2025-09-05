# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from ._cached import CACHED_DATA, CACHED_FORMS
from ._constants import STALE_WHILE_REVALIDATE
from ._logger import logger
from ._utils import decode_key, ensure_dict, make_key, valid_absolute_path

__version__ = "0.4.1"


def get_invalid_keys(start_path, start_deps):
    keys = []

    if start_path == "/":
        start_parts = []
    else:
        start_parts = start_path.split("/")

    for key in CACHED_DATA.keys() | CACHED_FORMS.keys():
        path, deps = decode_key(key)
        if path == "/":
            parts = []
        else:
            parts = path.split("/")

        if parts[: len(start_parts)] != start_parts:
            continue

        match = True
        for dep_key in start_deps.keys():
            if start_deps[dep_key] != deps[dep_key]:
                match = False
                break

        if match:
            keys.append(key)

    return keys


def invalidate(context_or_path=None, *, path=None, deps=None, exact=False):
    from ._context import RoutingContext

    if isinstance(context_or_path, RoutingContext):
        if path is not None:
            raise TypeError("cannot set named argument path if a first argument is set")
        if deps is not None:
            raise TypeError(
                "cannot set named argument deps if a first argument is a RoutingContext"
            )
        path = context_or_path.path
        deps = context_or_path.deps
    else:
        if context_or_path is not None:
            if not isinstance(context_or_path, str):
                raise TypeError("context_or_path must be a string or a Routing Context")
            if path is not None:
                raise TypeError(
                    "cannot set named argument path if a first argument is set"
                )
            path = context_or_path
        elif path is None:
            raise TypeError("path must be set")

        path = valid_absolute_path(path)
        deps = ensure_dict(deps, "deps")

    key = make_key(path, deps)

    if exact:
        keys = [make_key(path, deps)]

    else:
        keys = get_invalid_keys(path, deps)

    if keys:
        logger.debug(f"invalidating keys: {keys}")
    else:
        logger.debug("no keys to invalidate")

    for key in keys:
        CACHED_FORMS.pop(key, None)

        cached = CACHED_DATA.pop(key, None)
        if cached is not None and cached.mode == STALE_WHILE_REVALIDATE:
            cached.stale = True
            CACHED_DATA[key] = cached
