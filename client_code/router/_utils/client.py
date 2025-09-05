# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

# ruff: noqa: F401
from anvil.designer import in_designer
from anvil.js import (
    await_promise,
    report_exceptions,
)
from anvil.js.window import Promise, URLSearchParams, document, setTimeout

from .._constants import TIMEOUT

__version__ = "0.4.2"

if in_designer:
    from anvil.js.window import decodeURIComponent as url_decode
    from anvil.js.window import encodeURIComponent as url_encode
else:
    from anvil.http import (
        url_decode,
        url_encode,
    )


if in_designer:
    pass
else:
    pass


def timeout(s=0):
    def wait_async(resolve, reject):
        def timeout():
            resolve(TIMEOUT)

        setTimeout(timeout, s * 1000)

    return Promise(wait_async)


def encode_query_params(query):
    if not query:
        return ""

    return "?" + URLSearchParams(query).toString()
