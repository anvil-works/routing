# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

import anvil
import anvil.server

from ._utils import document

__version__ = "0.4.1"

_CACHE = {}


class Node:
    selector = ""

    def __init__(self, name: str):
        self.node = self.get_or_create_node(name)
        self.default_content = self.get_content()

    def get_content(self):
        raise NotImplementedError

    def set_content(self, content):
        raise NotImplementedError

    def reset(self):
        self.set_content(self.default_content)

    @classmethod
    def get_or_create_node(cls, name):
        node = document.querySelector(cls.selector.format(name))
        if node is None:
            node = cls.create_node(name)
            document.head.appendChild(node)
        return node

    @staticmethod
    def create_node(name):
        raise NotImplementedError


class TagNode(Node):
    # <name>content</name>
    selector = "{}"

    def get_content(self):
        return self.node.textContent

    def set_content(self, content):
        self.node.textContent = content

    @staticmethod
    def create_node(name):
        node = document.createElement(name)
        node.textContent = ""
        return node


class MetaNode(TagNode):
    # <meta name="name" content="content">
    selector = 'meta[name="{}"]'

    def get_content(self):
        return self.node.getAttribute("content")

    def set_content(self, content):
        if isinstance(content, str) and content.startswith("asset:"):
            from anvil.js.window import URL

            content = "/_/theme/" + content[6:]
            content = URL(anvil.server.get_app_origin() + content).href

        self.node.setAttribute("content", content)

    @staticmethod
    def create_node(name):
        node = document.createElement("meta")
        node.setAttribute("name", name)
        node.setAttribute("content", "")
        return node


class MetaTagStore:
    def __new__(cls, name):
        if name in _CACHE:
            return _CACHE[name]

        self = super().__new__(cls)
        _CACHE[name] = self
        return self

    def __init__(self, name: str):
        self.nodes = self.get_nodes(name)

    @staticmethod
    def get_nodes(name: str):
        return [MetaNode(name)]


class TitleTagStore(MetaTagStore):
    @staticmethod
    def get_nodes(name: str):
        # Returns both a Node and MetaNode for special cases (e.g., title, description)
        return [TagNode(name), MetaNode(name)]


NAME_TO_STORE = {
    "title": TitleTagStore,
    "description": MetaTagStore,
    "og:title": MetaTagStore,
    "og:description": MetaTagStore,
    "og:image": MetaTagStore,
}

FALLBACK_STORE = {
    "og:title": "title",
    "og:description": "description",
}


def get_tag_store(name: str):
    # arbitrary names not yet in the cache will be treated as meta tags
    cls = NAME_TO_STORE.get(name, MetaTagStore)
    return cls(name)


def update_meta_tags(meta):
    meta = {**meta}  # copy since we might mutate it

    for key, fallback_key in FALLBACK_STORE.items():
        if key not in meta and fallback_key in meta:
            meta[key] = meta[fallback_key]

    for name, content in meta.items():
        tag = get_tag_store(name)
        for node in tag.nodes:
            node.set_content(content)

    # Reset any cached tags that are not present in the current meta dict
    for name, tag in _CACHE.items():
        if name in meta:
            continue
        for node in tag.nodes:
            node.reset()
