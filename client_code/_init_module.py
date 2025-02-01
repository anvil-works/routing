# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# setup default navlink
import anvil
from anvil.designer import get_design_component
from anvil.js import get_dom_node

__version__ = "0.3.4"

BaseAnvilLink = get_design_component(anvil.Link)


class BaseAnchor(BaseAnvilLink):
    def __init__(self, **properties):
        super().__init__(**properties)
        self._d = get_dom_node(self)
        self._d.addEventListener("click", self._handle_click, True)

    def _handle_click(self, e):
        e.stopImmediatePropagation()
        self.raise_event("click", event=e)


class BaseNavLink(BaseAnchor):
    def __init__(self, active=False, role=None, **properties):
        super().__init__(**properties)
        self.active = active

    @property
    def active(self):
        return self.role == "selected"

    @active.setter
    def active(self, value):
        self.role = "selected" if value else None


try:
    from m3.components import Link as BaseAnchor
    from m3.components import NavigationLink as BaseNavLink
except ImportError:
    pass


try:
    from Mantine.Anchor import Anchor as BaseAnchor
    from Mantine.NavLink import NavLink as BaseNavLink

except ImportError:
    pass


anvil.pluggable_ui.provide_defaults(
    "routing", {"routing.NavLink": BaseNavLink, "routing.Anchor": BaseAnchor}
)
