# Copyright (c) 2024 Anvil
# SPDX-License-Identifier: MIT

# ruff:noqa: F401
import anvil

__version__ = "0.0.2"

if anvil.is_server_side():
    from .server import NavigationBlocker, UnloadBlocker, launch, navigation_emitter

else:
    from .client import NavigationBlocker, UnloadBlocker, launch, navigation_emitter
