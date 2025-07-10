# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from time import sleep

from ._non_blocking import Deferred
from ._utils import document, setTimeout

__version__ = "0.4.0"

_transition = None
_can_transition = hasattr(document, "startViewTransition")
_use_transition = True


def use_transitions(can_transition=True):
    global _use_transition
    _use_transition = can_transition


class ViewTransition:
    def __init__(self):
        self.deferred = Deferred()
        self.transition = None

    def resolve(self):
        global _transition
        if _transition is self.transition:
            _transition = None
        self.deferred.resolve(None)

    def __enter__(self):
        global _transition
        if _transition is None and _can_transition and _use_transition:
            self.transition = document.startViewTransition(
                lambda: self.deferred.promise
            )
            _transition = self.transition
            sleep(0)
            setTimeout(self.resolve, 100)
        return self

    def __exit__(self, *exc_args):
        self.resolve()
