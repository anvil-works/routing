# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from anvil.history import Location
from anvil.js import get_dom_node

from ._logger import logger
from ._navigate import navigate_with_location

__version__ = "0.4.2"


def register_links(*dom_nodes, selector="a[href^='/']"):
    """
    Register navigation links for client-side routing

    Automatically detects if dom_nodes are links or containers:
    - If element is an <a> tag → register it directly as a link
    - Otherwise → search within it using selector

    Args:
        *dom_nodes: DOM elements (links or containers)
        selector: CSS selector for finding links in containers (default: internal links)

    Examples:
        # Register container - finds all internal links
        router.register_links(self.dom_nodes["header"])

        # Register multiple containers
        router.register_links(
            self.dom_nodes["header"],
            self.dom_nodes["footer"]
        )

        # Register specific links directly (auto-detected as <a> tags)
        router.register_links(
            self.dom_nodes["pricing-link"],
            self.dom_nodes["faq-link"]
        )

        # Mix and match!
        router.register_links(
            self.dom_nodes["header"],        # container
            self.dom_nodes["special-link"]   # direct link
        )

        # Custom selector for containers
        router.register_links(
            self.dom_nodes["nav"],
            selector="a.internal-link, button[data-route]"
        )
    """
    for node in dom_nodes:
        # Get the actual DOM node if it's an Anvil component
        dom_node = get_dom_node(node)

        # Magic: detect if it's a link or container
        if dom_node.tagName.lower() == "a":
            # It's a link - register directly
            _make_nav_link(dom_node)
        else:
            # It's a container - search for links
            links = dom_node.querySelectorAll(selector)
            for link in links:
                _make_nav_link(link)


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


def _make_nav_link(element):
    """Internal: Make a single element a navigation link"""
    href = element.getAttribute("href")

    if not href:
        return

    element.removeEventListener("click", _handle_link_click)
    element.addEventListener("click", _handle_link_click)
    logger.debug(f"Registered navigation link: {href}")
