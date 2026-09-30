---
weight: -9
---

# Navigation

There are two ways to navigate. The first is with the `navigate` function, and the second is with a [navigation component](navigation-components.md).

## Navigating with `navigate`

The `navigate` function lets you navigate to a specific path through code. It is a function that you will likely call from a click handler.

Do note that the `navigate` function can only be called from client code.

```python
from routing.router import navigate


class Form(FormTemplate):
    def nav_button_click(self, **event_args):
        navigate(path="/articles/:id", params={"id": 123})
```

### Call Signatures

-   `navigate(*, path=None, params=None, query=None, hash=None, replace=False, nav_context=None, form_properties=None)`
    _use keyword arguments only_
-   `navigate(path, **kws)`
    _the first argument can be the path_
-   `navigate(url, **kws)`
    _the first argument can be a URL_
-   `navigate(routing_context, **kws)`
    _the first argument can be a routing context_

### Arguments

`path`
: The path to navigate to. e.g. `/articles/123` or `/articles` or `/articles/:id`. The path can be relative `./`. If not set, then the path will be the current path.

`params`
: The params for the path. e.g. `{"id": 123}`

`query`
: The query parameters to navigate to. e.g. `{"tab": "income"}`. This can be a function that takes the current query parameters as an argument and returns the new query parameters. If you provide a query function, avoid modifying the query parameters directly, instead return a new dictionary.

```python
def on_button_click(self, **event_args):
    def query(prev):
        return {**prev, "open": not prev.get("open", False)}

    navigate(query=query)
```

`hash`
: The hash to navigate to.

`replace`
: If `True`, then the current URL will be replaced with the new URL (default is `False`).

`nav_context`
: The nav context for this navigation.

`form_properties`
: The form properties to pass to the form when it is opened.

### Use of `form_properties`

The `form_properties` is a dictionary that is passed to the `open_form` function. A common use case is to pass the form's `item` property. Note that if you are relying on `form_properties`, you will always need to account for `form_properties` being an empty dictionary when the user navigates by changing the URL directly.

```python
from routing import router


class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        super().__init__(**properties)

    def button_click(self, **event_args):
        router.navigate(
            path="/articles/:id",
            params={"id": self.item["id"]},
            form_properties={"item": self.item},
        )
```

And then in the `/articles/:id` route:

```python
from routing import router


class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        if properties.get("item") is None:
            # The user navigated directly
            # to the form by changing the URL
            article_id = routing_context.params["id"]
            properties["item"] = anvil.server.call("get_article", article_id)

        super().__init__(**properties)
```

### Use of `nav_context`

The `nav_context` is a dictionary that is passed to the `navigate` function. A use case for this is to pass the previous routing context to the next routing context. This is useful when you want to navigate to a new route but want to preserve the previous route's data, particularly if the previous route uses query parameters that determine the state of the form.

```python
from routing import router


def on_button_click(self, **event_args):
    current_context = router.get_routing_context()
    router.navigate(path="/foo", nav_context={"prev_context": current_context})
```

And then in the `/foo` route:

```python
from routing import router


class FooForm(FooFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        super().__init__(**properties)

    def cancel_button_click(self, **event_args):
        prev_context = self.routing_context.nav_context.get("prev_context")
        if prev_context is not None:
            router.navigate(prev_context)
        else:
            # No nav-context - the user navigated directly to the form by changing the URL
            router.navigate(path="/")
```

#### Updating `nav_context` from `before_load`

You can also update the navigation context from a route's `before_load` method by returning a dictionary. The returned dictionary will be merged into `nav_context` for the route:

```python
class DashboardRoute(Route):
    path = "/dashboard"
    form = "Pages.Dashboard"

    def before_load(self, **loader_args):
        # Add a value to nav_context for this navigation
        return {"show_sidebar": True}
```

In this example, `routing_context.nav_context["show_sidebar"]` will be `True` when the form is loaded.

---

## Advanced: Composing hooks.before_loads

The `@hooks.before_load` decorator enables you to compose multiple hooks for a single route, supporting advanced patterns such as mixins, inheritance, and global hooks.

### Multiple Hooks and Inheritance

Hooks are collected from all base classes and **run in reverse MRO order** (base classes first, derived classes last), allowing you to layer behaviors:

```python
from routing.router import Route, hooks, Redirect


class AuthenticatedRoute(Route):
    @hooks.before_load
    def check_auth(self, **loader_args):
        if not user_is_authenticated():
            raise Redirect(path="/login")
        return {"user": get_current_user()}


class FeatureFlagMixin:
    @hooks.before_load
    def add_feature_flag(self, **loader_args):
        return {"feature_enabled": True}


class DashboardRoute(FeatureFlagMixin, AuthenticatedRoute):
    path = "/dashboard"
    form = "Pages.Dashboard"

    @hooks.before_load
    def dashboard_flag(self, **loader_args):
        return {"show_dashboard": True}
```

**Hook execution order (reverse MRO):**
1. `AuthenticatedRoute.check_auth` (most base)
2. `FeatureFlagMixin.add_feature_flag` (middle)
3. `DashboardRoute.dashboard_flag` (most derived)

This order ensures base classes can set up context (like authentication) that derived classes depend on.

### Global Hooks

Attach a hook to the `Route` base class before defining route subclasses. Hooks are collected when each subclass is created:

```python
@hooks.before_load
def global_hook(self, **loader_args):
    # e.g., add analytics or logging
    return {"analytics_id": "xyz"}


Route.global_hook = global_hook
```

### Best Practices
- Each hook should return only the context it wants to add (or raise for control flow).
- Hooks should expect a `nav_context` kwarg and can read or update it for composable navigation logic.
- Hooks may also return a dict with additional context to be merged into `nav_context` after the hook runs. This allows both direct mutation and returned values to contribute to the final context.

