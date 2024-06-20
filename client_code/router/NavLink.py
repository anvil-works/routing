import anvil
from anvil.js import get_dom_node
from ._navigate import navigate
from anvil.history import history


class DefaultLink(anvil.Link):
    def __init__(self, href=None, **properties):
        super().__init__(url=href, **properties)

    @property
    def href(self):
        return self.url

    @href.setter
    def href(self, value):
        self.url = value


class NavLink(anvil.Container):
    _anvil_properties_ = [
        {"name": "href", "type": "string"},
        {"name": "text", "type": "string"},
    ]
    _anvil_events_ = [{"name": "click", "defaultEvent": True}]

    def __init__(self, **properties):
        self._props = properties
        self._link = DefaultLink(**properties)
        self.href = self.href
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)

    def get_components(self):
        return self._link.get_components()

    def add_component(self, component, **properties):
        self._link.add_component(component, **properties)

    def clear(self):
        self._link.clear()

    @property
    def href(self):
        return self._props.get("href")

    @href.setter
    def href(self, value):
        self._props["href"] = value
        self._link.href = history.createHref(value)

    @property
    def text(self):
        return self._props.get("href")

    @text.setter
    def text(self, value):
        self._props["text"] = value
        self._link.text = value

    def _on_click(self, e):
        if e.ctrlKey or e.metaKey or e.shiftKey:
            return
        e.preventDefault()
        e.stopImmediatePropagation()

        href = self.href
        history.push(href)

    def _setup(self, **event_args):
        print("SETUP")
        self._el = get_dom_node(self._link)
        self._el.addEventListener("click", self._on_click, True)

    def _cleanup(self, **event_args):
        print("CLEANUP")
        el = self._el
        if el is None:
            return
        self._el = None
        el.removeEventListener("click", self._on_click, True)

    def _anvil_setup_dom_(self):
        return self._link._anvil_setup_dom_()

    @property
    def _anvil_dom_element_(self):
        return self._link._anvil_dom_element_

    def _anvil_get_container_design_info_(self, child):
        return self._link._anvil_get_container_design_info_(child)
    
    def _anvil_enable_drop_mode_(self, *args, **kwargs):
        return self._link._anvil_enable_drop_mode_(*args, **kwargs)
    
    def _anvil_disable_drop_mode_(self):
        return self._link._anvil_disable_drop_mode_()