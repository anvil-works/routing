"""Forms for the browser scroll regression checks; never published."""

import anvil
from anvil.history import history
from anvil.js import window
from routing.router import _navigate, _scroll, _view_transition
from routing.router._context import RoutingContext
from routing.router._exceptions import Redirect
from routing.router._route import Route, TemplateWithContainerRoute
from routing.router._router import client

_view_transition.use_transitions(False)
RoutingContext._current = None
client.navigation_blockers.clear()
client.waiting = False
_scroll.setup()
window.document.documentElement.style.overflowX = "auto"
window.document.body.style.overflowX = "visible"
window.document.body.style.minWidth = "1800px"
history.listen(client.listener)


class Layout(anvil.HtmlPanel):
    pass


layout = Layout(
    html="""
<aside id="scroll-sidebar" style="position:fixed;height:180px;overflow:auto;width:150px">
<div style="height:1500px">Sidebar</div></aside>
<div id="element-restore" data-routing-scroll-id="main" data-routing-scroll="default"
 style="position:fixed;left:700px;top:10px;height:180px;width:180px;overflow:auto;border:3px solid">
 <div style="height:1600px;width:900px"><div style="height:900px"></div>
 <h2 id="element-anchor" style="scroll-margin-top:25px">Element anchor</h2>
 <div id="nested-none" data-routing-scroll-id="nested" data-routing-scroll="none"
 style="height:100px;overflow:auto"><div style="height:900px">
 <div style="height:500px"></div><h2 id="nested-anchor">Nested</h2></div></div>
 </div></div>
<div id="element-auto" data-routing-scroll-id="second" data-routing-scroll="auto"
 style="position:fixed;left:900px;top:10px;height:180px;width:180px;overflow:auto">
 <div style="height:1600px;width:900px">Auto</div></div>
<div id="element-none" data-routing-scroll-id="none" data-routing-scroll="none"
 style="position:fixed;left:1100px;top:10px;height:180px;width:180px;overflow:auto">
 <div style="height:1600px">None</div></div>
<div id="element-unregistered" data-routing-scroll="auto"
 style="position:fixed;left:1300px;top:10px;height:180px;width:180px;overflow:auto">
 <div style="height:1600px">No ID</div></div>
<div anvil-slot="content" style="margin-left:180px"></div>
"""
)
layout.content_panel = anvil.FlowPanel()
layout.add_component(layout.content_panel, slot="content")


class Page(anvil.HtmlPanel):
    def __init__(self, routing_context, **properties):
        anvil.HtmlPanel.__init__(
            self,
            html="""
<div style="height:3000px;width:1600px" id="scroll-page">
<div style="height:1000px"></div>
<h2 id="section:a" style="scroll-margin-top:40px">Section</h2>
<h2 id="#section" style="scroll-margin-top:40px">Leading hash ID</h2>
</div>""",
        )
        self.routing_context = routing_context


class AppRoute(TemplateWithContainerRoute):
    template = layout
    form = Page
    scroll_default = "restore"

    def load_form(self, form, routing_context):
        if isinstance(form, type):
            form = form(routing_context=routing_context)
        return TemplateWithContainerRoute.load_form(self, form, routing_context)


class Bootstrap(AppRoute):
    path = window.scrollTestBootstrapPath
    scroll_manage_elements = True


class PageA(AppRoute):
    path = "/__scroll/a"


class PageB(AppRoute):
    path = "/__scroll/b"


class Cached(AppRoute):
    path = "/__scroll/cached"
    cache_form = True

    def cache_deps(self, **loader_args):
        return {}


class PathRestoration(Cached):
    path = "/__scroll/by-path"

    def scroll_restoration_key(self, location):
        return location.path


class PathPreserve(PathRestoration):
    path = "/__scroll/by-path-preserve"
    scroll_document = "none"


class PathNoRestore(PathRestoration):
    path = "/__scroll/by-path-disabled"
    scroll_default = "auto"


class Standalone(Cached):
    path = "/__scroll/standalone"

    def load_form(self, form, routing_context):
        if isinstance(form, type):
            form = form(routing_context=routing_context)
        return Route.load_form(self, form, routing_context)


class NoRestore(AppRoute):
    path = "/__scroll/no-restore"
    scroll_default = "auto"


class Preserve(AppRoute):
    path = "/__scroll/preserve"
    scroll_document = "none"


class Auto(AppRoute):
    path = "/__scroll/auto"
    scroll_default = "auto"


class Elements(AppRoute):
    path = "/__scroll/elements"
    scroll_document = "none"
    scroll_manage_elements = True


class ElementsDefault(Elements):
    path = "/__scroll/elements-default"
    scroll_document = "default"


class ElementsOverride(Elements):
    path = "/__scroll/elements-override"
    scroll_default = "none"


class Redirected(Preserve):
    path = "/__scroll/redirect"

    def before_load(self, **loader_args):
        raise Redirect(path="/__scroll/b")


class RedirectToPreserve(AppRoute):
    path = "/__scroll/redirect-preserve"

    def before_load(self, **loader_args):
        raise Redirect(path="/__scroll/preserve")


class InvalidKey(AppRoute):
    path = "/__scroll/invalid-key"

    def scroll_restoration_key(self, location):
        raise ValueError("fixture key failure")


class Failed(AppRoute):
    path = "/__scroll/failed"

    def before_load(self, **loader_args):
        raise ValueError("fixture failure")


class Handled(Failed):
    path = "/__scroll/handled"
    error_form = Page


class Pending(anvil.HtmlPanel):
    def __init__(self, **properties):
        anvil.HtmlPanel.__init__(
            self, html='<div id="scroll-pending" style="height:3000px">Pending</div>'
        )


class Slow(AppRoute):
    path = "/__scroll/slow"
    pending_form = Pending
    pending_delay = 0.01
    pending_min = 0

    def load_data(self, **loader_args):
        from time import sleep

        sleep(0.4)


class ShortPending(anvil.HtmlPanel):
    def __init__(self, **properties):
        anvil.HtmlPanel.__init__(
            self,
            html='<div id="scroll-short-pending" style="height:40px">Pending</div>',
        )


class ShortSlow(Slow):
    path = "/__scroll/short-slow"
    pending_form = ShortPending


# Start from a real history entry so reload keeps a stable key.
if window.scrollTestReload:
    client.on_navigate()
else:
    _navigate.navigate(path="/__scroll/a", replace=True)