- Use mixins or base classes to share common hooks across multiple routes.
- Global hooks are powerful for cross-cutting concerns, but use them judiciously to avoid surprises.

**Example:**
```python
from routing.router import Route, hooks, Redirect


class AuthenticatedRoute(Route):
    @hooks.before_load
    def require_user(self, nav_context, **loader_args):
        user = get_current_user()  # Application-defined helper
        if not user or not user.has_permission():
            raise Redirect(path="/login")
        return {"user": user}


class FeatureRoute(AuthenticatedRoute):
    @hooks.before_load
    def add_feature_flag(self, nav_context, **loader_args):
        nav_context["feature_enabled"] = True
```

Hooks in different classes run in reverse MRO order. Within one class, the current implementation runs hooks in reverse definition order. Keep dependent steps in a single hook, as in `require_user` above. Overriding `before_load` bypasses decorated hooks unless the override calls `super().before_load(**loader_args)`.

## Document scrolling

For ordinary history restoration, enable it on your app's base route:

```python
class AppRoute(router.Route):
    scroll_default = "restore"
```

Add `scroll_manage_elements = True` when your layout also has registered scrollable
panels. The destination route supplies these inherited settings:

```python
class Route:
    scroll_default = "auto"
    scroll_document = "default"
    scroll_manage_elements = False

    def scroll_restoration_key(self, location):
        return location.key
```

`scroll_default` accepts three policies:

| Policy | Behaviour |
| --- | --- |
| `"auto"` | Scroll to the URL fragment's target, or to the top when no fragment is present. A missing target causes no movement. No positions are saved. |
| `"restore"` | Save both scroll axes and restore a saved position when available; otherwise use `"auto"`. Saved positions take precedence over anchors. |
| `"none"` | No router saving or scrolling for this area. |

`scroll_document` accepts those policies or `"default"`, which uses
`scroll_default`. Python `None` is not a policy. New visits, query changes and
replacements follow the same rules. Identical URLs remain a no-op.

### Scrollable elements

Enable `scroll_manage_elements` to discover elements with
`data-routing-scroll-id` after the final form attaches. Each ID must be nonempty,
stable across renders and unique on the page. Without an ID an element is
unmanaged, even if it has a `data-routing-scroll` attribute.

```python
class AppRoute(router.Route):
    scroll_default = "restore"
    scroll_document = "none"
    scroll_manage_elements = True
```

```html
<!-- Omitted policy and explicit "default" both use the route's scroll_default -->
<main data-routing-scroll-id="content" data-routing-scroll="default">
  ...
</main>

<!-- Explicit policies override the route default -->
<aside data-routing-scroll-id="sidebar" data-routing-scroll="none">
  ...
</aside>
```

`data-routing-scroll` accepts `"default"`, `"auto"`, `"restore"`, or `"none"`.
Invalid policies and empty or duplicate registered IDs are configuration errors.
Setting `scroll_manage_elements=False` disables discovery, saving and scrolling
for elements; document handling is independent. To disable all router scrolling,
set `scroll_document="none"` and `scroll_manage_elements=False`.
`scroll_default="none"` alone is not a global disable: explicit overrides still
apply. To undo an inherited document override, set `scroll_document="default"`.

### Restoration identity

Positions use versioned, app-scoped session storage. The route's
`scroll_restoration_key(location)` identifies the visit; the element ID identifies
the area within that visit. The document has a separate internal identity.
The default visit key is `location.key`, so Back/Forward and reload restore while
new link visits start with no saved position. In other words, `"restore"` remembers
a visit by default, rather than every visit to a page.

| Navigation | Default history-entry identity |
| --- | --- |
| Click a link to a page | A new entry has no saved position: anchor/top. |
| Back/Forward | Revisit an entry and restore its saved position. |
| Reload | Restore the current entry's saved position. |

To remember a page across new link visits, override the identity with its path:

```python
class SearchRoute(AppRoute):
    path = "/search"

    def scroll_restoration_key(self, location):
        return location.path
```

This shares positions across visits to the same path, including query and fragment
variants. Later saves replace earlier coordinates for that path and area. Include
`location.search` in the returned string if query variants need separate positions.
If storage is unavailable or a record is invalid, `"restore"` uses `"auto"`;
there is no in-memory fallback.

### Forms and DOM lifetime

`"none"` means the router leaves an area's scroll position alone; it does not
preserve a position across removal and recreation of that element. A new element
normally starts at zero. `"restore"` can recover the previous position using its
stable scroll ID when returning to a saved visit.

Cached forms still receive the destination route's scroll policy. Form caching
reuses the form instance, but detaching and reattaching its DOM can still lose
browser scroll state. Use restoration when a position must survive navigation. A persistent element that stays mounted can retain its position
without router intervention.

### Anchors and timing

An anchor belongs to its nearest ancestor with a scroll ID when element management
is enabled, otherwise to the document. Only that owner performs anchor scrolling,
respecting `scroll-margin-top` and changing only its own scroll offsets. An owner
with policy `"none"` suppresses anchor scrolling, without falling back to an outer
area. Other areas do not reset to the top while a fragment is present, but may
restore their own saved positions. When element management is off, document
scrolling cannot reveal a target hidden inside an independently scrolling panel.

Scrolling is instant and occurs once after the final form attaches and a render
frame is scheduled. Pending forms do not trigger scrolling; rendered error and
not-found forms do. Blocked, stale or failed navigation without a final form does
not scroll. Outgoing positions are captured before content changes and on pagehide.
There are no delayed-content retries. A custom `load_form` must return its attached
form, as the built-in implementations do.

Links, redirects and `navigate` use the final destination route's settings; there
are no per-navigation overrides. The router disables native automatic history
restoration to avoid competing browser operations.
