# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

import anvil

from ._utils import document

__version__ = "0.3.4"


def get_or_create_tag(type):
    tag = document.querySelector(type)
    if tag is None:
        tag = document.createElement(type)
        tag.textContent = ""
        document.head.appendChild(tag)
    return tag


def get_or_create_meta_tag(name):
    tag = document.querySelector(f'meta[name="{name}"]')
    if tag is None:
        tag = document.createElement("meta")
        tag.setAttribute("name", name)
        tag.setAttribute("content", "")
        document.head.appendChild(tag)
    return tag


if anvil.is_server_side():
    title_tag = meta_title = meta_title_og = meta_description = meta_description_og = (
        None
    )
    default_title = ""
    default_description = ""

else:
    title_tag = get_or_create_tag("title")
    meta_title = get_or_create_meta_tag("title")
    meta_title_og = get_or_create_meta_tag("og:title")
    meta_description = get_or_create_meta_tag("description")
    meta_description_og = get_or_create_meta_tag("og:description")

    default_title = title_tag.textContent or meta_title.content
    default_description = meta_description.content


def get_default_meta():
    rv = {}
    if default_title:
        rv["title"] = default_title
    if default_description:
        rv["description"] = default_description
    return rv


def update_meta_tags(meta):
    title = meta.get("title") or default_title
    description = meta.get("description") or default_description
    title_tag.textContent = title
    meta_title.content = title
    meta_title_og.content = title
    document.title = title

    meta_description.content = description
    meta_description_og.content = description
