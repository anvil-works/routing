# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from time import sleep

from ._logger import logger
from ._non_blocking import Deferred
from ._utils import document, setTimeout

__version__ = "0.4.1"

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
        self.promise_callback = lambda: self.deferred.promise

    def resolve(self):
        global _transition
        if _transition is self.transition:
            _transition = None
        self.deferred.resolve(None)

    def __enter__(self):
        global _transition
        # Only attempt a view transition when supported, enabled, and visible
        visible = getattr(document, "visibilityState", "visible") == "visible"
        try:
            if _transition is None and _can_transition and _use_transition and visible:
                self.transition = document.startViewTransition(self.promise_callback)
                _transition = self.transition
                sleep(0)
                setTimeout(self.resolve, 100)

        except Exception as e:
            # startViewTransition can throw InvalidStateError if the document becomes hidden
            # between checks or other environment constraints occur; gracefully fall back.
            logger.debug(f"Failed to start view transition {e!r}")

        return self

    def __exit__(self, *exc_args):
        self.resolve()
