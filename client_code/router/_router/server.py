# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from .._utils import EventEmitter

__version__ = "0.4.1"


def launch():
    raise NotImplementedError("launch is not implemented on the server")


class _Blocker:
    def block(self):
        pass

    def unblock(self):
        pass


class NavigationBlocker(_Blocker):
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


class UnloadBlocker(_Blocker):
    pass


class _NavigationEmitter(EventEmitter):
    _events = ["navigate", "pending", "idle"]


navigation_emitter = _NavigationEmitter()
