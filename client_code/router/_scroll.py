# Copyright (c) 2026 Anvil
# SPDX-License-Identifier: MIT

"""Document scrolling after a destination form has attached."""

import json
from math import isfinite

from anvil.history import Location, history
from anvil.js import get_dom_node, window

__version__ = "0.6.2"

_displayed = None
_suspended = False
_generation = 0
_started = False


def _storage_key(key):
    return f"anvil-routing-scroll-v1:{Location(path='/').get_url(True)}:{key}"


def _read_position(key):
    try:
        position = json.loads(
            window.sessionStorage.getItem(_storage_key(key)) or "null"
        )
        if (
            isinstance(position, list)
            and len(position) == 2
            and all(type(n) in (int, float) and isfinite(n) for n in position)
        ):
            return position
    except Exception:
        # Storage is optional. Do not retain a second, in-memory cache.
        pass
    return None


def _snapshot(*args):
    if _displayed is None or _suspended:
        return
    key, form, restore = _displayed
    if not restore or not get_dom_node(form).isConnected:
        return
    try:
        window.sessionStorage.setItem(
            _storage_key(key), json.dumps([window.scrollX, window.scrollY])
        )
    except Exception:
        pass


def setup():
    global _started
    if _started:
        return
    _started = True
    # Anvil uses the same sentinel for every unkeyed full-document entry.
    # Persist a real key before launch, retaining it on subsequent reloads.
    location = history.location
    if location.key == "default":
        history.replace(
            Location(
                path=location.path,
                search=location.search,
                hash=location.hash,
                state=location.state,
            )
        )
    window.history.scrollRestoration = "manual"
    window.addEventListener("pagehide", _snapshot)


class ScrollNavigation:
    def __init__(self, context, *, restore):
        global _generation, _suspended
        _snapshot()
        _generation += 1
        _suspended = True
        self.generation = _generation
        self.location = context.location
        self.route = context.route
        self.restore = restore

    def _current(self):
        return (
            self.generation == _generation and self.location.key == history.location.key
        )

    def cancel(self):
        global _suspended
        if self._current():
            _suspended = False

    def commit(self, form):
        if not self._current() or form is None:
            return

        def apply(timestamp):
            global _displayed, _suspended
            if not self._current() or not get_dom_node(form).isConnected:
                return
            reset = self.route.reset_scroll
            anchor = self.route.hash_scroll_into_view

            try:
                position = None
                if reset and self.restore and self.route.scroll_restoration:
                    position = _read_position(self.location.key)
                if position is not None:
                    window.scrollTo(
                        {"left": position[0], "top": position[1], "behavior": "instant"}
                    )
                elif self.location.hash:
                    if anchor:
                        fragment = self.location.hash.lstrip("#")
                        try:
                            fragment = window.decodeURIComponent(fragment)
                        except Exception:
                            pass
                        target = window.document.getElementById(fragment)
                        if target is not None:
                            margin = window.parseFloat(
                                window.getComputedStyle(target).scrollMarginTop
                            )
                            if not isfinite(margin):
                                margin = 0
                            window.scrollTo(
                                {
                                    "left": window.scrollX,
                                    "top": window.scrollY
                                    + target.getBoundingClientRect().top
                                    - margin,
                                    "behavior": "instant",
                                }
                            )
                elif reset:
                    window.scrollTo({"left": 0, "top": 0, "behavior": "instant"})
            finally:
                _displayed = (self.location.key, form, self.route.scroll_restoration)
                _suspended = False

        window.requestAnimationFrame(apply)
