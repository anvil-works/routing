# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.designer import in_designer

from ._BaseLinks import setup_base_navlink
from ._context import RoutingContext
from ._LinkCommon import LinkMixinCommon, active_props, filter_props, nav_props
from ._router import navigation_emitter
from ._segments import Segment
from ._utils import ensure_dict

__version__ = "0.4.2"

BaseNavLink = setup_base_navlink()


def _query_inclusively_equal(a, b):
    """check if all the keys in a are in b and have the same value"""
    for key in a:
        if key not in b:
            return False
        if a[key] != b[key]:
            return False
    return True


class NavLink(BaseNavLink, LinkMixinCommon):
    _anvil_properties_ = [
        *nav_props.values(),
        *active_props.values(),
        *filter_props(BaseNavLink._anvil_properties_),
    ]

    def __init__(
        self,
        path=None,
        query=None,
        params=None,
        hash=None,
        nav_context=None,
        form_properties=None,
        exact_path=False,
        exact_query=False,
        exact_hash=False,
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
            exact_path=exact_path,
            exact_query=exact_query,
            exact_hash=exact_hash,
        )
        BaseNavLink.__init__(self, **properties)

        if not in_designer:
            self.add_event_handler("x-anvil-page-added", self._rn_on_navigate)
            self.add_event_handler(
                "x-anvil-page-added",
                lambda **e: navigation_emitter.add_event_handler(
                    "navigate", self._rn_on_navigate
                ),
            )
            self.add_event_handler(
                "x-anvil-page-removed",
                lambda **e: navigation_emitter.remove_event_handler(
                    "navigate", self._rn_on_navigate
                ),
            )

    def _rn_on_navigate(self, routing_context: RoutingContext = None, **nav_args):
        routing_context = routing_context or RoutingContext._current
        if routing_context is None:
            return

        location = self._rn.location
        active = True

        query = self.query
        if callable(query):
            query = query(routing_context.query)

        query = ensure_dict(query, "query")

        if location is None:
            active = False
        elif self.exact_path and routing_context.path != location.path:
            active = False
        elif self.exact_query and not _query_inclusively_equal(
            query, routing_context.query
        ):
            active = False
        elif self.exact_hash and routing_context.hash != location.hash:
            active = False
        elif routing_context.path != location.path:
            # check if the current location is a parent of the new location
            curr_segments = Segment.from_path(routing_context.path)
            location_segments = Segment.from_path(location.path)
            if len(location_segments) > len(curr_segments):
                active = False
            else:
                for gbl, loc in zip(curr_segments, location_segments):
                    if gbl.value == loc.value or loc.is_param():
                        continue
                    active = False
                    break

        self.active = active

    @property
    def exact_path(self):
        return self._rn.props.get("exact_path")

    @exact_path.setter
    def exact_path(self, value):
        self._rn.props["exact_path"] = value

    @property
    def exact_query(self):
        return self._rn.props.get("exact_query")

    @exact_query.setter
    def exact_query(self, value):
        self._rn.props["exact_query"] = value

    @property
    def exact_hash(self):
        return self._rn.props.get("exact_hash")

    @exact_hash.setter
    def exact_hash(self, value):
        self._rn.props["exact_hash"] = value
