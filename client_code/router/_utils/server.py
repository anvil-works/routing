# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff: noqa: F401
from urllib.parse import urlencode

__version__ = "0.5.0"

try:
    from anvil.http import (
        url_decode,
        url_encode,
    )
except ImportError:
    from urllib.parse import quote as url_encode
    from urllib.parse import unquote as url_decode


try:
    from async_promises import Promise
except ImportError:

    class Promise:
        def __init__(self, fn):
            self.fn = fn
            self.STATUS = "PENDING"
            self.result = None
            self.error = None
            self.resolved = False
            self._subscribers = {}
            self.get()

        def get(self):
            if self.resolved:
                return self.result

            self.fn(self.resolve, self.reject)
            if self.error:
                raise self.error
            return self.result

        def resolve(self, result):
            self.result = result
            self.resolved = True
            self.STATUS = "FULFILLED"

        def reject(self, error):
            self.error = error
            self.resolved = True
            self.STATUS = "REJECTED"

        def _subscribe(self, event, fn):
            if event not in self._subscribers:
                self._subscribers[event] = []
            self._subscribers[event].append(fn)

        def _unsubscribe(self, event, fn):
            if event in self._subscribers:
                self._subscribers[event].remove(fn)

        def once(self, event):
            fns = self._subscribers.get(event, [])
            self._subscribers[event] = []
            for fn in fns:
                fn()

        @classmethod
        def race(cls, promises):
            raise NotImplementedError

        def then(self, fn=None, error_fn=None):
            def handler(resolve, reject):
                def on_status_change():
                    if self.STATUS == "FULFILLED":
                        if fn:
                            try:
                                # what if fn returns a promise?
                                resolve(fn(self.result))
                            except Exception as e:
                                reject(e)
                        else:
                            resolve(self.result)
                    elif self.STATUS == "REJECTED":
                        if error_fn:
                            try:
                                resolve(error_fn(self.error))
                            except Exception as e:
                                reject(e)
                        else:
                            reject(self.error)

                if self.STATUS == "PENDING":
                    self._subscribe("status_change", on_status_change)
                else:
                    on_status_change()

            return Promise(handler)

        def catch(self, error_fn):
            return self.then(None, error_fn)


def await_promise(promise):
    if not isinstance(promise, Promise):
        return promise
    return promise.get()


def report_exceptions(fn):
    return fn


def timeout(ms=0):
    return None


def setTimeout(fn, ms):
    fn()


def encode_query_params(query):
    if not query:
        return ""
    return "?" + urlencode(query)


document = object()
