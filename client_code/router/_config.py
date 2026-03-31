# Copyright (c) 2024-2026 Anvil
# SPDX-License-Identifier: MIT

import anvil

__version__ = "0.6.1"

_DEFAULTS = {
    "debug_logging": False,
    "raise_on_data_error": True,
    "routes_module": "routes",
    "robots": False,
    "sitemap": False,
}


def get_routing_config():
    try:
        config = anvil.app.get_client_config("routing")
    except AttributeError:
        config = {}
    if not isinstance(config, dict):
        return dict(_DEFAULTS)
    return {**_DEFAULTS, **config}


def get_routes_module():
    return get_routing_config().get("routes_module") or "routes"


def get_debug_logging():
    return bool(get_routing_config().get("debug_logging"))


def get_raise_on_data_error():
    return bool(get_routing_config().get("raise_on_data_error"))
