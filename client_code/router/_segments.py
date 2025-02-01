# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

from ._utils import trim_path

__version__ = "0.3.4"


class Segment:
    PARAM = "PARAM"
    STATIC = "STATIC"

    def __init__(self, type, value):
        self.type = type
        self.value = value

    @classmethod
    def static(cls, value):
        return cls(cls.STATIC, value)

    @classmethod
    def param(cls, value):
        return cls(cls.PARAM, value)

    def is_static(self):
        return self.type == self.STATIC

    def is_param(self):
        return self.type == self.PARAM

    @classmethod
    def from_path(cls, path):
        path = trim_path(path)
        parts = path.split("/")
        segments = []
        for part in parts:
            if part.startswith(":"):
                segments.append(Segment.param(part[1:]))
            else:
                segments.append(Segment.static(part))
        return segments
