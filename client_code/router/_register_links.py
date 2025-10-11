# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.history import Location
from anvil.js import get_dom_node

from ._context import RoutingContext
from ._LinkCommon import check_if_location_is_active
from ._logger import logger
from ._matcher import parse_query
from ._navigate import navigate_with_location
from ._route import Route
from ._router import navigation_emitter

__version__ = "0.4.2"


def register_links(
    *dom_nodes,
    selector="a[href^='/']",
    active_class="active",
    active_callback=None,
    exact_path=False,
    exact_query=False,
    exact_hash=False,
    component=None,
):
    """
    Register navigation links for client-side routing with active state tracking

    Automatically detects if dom_nodes are links or containers:
    - If element is an <a> tag → register it directly as a link
    - Otherwise → search within it using selector

    Args:
        *dom_nodes: DOM elements (links or containers)
        selector: CSS selector for finding links in containers (default: internal links)
        active_class: CSS class to add/remove when link matches current route
        active_callback: Custom callback(element, is_active) for styling (overrides active_class)
        exact_path: If True, path must match exactly (default: False)
        exact_query: If True, query must match exactly (default: False)
        exact_hash: If True, hash must match exactly (default: False)
        component: Anvil component - auto setup on show, cleanup on hide (default: None)

    Returns:
        Cleanup function to unregister links and remove event listeners
        (or None if component is used)

    Examples:
        # Auto setup/cleanup tied to component lifecycle
        router.register_links(self.dom_nodes["header"], component=self)

        # Manual cleanup
        cleanup = router.register_links(self.dom_nodes["header"])
        # Later: cleanup()

        # With active class
        cleanup = router.register_links(
            self.dom_nodes["nav"],
            active_class="current"
        )

        # With custom callback
        def style_link(element, is_active):
            element.style.fontWeight = "bold" if is_active else "normal"

        cleanup = router.register_links(
            self.dom_nodes["nav"],
            active_callback=style_link
        )

        # Exact path matching
        cleanup = router.register_links(
            self.dom_nodes["breadcrumbs"],
            exact_path=True
        )
    """
    # Collect all links to register
    registered_links = []

    for node in dom_nodes:
        dom_node = get_dom_node(node)

        if dom_node.tagName.lower() == "a":
            registered_links.append(dom_node)
        else:
            links = dom_node.querySelectorAll(selector)
            for link in links:
                registered_links.append(link)

    # Register click handlers on all links
    for link in registered_links:
        _make_nav_link(link)

    # Create navigation handler that updates active state
    def on_navigate(routing_context=None, **nav_args):
        routing_context = routing_context or RoutingContext._current
        if routing_context is None:
            return

        for link in registered_links:
            _update_active_state(
                link,
                routing_context,
                active_class,
                active_callback,
                exact_path,
                exact_query,
                exact_hash,
            )

    # Subscribe to navigation events
    navigation_emitter.add_event_handler("navigate", on_navigate)

    # Trigger initial active state update
    on_navigate()

    # Return cleanup function
    def cleanup():
        navigation_emitter.remove_event_handler("navigate", on_navigate)
        # Optionally clear active state on cleanup
        if active_callback:
            for link in registered_links:
                active_callback(link, False)
        elif active_class:
            for link in registered_links:
                link.classList.remove(active_class)

    # If component is provided, tie to component's page lifecycle events
    if component is not None:

        def on_page_added(**event_args):
            # Re-register on each page added (in case links changed)
            on_navigate()

        def on_page_removed(**event_args):
            cleanup()

        component.add_event_handler("x-anvil-page-added", on_page_added)
        component.add_event_handler("x-anvil-page-removed", on_page_removed)
        return None  # Don't return cleanup function when lifecycle is managed

    return cleanup


def _handle_link_click(event):
    """Internal: Handle click on a registered navigation link"""
    if event.ctrlKey or event.metaKey or event.shiftKey:
        logger.debug("Link clicked with modifier keys - letting browser handle")
        return

    element = event.currentTarget
    href = element.getAttribute("href")

    if not href:
        return

    try:
        location = Location.from_url(href)
    except Exception as e:
        logger.debug(f"Failed to parse href '{href}': {e}")
        return

    event.preventDefault()
    logger.debug(f"Registered link clicked, navigating to {location}")
    navigate_with_location(location)


def _update_active_state(
    element,
    routing_context,
    active_class,
    active_callback,
    exact_path,
    exact_query,
    exact_hash,
):
    """Internal: Update active state for a registered link (uses NavLink logic)"""
    href = element.getAttribute("href")
    if not href:
        return

    try:
        location = Location.from_url(href)
    except Exception:
        return

    # Parse query from location if needed for exact_query check
    query = {}
    if exact_query and location.search_params:
        # Use a dummy route to parse query params
        dummy_route = Route()
        query = parse_query(dummy_route, location.search_params)

    # Use shared utility function
    active = check_if_location_is_active(
        location,
        query,
        routing_context,
        exact_path=exact_path,
        exact_query=exact_query,
        exact_hash=exact_hash,
    )

    # Apply active state
    if active_callback:
        active_callback(element, active)
    elif active_class:
        if active:
            element.classList.add(active_class)
        else:
            element.classList.remove(active_class)


def _make_nav_link(element):
    """Internal: Make a single element a navigation link"""
    href = element.getAttribute("href")

    if not href:
        return

    element.removeEventListener("click", _handle_link_click)
    element.addEventListener("click", _handle_link_click)
    logger.debug(f"Registered navigation link: {href}")
