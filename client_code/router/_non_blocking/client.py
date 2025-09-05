# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.js.window import Function

# We need to make sure the .then method doesn't return a Promise to avoid suspensions
__version__ = "0.4.2"

PromiseLike = Function("""
class PromiseLike extends Promise {
    then(...args) {
        Promise.prototype.then.apply(this, args);
    }
}

return PromiseLike;
""")()
