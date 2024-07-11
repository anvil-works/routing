import anvil
from anvil import Component
from anvil.js import get_dom_node
from anvil.history import history, Location
from anvil.designer import (
    in_designer,
    get_design_component,
    start_editing_form,
    register_interaction,
)
from ._navigate import nav_args_to_location, navigate_with_location
from ._matcher import get_match
from ._exceptions import InvalidPathParams
from ._segments import Segment
from ._router import navigation_emitter
from ._logger import logger


_DefaultLink = get_design_component(anvil.Link)


class DefaultLink(_DefaultLink):
    def __init__(self, href=None, **properties):
        self._active = False
        super().__init__(url=href, **properties)
        self._d = get_dom_node(self)
        self._d.addEventListener("click", self._handle_click, True)

    def _handle_click(self, e):
        e.stopImmediatePropagation()
        self.raise_event("click", event=e)

    @property
    def href(self):
        return self.url

    @href.setter
    def href(self, value):
        self.url = value

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.role = "selected" if value else None


def _temp_hack_to_get_form(self):
    if not in_designer:
        return None

    try:
        from SimpleRoutingExample import routes
    except (ImportError, ModuleNotFoundError, AttributeError):
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
    "search_params": {"name": "search_params", "type": "object", "group": "navigation"},
    "search": {"name": "search", "type": "string", "group": "navigation"},
    "path_params": {"name": "path_params", "type": "object", "group": "navigation"},
    "hash": {"name": "hash", "type": "string", "group": "navigation"},
    "nav_args": {"name": "nav_args", "type": "object", "group": "navigation"},
}

active_props = {
    "exact_path": {"name": "exact_path", "type": "boolean", "group": "active"},
    "exact_search": {"name": "exact_search", "type": "boolean", "group": "active"},
    "exact_hash": {"name": "exact_hash", "type": "boolean", "group": "active"},
}

all_props = {**nav_props, **active_props}


class LinkMixinCommon(Component):
    def __init__(self, **properties):
        self._props = properties
        self._location = None
        self._form = None
        self._href = ""
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)
        self.add_event_handler("click", self._on_click)

    def _do_click(self, e):
        if not in_designer:
            if self._location is not None:
                logger.debug(f"NavLink clicked, navigating to {self._location}")
                navigate_with_location(self._location, nav_args=self.nav_args)
            else:
                logger.debug("NavLink clicked, but with invalid path, search or hash")
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
            register_interaction(self, self._el, "dblclick", self._do_click)

    def _cleanup(self, **event_args):
        pass

    @property
    def nav_args(self):
        return self._props.get("nav_args")

    @nav_args.setter
    def nav_args(self, value):
        self._props["nav_args"] = value

    @property
    def path(self):
        return self._props.get("path")

    @path.setter
    def path(self, value):
        self._props["path"] = value
        self._set_href()

    @property
    def search_params(self):
        return self._props.get("search_params")

    @search_params.setter
    def search_params(self, value):
        self._props["search_params"] = value
        self._set_href()

    @property
    def search(self):
        return self._props.get("search")

    @search.setter
    def search(self, value):
        self._props["search"] = value
        self._set_href()

    @property
    def path_params(self):
        return self._props.get("path_params")

    @path_params.setter
    def path_params(self, value):
        self._props["path_params"] = value
        self._set_href()

    @property
    def hash(self):
        return self._props.get("hash")

    @hash.setter
    def hash(self, value):
        self._props["hash"] = value
        self._set_href()

    @property
    def exact_path(self):
        return self._props.get("exact_path")

    @exact_path.setter
    def exact_path(self, value):
        self._props["exact_path"] = value

    @property
    def exact_search(self):
        return self._props.get("exact_search")

    @exact_search.setter
    def exact_search(self, value):
        self._props["exact_search"] = value

    @property
    def exact_hash(self):
        return self._props.get("exact_hash")

    @exact_hash.setter
    def exact_hash(self, value):
        self._props["exact_hash"] = value

    def _set_href(self):
        self._location = None
        self._form = None

        path = self.path
        search = self.search
        path_params = self.path_params
        search_params = self.search_params
        hash = self.hash
        if not path:
            # path must be explicitly set
            self._href = self.href = None
            return

        try:
            location = nav_args_to_location(
                path=path,
                path_params=path_params,
                search_params=search_params,
                hash=hash,
            )
        except InvalidPathParams as e:
            if not in_designer:
                raise e
            else:
                location = Location(path=path, search=search, hash=hash)
        if not location.search and search:
            # search was set by the search attribute rather than the search_params
            location = Location(path=location.path, search=search, hash=location.hash)

        self._location = location

        if in_designer:
            self._form = _temp_hack_to_get_form(self)
        elif location.path is not None:
            self.href = self._href = location.get_url(False)
