# Copyright (c) 2024 Anvil
# SPDX-License-Identifier: MIT

from anvil import Component
from anvil.designer import in_designer, register_interaction, start_editing_form
from anvil.history import Location
from anvil.js import get_dom_node

from ._exceptions import InvalidPathParams
from ._logger import logger
from ._matcher import get_match
from ._navigate import nav_args_to_location, navigate_with_location
from ._router import navigation_emitter
from ._utils import ensure_dict

__version__ = "0.2.3"


def _temp_hack_to_get_form(self):
    if not in_designer:
        return None

    from ._import_utils import import_module

    try:
        import_module("routes")
    except Exception:
        pass

    if self._location is None:
        return None
    elif self._location.path is None:
        return None
    match = get_match(location=self._location)

    if match is not None:
        return match.route.form


nav_props = {
    "path": {
        "name": "path",
        "type": "string",
        "group": "navigation",
        "priority": 100,
        "important": True,
    },
    "query": {"name": "query", "type": "object", "group": "navigation"},
    "params": {"name": "params", "type": "object", "group": "navigation"},
    "hash": {"name": "hash", "type": "string", "group": "navigation"},
    "nav_context": {"name": "nav_context", "type": "object", "group": "navigation"},
    "form_properties": {
        "name": "form_properties",
        "type": "object",
        "group": "navigation",
    },
}

active_props = {
    "active": {"name": "active", "type": "boolean", "group": "active"},
    "exact_path": {"name": "exact_path", "type": "boolean", "group": "active"},
    "exact_query": {"name": "exact_query", "type": "boolean", "group": "active"},
    "exact_hash": {"name": "exact_hash", "type": "boolean", "group": "active"},
}

all_props = {**nav_props, **active_props}

ignore_props = ["href", "url", "selected", *all_props]


def prop_filter(prop):
    return prop["name"] not in ignore_props and prop["type"] != "form"


def filter_props(prop_list):
    return filter(prop_filter, prop_list)


class LinkMixinCommon(Component):
    def __init__(self, **properties):
        self.__props = properties
        self._location = None
        self._form = None
        self._invalid = None
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)
        self.add_event_handler("click", self._on_click)

    def _do_click(self, e):
        if not in_designer:
            if self._location is not None:
                logger.debug(f"NavLink clicked, navigating to {self._location}")
                navigate_with_location(
                    self._location,
                    nav_context=self.nav_context,
                    form_properties=self.form_properties,
                )
            elif self._invalid is not None:
                raise self._invalid
            else:
                logger.debug("NavLink clicked, but with invalid path, query or hash")
        elif self._form is not None:
            start_editing_form(self, self._form)

    def _on_click(self, **event_args):
        event = event_args.get("event")
        if event is None:
            raise RuntimeError("Link provider did not pass the event")
        if event.ctrlKey or event.metaKey or event.shiftKey:
            logger.debug(
                "NavLink clicked, but with modifier keys - letting browser handle"
            )
            return
        event.preventDefault()
        self._do_click(event)

    def _setup(self, **event_args):
        # we have to do this when we're on the page in case links are relative
        self._set_href()

        if in_designer and self._form is not None:
            register_interaction(self, get_dom_node(self), "dblclick", self._do_click)

        if not in_designer:
            navigation_emitter.add_event_handler("navigate", self._set_href)

    def _cleanup(self, **event_args):
        navigation_emitter.remove_event_handler("navigate", self._set_href)

    @property
    def nav_context(self):
        return self.__props.get("nav_context")

    @nav_context.setter
    def nav_context(self, value):
        value = ensure_dict(value, "nav_context")
        self.__props["nav_context"] = value

    @property
    def form_properties(self):
        return self.__props.get("form_properties")

    @form_properties.setter
    def form_properties(self, value):
        value = ensure_dict(value, "form_properties")
        self.__props["form_properties"] = value

    @property
    def path(self):
        return self.__props.get("path")

    @path.setter
    def path(self, value):
        self.__props["path"] = value
        self._set_href()

    @property
    def query(self):
        return self.__props.get("query")

    @query.setter
    def query(self, value):
        self.__props["query"] = value
        self._set_href()

    @property
    def params(self):
        return self.__props.get("params")

    @params.setter
    def params(self, value):
        self.__props["params"] = value
        self._set_href()

    @property
    def hash(self):
        return self.__props.get("hash")

    @hash.setter
    def hash(self, value):
        self.__props["hash"] = value
        self._set_href()

    def _set_href(self, **nav_args):
        prev_location = self._location

        path = self.path or None
        params = self.params
        query = self.query
        hash = self.hash

        # fast path
        if (
            path is not None
            and not callable(query)
            and not in_designer
            and prev_location is not None
        ):
            return

        self._location = None
        self._form = None

        try:
            location = nav_args_to_location(
                path=path,
                params=params,
                query=query,
                hash=hash,
            )
        except InvalidPathParams as e:
            if not in_designer:
                self._invalid = e
                self.href = ""
                return
            else:
                location = Location(path=path, hash=hash)
        else:
            self._invalid = None

        self._location = location

        if prev_location == location:
            return

        if in_designer:
            self._form = _temp_hack_to_get_form(self)
        elif location.path is not None:
            self.href = location.get_url(True)
