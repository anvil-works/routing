# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT
from ._BaseLinks import setup_base_anchor
from ._LinkCommon import LinkMixinCommon, filter_props, nav_props

__version__ = "0.4.0"

BaseAnchor = setup_base_anchor()


class Anchor(BaseAnchor, LinkMixinCommon):
    _anvil_properties_ = [
        *nav_props.values(),
        *filter_props(BaseAnchor._anvil_properties_),
    ]

    def __init__(
        self,
        path=None,
        query=None,
        params=None,
        hash=None,
        nav_context=None,
        form_properties=None,
        **properties,
    ):
        LinkMixinCommon.__init__(
            self,
            path=path,
            query=query,
            params=params,
            hash=hash,
            nav_context=nav_context,
            form_properties=form_properties,
            **properties,
        )
        BaseAnchor.__init__(self, **properties)
