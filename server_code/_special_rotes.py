# Copyright (c) 2025 Anvil
# SPDX-License-Identifier: MIT

# adapted form https://anvil.works/forum/t/automatic-sitemap-txt-with-routing/24249

import anvil
import anvil.server

from . import router

__version__ = "0.3.5"


def create_text_file(lines, name: str):
    """Create a text file from a list of strings"""
    content = "\n".join(lines).encode()
    return anvil.BlobMedia(content_type="text/plain", content=content, name=name)


def site_map_iter():
    origin = anvil.server.get_app_origin()
    # I don't really know if this bare url is necessary, but what's the harm?
    yield origin

    yield from (
        f"{origin}{route.path}"
        for route in router.sorted_routes
        if not route.private and route.path
    )


def get_sitemap():
    """Create and serve a simple sitemap.txt file base on the routes defined in client/routes.py
    More info on sitemaps:
    https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
    """
    # serve our up-to-date sitemap
    file = create_text_file(site_map_iter(), "sitemap.txt")
    return anvil.server.HttpResponse(200, file)


def get_robots():
    """Create and serve a robots.txt file
    More info:
    https://developers.google.com/search/docs/crawling-indexing/robots/intro
    """
    origin = anvil.server.get_app_origin()
    lines = [
        "# robots.txt",  # Just a dumb header for us dumb humans to read.
        f"Sitemap: {origin}/sitemap.txt",  # Provide the path to the sitemap for crawling
    ]

    # Create our txt file and return it in a http response
    file = create_text_file(lines, "robots.txt")
    return anvil.server.HttpResponse(200, file)


if router.config.get("SITEMAP"):
    router.logger.debug("Sitemap enabled")
    anvil.server.route("/sitemap.txt")(get_sitemap)
if router.config.get("ROBOTS"):
    router.logger.debug("Robots enabled")
    anvil.server.route("/robots.txt")(get_robots)
