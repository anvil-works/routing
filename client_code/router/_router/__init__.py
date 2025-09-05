# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff:noqa: F401
import anvil

__version__ = "0.4.1"

if anvil.is_server_side():
    from .server import NavigationBlocker, UnloadBlocker, launch, navigation_emitter

else:
    from .client import NavigationBlocker, UnloadBlocker, launch, navigation_emitter
