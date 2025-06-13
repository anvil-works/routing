# Copyright (c) 2025 Anvil
# SPDX-License-Identifier: MIT

__version__ = "0.4.0"


def before_load(func):
    """
    Decorator to register a method as a before_load hook for a Route.
    Hooks are called in the order they are defined on the class.
    Each hook receives a 'nav_context' keyword argument (the context dict accumulated so far),
    which can be read and updated for composable navigation logic.
    """
    func._is_before_load_hook = True
    return func
