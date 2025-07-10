# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

import anvil

from ._router import NavigationBlocker, navigation_emitter

__version__ = "0.4.0"

dismissible_alerts = []


def _on_navigate(**kws):
    global dismissible_alerts
    for alert in dismissible_alerts:
        alert.content.raise_event("x-close-alert")


navigation_emitter.add_event_handler("navigate", _on_navigate)


class DismissibleAlert:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        dismissible_alerts.append(self)

    def __exit__(self, *args):
        global dismissible_alerts
        dismissible_alerts = [x for x in dismissible_alerts if x is not self]


def wrap_alert(alert_method, dismissible=True):
    def alert(content, *args, dismissible=dismissible, **kwargs):
        if isinstance(content, str):
            content = anvil.Label(text=content)

        if dismissible:
            with DismissibleAlert(content):
                return alert_method(content, *args, dismissible=dismissible, **kwargs)
        else:
            with NavigationBlocker():
                return alert_method(content, *args, dismissible=dismissible, **kwargs)

    return alert


try:
    _anvil_alert = anvil.alert
    _anvil_confirm = anvil.confirm
except AttributeError:

    def _anvil_alert(*args, **kws):
        pass

    def _anvil_confirm(*args, **kws):
        pass


alert = wrap_alert(_anvil_alert)
confirm = wrap_alert(_anvil_confirm, dismissible=False)
