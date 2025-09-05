# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from ._invalidate import invalidate
from ._loader import load_data
from ._matcher import Match
from ._utils import EventEmitter, ensure_dict

__version__ = "0.4.1"


class RoutingContext(EventEmitter):
    _current: "RoutingContext" = None
    _events = [
        "data_loaded",
        "data_loading",
        "data_error",
        "query_changed",
        "hash_changed",
    ]

    def __init__(self, match: Match, data=None, nav_context=None, form_properties=None):
        self.match = match
        self.deps = match.deps
        self.location = match.location
        self.path = match.path
        self.params = match.params
        self.query = match.query
        self.hash = match.hash
        self.route = match.route
        self.nav_context = ensure_dict(nav_context, "nav_context")
        self.form_properties = ensure_dict(form_properties, "form_properties")
        self._error = None
        self._data = data
        self._listeners = {}
        self._blockers = set()

    def _update(self, context):
        prev_match = self.match

        self.match = context.match
        self.deps = context.match.deps
        self.nav_context = context.nav_context
        self.form_properties = context.form_properties
        self.location = context.match.location
        self.path = context.match.path
        self.params = context.match.params
        self.query = context.match.query
        self.hash = context.match.hash
        self.route = context.match.route

        if prev_match.query != self.query:
            self.raise_event("query_changed", query=self.query)
        if prev_match.hash != self.hash:
            self.raise_event("hash_changed", hash=self.hash)

    def _prevent_unload(self):
        for blocker in list(self._blockers):
            if blocker not in self._blockers:
                # we were removed while blocking
                continue
            if blocker():
                return True
        return False

    def register_blocker(self, blocker):
        self._blockers.add(blocker)

    def unregister_blocker(self, blocker):
        self._blockers.discard(blocker)

    def invalidate(self, exact=False):
        # remove ourselves from cached forms and cached data
        invalidate(self, exact=exact)

    def set_data(self, data, error=None):
        if error is not None:
            self._error = error
            self.raise_event("data_error", error=error)
        else:
            self._data = data
            self.raise_event("data_loaded", data=data)

    @property
    def data(self):
        return self._data

    @property
    def error(self):
        return self._error

    def raise_init_events(self):
        self.raise_event("data_loaded", data=self.data, error=self.error)
        if self.error is not None:
            self.raise_event("data_error", error=self.error)
        self.raise_event("query_changed", query=self.query)
        self.raise_event("hash_changed", hash=self.hash)

    def refetch(self):
        self.invalidate(exact=True)
        if self._current is not self:
            return
        return self._load_data()

    def get_url(self, full=False):
        return self.location.get_url(full)

    def _load_data(self):
        from ._non_blocking import call_async

        data_promise = call_async(load_data, self, force=True)
        self.raise_event("data_loading")
        return data_promise

    @property
    def _loader_args(self):
        return {
            "location": self.location,
            "path": self.path,
            "query": self.query,
            "params": self.params,
            "deps": self.deps,
            "nav_context": self.nav_context,
            "form_properties": self.form_properties,
        }
