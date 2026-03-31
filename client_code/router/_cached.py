# Copyright (c) 2024-2026 Anvil
# SPDX-License-Identifier: MIT

__version__ = "0.6.1"

CACHED_FORMS = {}
CACHED_DATA = {}
IN_FLIGHT_DATA = {}


def clear_cache():
    CACHED_FORMS.clear()
    CACHED_DATA.clear()
    IN_FLIGHT_DATA.clear()
