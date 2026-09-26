"""Exercise link setters with real URL conversion and a stand-in UI provider."""

import importlib
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import anvil
import pytest
from anvil.history import Location


@pytest.fixture
def anchor(monkeypatch):
    # Load the client modules without the router's public API initialisation.
    package_name = "_routing_link_tests"
    package = ModuleType(package_name)
    package.__path__ = [str(Path(__file__).parents[1] / "client_code" / "router")]
    monkeypatch.setitem(sys.modules, package_name, package)
    designer = ModuleType("anvil.designer")
    designer.in_designer = False
    designer.register_interaction = Mock()
    designer.start_editing_form = Mock()
    monkeypatch.setitem(sys.modules, "anvil.designer", designer)

    class Component:
        _anvil_properties_ = []

        def __init__(self, **properties):
            pass

        def add_event_handler(self, *args):
            pass

    monkeypatch.setattr(anvil, "Component", Component)
    provider = ModuleType(f"{package_name}._BaseLinks")
    provider.setup_base_anchor = lambda: type("BaseAnchor", (Component,), {})
    monkeypatch.setitem(sys.modules, provider.__name__, provider)
    # Full server URLs need an app origin, which is irrelevant to this test.
    monkeypatch.setattr(Location, "get_url", lambda self, full=False: str(self))
    try:
        yield importlib.import_module(f"{package_name}.Anchor").Anchor
    finally:
        for name in list(sys.modules):
            if name.startswith(package_name + "."):
                del sys.modules[name]


@pytest.mark.parametrize(
    "prop,initial,value,expected",
    [
        ("path", {"path": "/original-path"}, "/modified-path", "/modified-path"),
        ("query", {"path": "/articles"}, {"page": "2"}, "/articles?page=2"),
        (
            "params",
            {"path": "/articles/:id", "params": {"id": "1"}},
            {"id": "2"},
            "/articles/2",
        ),
        ("hash", {"path": "/articles"}, "details", "/articles#details"),
    ],
)
def test_navigation_property_updates_href_and_click(
    anchor, monkeypatch, prop, initial, value, expected
):
    link = anchor(**initial)
    link._rn_setup()
    original_href = link.href

    setattr(link, prop, value)

    assert link.href == expected
    assert link.href != original_href
    common = sys.modules[f"{anchor.__module__.rsplit('.', 1)[0]}._LinkCommon"]
    navigate = Mock()
    monkeypatch.setattr(common, "navigate_with_location", navigate)
    link._rn_do_click(None)
    assert str(navigate.call_args.args[0]) == expected


def test_invalid_params_clear_href_and_recover(anchor):
    link = anchor(path="/articles/:id", params={"id": "1"})
    link._rn_setup()

    link.params = {}

    assert link.href == ""
    exceptions = sys.modules["_routing_link_tests._exceptions"]
    with pytest.raises(exceptions.InvalidPathParams, match="No path param for id"):
        link._rn_do_click(None)

    link.params = {"id": "2"}
    assert link.href == "/articles/2"
    assert link._rn.invalid is None


def test_navigation_keeps_fixed_destination_cached(anchor, monkeypatch):
    link = anchor(path="/articles")
    link._rn_setup()
    common = sys.modules[f"{anchor.__module__.rsplit('.', 1)[0]}._LinkCommon"]
    convert = Mock(wraps=common.nav_args_to_location)
    monkeypatch.setattr(common, "nav_args_to_location", convert)

    common.navigation_emitter.raise_event("navigate")

    assert link.href == "/articles"
    convert.assert_not_called()


def test_cached_destination_gets_distinct_history_entries(anchor, monkeypatch):
    from types import SimpleNamespace

    navigation = sys.modules["_routing_link_tests._navigate"]
    entries = []
    intents = []

    def push(location):
        fake_history.location = location
        entries.append(location)
        intents.append(navigation._take_new_navigation(location.key))

    fake_history = SimpleNamespace(
        location=Location(path="/start"), push=push, replace=push
    )
    monkeypatch.setattr(navigation, "history", fake_history)
    destination = Location(path="/articles", state={"user": "state"})
    for _ in range(2):
        navigation.navigate_with_location(destination)
        navigation.navigate_with_location(Location(path="/other"))

    assert entries[0].key != entries[2].key
    assert entries[0].state == entries[2].state == {"user": "state"}
    assert destination.key not in {entry.key for entry in entries}
    assert intents == [True] * 4
    assert navigation._take_new_navigation(entries[0].key) is False


def test_failed_history_write_does_not_leak_navigation_intent(anchor, monkeypatch):
    from types import SimpleNamespace

    navigation = sys.modules["_routing_link_tests._navigate"]
    fake_history = SimpleNamespace(
        location=Location(path="/start"),
        push=Mock(side_effect=RuntimeError("write failed")),
    )
    monkeypatch.setattr(navigation, "history", fake_history)
    with pytest.raises(RuntimeError, match="write failed"):
        navigation.navigate(path="/articles")
    attempted_location = fake_history.push.call_args.args[0]
    assert navigation._take_new_navigation(attempted_location.key) is False
