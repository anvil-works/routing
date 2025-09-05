# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff: noqa: F401
import anvil
from anvil.designer import get_design_component

__version__ = "0.4.2"


class UrlMixin:
    def __init__(self, href=None, url=None, **properties):
        super().__init__(url=href, **properties)

    @property
    def href(self):
        return self.url

    @href.setter
    def href(self, value):
        self.url = value


class SelectedMixin:
    def __init__(self, active=False, selected=False, **properties):
        super().__init__(selected=active, **properties)

    @property
    def active(self):
        return self.selected

    @active.setter
    def active(self, value):
        self.selected = value


def setup_base_component(component):
    Base = anvil.pluggable_ui[component]
    Base = get_design_component(Base)
    if hasattr(Base, "url"):

        class Base(UrlMixin, Base):
            pass

    return Base


def setup_base_anchor():
    return setup_base_component("routing.Anchor")


def setup_base_navlink():
    Base = setup_base_component("routing.NavLink")

    if hasattr(Base, "selected"):

        class Base(SelectedMixin, Base):
            pass

    return Base
