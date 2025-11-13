# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

import anvil.js
from anvil.history import Location

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
    component=None,
):
    """
    Register navigation links for client-side routing with active state tracking

    Automatically detects if dom_nodes are links or containers:
    - If element is an <a> tag → register it only if it matches the selector
    - Otherwise → search within it using selector

    Args:
        *dom_nodes: DOM elements (links or containers)
        selector: CSS selector for finding links in containers (default: internal links)
        active_class: CSS class to add/remove when link matches current route
        active_callback: Custom callback(element, is_active) for styling (overrides active_class)
        component: Anvil component - auto setup on show, cleanup on hide (default: None)

    Returns:
        Cleanup function to unregister links and remove event listeners
        (or None if component is used)

    Exact Matching:
        Each link can specify exact matching behavior using data attributes:
        - data-exact-path: Path must match exactly (presence of attribute enables)
        - data-exact-query: Query parameters must match exactly (presence of attribute enables)
        - data-exact-hash: Hash must match exactly (presence of attribute enables)

        These attributes are read from each link element individually, allowing
        different links to have different exact matching behavior.

    Skip Active State:
        Use data-no-active attribute to skip active state tracking for a link:
        - data-no-active: Link will navigate but won't receive active state updates
        - Useful for links like home page ("/") that you want to navigate but not highlight

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

        # Exact path matching via data attribute in HTML:
        # <a href="/articles" data-exact-path>Articles</a>
        cleanup = router.register_links(self.dom_nodes["breadcrumbs"])
    """
    registered_links = []
    registered = {"done": False}  # nonlocal issue in skulpt

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
            )

    def initial_walk_links():
        if registered["done"]:
            return
        registered["done"] = True

        for node in dom_nodes:
            dom_node = anvil.js.get_dom_node(node)

            if dom_node.tagName.lower() == "a":
                # Check if the link itself matches the selector
                # Only register it if it matches (consistent with container behavior)
                if dom_node.matches(selector):
                    registered_links.append(dom_node)
            else:
                # Search for links within the container that match the selector
                links = dom_node.querySelectorAll(selector)
                for link in links:
                    registered_links.append(link)

        # Register click handlers on all links
        for link in registered_links:
            _make_nav_link(link)

    def setup(**event_args):
        initial_walk_links()
        # Subscribe to navigation events
        navigation_emitter.add_event_handler("navigate", on_navigate)
        # Update active state for initial route
        on_navigate()

    # Return cleanup function
    def cleanup(**event_args):
        navigation_emitter.remove_event_handler("navigate", on_navigate)
        # Optionally clear active state on cleanup
        if active_callback:
            for link in registered_links:
                active_callback(link, False)
        elif active_class:
            for link in registered_links:
                link.classList.remove(active_class)

    if component is None:
        # consumer is responsible for cleanup
        setup()
        return cleanup

    # If component is provided, tie to component's page lifecycle events
    component.add_event_handler("x-anvil-page-added", setup)
    component.add_event_handler("x-anvil-page-removed", cleanup)
    # Don't return cleanup function when lifecycle is managed
    return None


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
):
    """Internal: Update active state for a registered link (uses NavLink logic)

    Reads exact matching flags from data attributes on the element:
    - data-exact-path: presence enables exact path matching
    - data-exact-query: presence enables exact query matching
    - data-exact-hash: presence enables exact hash matching
    - data-no-active: presence skips active state tracking entirely
    """
    href = element.getAttribute("href")
    if not href:
        return

    # Check if link should skip active state tracking
    dataset = element.dataset
    if dataset.get("noActive") is not None:
        return

    try:
        location = Location.from_url(href)
    except Exception:
        return

    # Read exact matching flags from dataset (presence-based)
    # dataset converts data-exact-path to exactPath, etc.
    # dataset.get() returns None if attribute doesn't exist
    exact_path = dataset.get("exactPath") is not None
    exact_query = dataset.get("exactQuery") is not None
    exact_hash = dataset.get("exactHash") is not None

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
