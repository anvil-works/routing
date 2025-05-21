# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.history import history

from ._navigate import get_nav_location

__version__ = "0.3.6"


def get_url(
    context_or_path=None, *, path=None, params=None, query=None, hash=None, full=False
):
    if (
        context_or_path is None
        and path is None
        and params is None
        and query is None
        and hash is None
    ):
        return history.location.get_url(full)

    location = get_nav_location(
        context_or_path, path=path, params=params, query=query, hash=hash
    )
    return location.get_url(full)
