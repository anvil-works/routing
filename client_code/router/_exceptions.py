# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.server import AnvilWrappedError, _register_exception_type

from ._utils import ensure_dict

__version__ = "0.4.1"


class Redirect(AnvilWrappedError):
    def __init__(
        self,
        path=None,
        *,
        query=None,
        params=None,
        hash=None,
        nav_context=None,
        form_properties=None,
    ):
        self.path = path
        self.query = query
        self.params = params
        self.hash = hash
        self.nav_context = ensure_dict(nav_context, "nav_context")
        self.form_properties = ensure_dict(form_properties, "form_properties")


class NotFound(AnvilWrappedError):
    pass


class InvalidPathParams(Exception):
    pass


_register_exception_type(f"{Redirect.__module__}.Redirect", Redirect)
_register_exception_type(f"{NotFound.__module__}.NotFound", NotFound)
