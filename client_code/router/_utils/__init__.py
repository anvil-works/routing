# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff:noqa: F401
import json
from datetime import date, datetime

import anvil

from .._constants import TIMEOUT

__version__ = "0.3.6"

if anvil.is_server_side():
    from .server import (
        Promise,
        await_promise,
        document,
        encode_query_params,
        report_exceptions,
        setTimeout,
        timeout,
        url_decode,
        url_encode,
    )

    # TODO: remove this at some point
    anvil.server.call_s = anvil.server.call

    class LoadingIndicator:
        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    anvil.server.no_loading_indicator = LoadingIndicator()

else:
    from .client import (
        Promise,
        await_promise,
        document,
        encode_query_params,
        report_exceptions,
        setTimeout,
        timeout,
        url_decode,
        url_encode,
    )


def trim_path(path):
    start = 0
    end = len(path)
    while start < end and path[start] == "/":
        start += 1
    while end > start and path[end - 1] == "/":
        end -= 1
    return path[start:end]


def valid_absolute_path(path):
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    trimmed_path = trim_path(path)
    if trimmed_path.startswith("."):
        raise ValueError("Route path cannot be relative")
    return "/" + trimmed_path


def ensure_dict(value, name):
    if value is None:
        return {}
    elif not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value


def make_key(path, deps):
    deps = ensure_dict(deps, "deps")
    try:
        json_deps = dumps(deps)
    except Exception:
        raise TypeError(
            f"cache_deps must return a json serializable dict, got {deps!r}"
        )

    return f"{path}:{json_deps}"


def decode_key(key):
    parts = key.split(":", 1)
    path, deps = parts
    return path, json.loads(deps)


PREFIX = "$$_"
SERIALIZERS = {
    datetime: (datetime.isoformat, datetime.fromisoformat),
    date: (date.isoformat, date.fromisoformat),
}
KEY_TO_SERIALIZER_CLS = {f"{PREFIX}{cls.__name__}": cls for cls in SERIALIZERS}


def default_hook(obj):
    for cls, serializer_args in SERIALIZERS.items():
        if isinstance(obj, cls):
            key = f"{PREFIX}{cls.__name__}"
            serializer = serializer_args[0]
            return {key: serializer(obj)}

    raise TypeError(f"TypeError: Object of type {type(obj)} is not JSON serializable")


def object_hook(obj):
    if len(obj) != 1:
        return obj

    key = next(iter(obj))
    deserializer_cls = KEY_TO_SERIALIZER_CLS.get(key)
    if deserializer_cls is None:
        return obj

    deserializer = SERIALIZERS[deserializer_cls][1]
    return deserializer(obj[key])


def dumps(obj):
    return json.dumps(obj, sort_keys=True, default=dumps)


def loads(s):
    return json.loads(s, object_hook=object_hook)


class EventEmitter:
    _events = []

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance._subscribers = {}
        return instance

    def _validate_event(self, event_name):
        if not isinstance(event_name, str):
            raise TypeError("event_name must be a string")
        if event_name not in self._events:
            raise ValueError(
                f"event_name {event_name} is not valid, valid events are {self._events}"
            )

    def add_event_handler(self, event_name, handler):
        self._validate_event(event_name)
        self._subscribers.setdefault(event_name, set()).add(handler)

    def remove_event_handler(self, event_name, handler):
        self._validate_event(event_name)
        if event_name in self._subscribers:
            self._subscribers[event_name].discard(handler)

    def raise_event(self, event_name, **kwargs):
        self._validate_event(event_name)
        kwargs["event_name"] = event_name
        kwargs["sender"] = self
        fns = self._subscribers.get(event_name, [])
        for fn in fns:
            fn(**kwargs)
