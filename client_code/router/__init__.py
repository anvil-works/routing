# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff: noqa: F401, F811
from anvil.history import history as _history

from ._alert import alert, confirm
from ._cached import clear_cache
from ._constants import (
    CACHE_FIRST,
    NETWORK_FIRST,
    NO_CACHE,
    STALE_WHILE_REVALIDATE,
)
from ._context import RoutingContext
from ._exceptions import NotFound, Redirect
from ._invalidate import invalidate
from ._loader import use_data
from ._logger import debug_logging, logger
from ._navigate import navigate
from ._route import Route, TemplateWithContainerRoute, open_form
from ._router import NavigationBlocker, launch, navigation_emitter
from ._url import get_url
from ._view_transition import use_transitions

__version__ = "0.3.4"


def add_event_handler(event_name, fn):
    return navigation_emitter.add_event_handler(event_name, fn)


def remove_event_handler(event_name, fn):
    return navigation_emitter.remove_event_handler(event_name, fn)


def go(n=0):
    return _history.go(n)


def back():
    return _history.go(-1)


def forward():
    return _history.go(1)


def get_routing_context():
    return RoutingContext._current


def reload(hard=False):
    logger.debug(f"reload called with hard={hard}")
    if hard:
        _history.reload()
    else:
        invalidate(path=_history.location.path)

        _history.replace(_history.location)
