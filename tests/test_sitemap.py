"""Exercise sitemap responses without starting the Anvil runtime."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture
def sitemap(monkeypatch):
    anvil = ModuleType("anvil")
    anvil.server = ModuleType("anvil.server")
    anvil.server.get_app_origin = lambda: "https://example.anvil.app"
    anvil.server.HttpResponse = lambda status, body: SimpleNamespace(
        status=status, body=body
    )
    anvil.BlobMedia = lambda **kwargs: SimpleNamespace(**kwargs)
    anvil.app = SimpleNamespace(get_client_config=lambda name: {})
    monkeypatch.setitem(sys.modules, "anvil", anvil)
    monkeypatch.setitem(sys.modules, "anvil.server", anvil.server)

    package_name = "_routing_sitemap_tests"
    package = ModuleType(package_name)
    package.__path__ = []
    router = ModuleType(f"{package_name}.router")
    router.__path__ = []
    router.sorted_routes = []
    router.debug_logging = Mock()
    imports = ModuleType(f"{package_name}.router._import_utils")
    imports.import_routes = Mock()
    for module in (package, router, imports):
        monkeypatch.setitem(sys.modules, module.__name__, module)

    spec = importlib.util.spec_from_file_location(
        f"{package_name}._special_routes",
        Path(__file__).parents[1] / "server_code" / "_special_routes.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "routes,expected_paths",
    [
        (
            [("/", True), ("/articles", True), ("/admin", False)],
            ["/", "/articles"],
        ),
        (
            [("/", False), ("/articles", True), ("/articles/:id", True)],
            ["/articles"],
        ),
        ([("/:category/articles", True), (None, True)], []),
    ],
)
def test_sitemap_includes_only_enabled_static_routes(sitemap, routes, expected_paths):
    sitemap.router.sorted_routes = [
        SimpleNamespace(
            path=path,
            sitemap=enabled,
            segments=[
                SimpleNamespace(is_param=lambda part=part: part.startswith(":"))
                for part in (path or "").split("/")
            ],
        )
        for path, enabled in routes
    ]

    response = sitemap.get_sitemap()

    assert response.status == 200
    assert response.body.content_type == "text/plain"
    assert response.body.content.decode().splitlines() == [
        f"https://example.anvil.app{path}" for path in expected_paths
    ]
