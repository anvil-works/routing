# Copyright (c) 2026 Anvil
# SPDX-License-Identifier: MIT

"""Scroll policies for the document and explicitly registered elements."""

import json
from math import isfinite

from anvil.history import Location, history
from anvil.js import get_dom_node, window

__version__ = "0.6.2"

_displayed = None
_suspended = False
_generation = 0
_started = False


def _storage_key(key, area_id=None):
    identity = json.dumps([key, area_id])
    return f"anvil-routing-scroll-v2:{Location(path='/').get_url(True)}:{identity}"


def _read_position(key, area_id):
    try:
        position = json.loads(
            window.sessionStorage.getItem(_storage_key(key, area_id)) or "null"
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
    key, form, areas = _displayed
    if not get_dom_node(form).isConnected:
        return
    for node, area_id, policy in areas:
        if policy != "restore" or (node is not None and not node.isConnected):
            continue
        position = (
            [window.scrollX, window.scrollY]
            if node is None
            else [node.scrollLeft, node.scrollTop]
        )
        try:
            window.sessionStorage.setItem(
                _storage_key(key, area_id), json.dumps(position)
            )
        except Exception:
            # Storage is optional; never retain a second position cache.
            pass


def _policy(value, default):
    if value == "default":
        value = default
    if value not in ("auto", "restore", "none"):
        raise ValueError(f"Invalid routing scroll policy: {value!r}")
    return value


def _areas(route):
    default = _policy(route.scroll_default, None)
    areas = [(None, None, _policy(route.scroll_document, default))]
    if route.scroll_manage_elements:
        ids = set()
        for node in window.document.querySelectorAll("[data-routing-scroll-id]"):
            area_id = node.getAttribute("data-routing-scroll-id")
            if not area_id or area_id in ids:
                raise ValueError(
                    "data-routing-scroll-id must be nonempty and unique on the page"
                )
            ids.add(area_id)
            value = node.getAttribute("data-routing-scroll")
            policy = _policy("default" if value is None else value, default)
            areas.append((node, area_id, policy))
    return areas


def _scroll_to(node, x, y):
    target = window if node is None else node
    target.scrollTo({"left": x, "top": y, "behavior": "instant"})


def _anchor(location, manage_elements):
    if not location.hash:
        return None, None
    fragment = location.hash[1:] if location.hash.startswith("#") else location.hash
    try:
        fragment = window.decodeURIComponent(fragment)
    except Exception:
        pass
    target = window.document.getElementById(fragment)
    owner = None
    if target is not None and manage_elements:
        # A target scrolls within its ancestors, not within itself.
        parent = target.parentElement
        if parent is not None:
            owner = parent.closest("[data-routing-scroll-id]")
    return target, owner


def _scroll_to_anchor(node, target):
    margin = window.parseFloat(window.getComputedStyle(target).scrollMarginTop)
    if not isfinite(margin):
        margin = 0
    top = target.getBoundingClientRect().top - margin
    if node is None:
        _scroll_to(None, window.scrollX, window.scrollY + top)
    else:
        top += node.scrollTop - node.getBoundingClientRect().top - node.clientTop
        _scroll_to(node, node.scrollLeft, top)


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
    def __init__(self, context):
        global _generation, _suspended
        self.location = context.location
        self.route = context.route
        self.key = self.route.scroll_restoration_key(self.location)
        _snapshot()
        _generation += 1
        _suspended = True
        self.generation = _generation

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
            # Invalid configuration must not leave outgoing state eligible for saving.
            _displayed = None
            try:
                areas = _areas(self.route)
                target, owner = _anchor(
                    self.location, self.route.scroll_manage_elements
                )
                for node, area_id, policy in areas:
                    if policy == "none":
                        continue
                    position = (
                        _read_position(self.key, area_id)
                        if policy == "restore"
                        else None
                    )
                    if position is not None:
                        _scroll_to(node, position[0], position[1])
                    elif self.location.hash:
                        if target is not None and node == owner:
                            _scroll_to_anchor(node, target)
                    else:
                        _scroll_to(node, 0, 0)
                _displayed = (self.key, form, areas)
            finally:
                _suspended = False

        window.requestAnimationFrame(apply)
