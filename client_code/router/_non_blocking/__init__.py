# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff: noqa: F401
import anvil

from .._utils import setTimeout

__version__ = "0.5.0"

if anvil.is_server_side():
    from .server import PromiseLike
else:
    from .client import PromiseLike


class Deferred:
    def __init__(self):
        def callback(resolve, reject):
            self.resolve = resolve
            self.reject = reject

        self.promise = PromiseLike(callback)


# We wrap the result in a obtuse python object
# to avoid converting python objects to javascript
class Result:
    def __init__(self, ok=None, error=None):
        self.ok = ok
        self.error = error

    def __iter__(self):
        return [self.ok, self.error].__iter__()


def call_async(fn, *args, **kws):
    _deferred = Deferred()

    def call():
        try:
            result = fn(*args, **kws)
            _deferred.resolve(Result(result))
        except Exception as e:
            _deferred.resolve(Result(error=e))

    setTimeout(call, 0)

    return _deferred.promise
