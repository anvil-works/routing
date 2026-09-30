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

## Scrolling

By default, navigation scrolls the document to the top. A URL fragment such as
`#comments` scrolls to that element instead. If the element is missing, the router
leaves the scroll position alone. Query changes and replacements follow the same
rules; navigating to an identical URL does nothing.

### Restore positions with Back and Forward

Enable restoration on your app's base route:

```python
from routing.router import Route


class AppRoute(Route):
    scroll_default = "restore"
```

Routes inheriting from `AppRoute` remember each visit's scroll position:

| Navigation | What happens |
| --- | --- |
| Click a link | Start a new visit: scroll to the fragment or top. |
| Back or Forward | Restore that visit's saved position. |
| Reload | Restore the current visit's saved position. |

A saved position takes precedence over a fragment. Positions are stored in the
browser's session storage. If saving is unavailable or a record is invalid,
the router uses the usual fragment/top behavior.

### Restore by path across new link clicks

To remember the latest position for each path, including new link clicks,
give your base route a path-based restoration key:

```python
class AppRoute(Route):
    scroll_default = "restore"

    def scroll_restoration_key(self, location):
        return location.path
```

The default key, `location.key`, distinguishes browser history entries. Using
`location.path` shares the latest position across visits to that path, including
query and fragment changes. Return `location.path + location.search` to keep
query variants separate.

### Choose a scroll policy

`scroll_default` sets the policy for the document and any managed scrollable
panels:

| Policy | Behavior |
| --- | --- |
| `"auto"` | Scroll to the fragment, or top if there is no fragment. Save no positions. This is the default. |
| `"restore"` | Restore a saved position when available; otherwise use `"auto"`. Save both horizontal and vertical positions. |
| `"none"` | Leave the scroll position alone. Save no positions. |

To give the document a different policy, set `scroll_document` on a route:

```python
class SearchRoute(AppRoute):
    path = "/search"
    form = "Pages.Search"
    scroll_document = "none"
```

Its default value, `"default"`, uses `scroll_default`. Set it back to `"default"`
to remove an inherited override. These settings apply to the final destination
of links, redirects and `navigate`; there are no per-navigation scroll options.

### Manage scrollable panels

Panel scrolling is opt-in. Enable it on a base route and give each scrollable
element a nonempty ID that is stable across renders and unique on the page:

```python
class PanelRoute(AppRoute):
    scroll_manage_elements = True
```

```html
<main data-routing-scroll-id="results">...</main>
<aside data-routing-scroll-id="sidebar" data-routing-scroll="auto">...</aside>
```

Here, `results` inherits `scroll_default="restore"` from `AppRoute`, while
`sidebar` uses `"auto"` instead of restoring saved positions. `data-routing-scroll`
accepts `"auto"`, `"restore"`,
`"none"`, or `"default"`. Omitting it is the same as `"default"`.

Elements without `data-routing-scroll-id` are unmanaged. With
`scroll_manage_elements=False`, the default, the router does not look for or
manage panels. Document scrolling is independent: set `scroll_document="none"`
and `scroll_manage_elements=False` to turn off all router scrolling. Explicit
panel policies still apply when `scroll_default="none"`.

`"none"` does not preserve a panel's position when its DOM is removed and
recreated. New elements normally start at zero. Cached forms follow the same
policies, and detaching their DOM can lose scroll state. Use `"restore"` and stable IDs to recover
saved positions. A panel that stays mounted can retain its position without
router intervention.

### Anchors and loading

For a fragment inside a managed panel, the router scrolls its nearest managed
ancestor. Otherwise it scrolls the document. It respects `scroll-margin-top` and
moves only that area's scroll offsets. A panel with `"none"` prevents anchor
scrolling inside it. Other areas can restore saved positions but do not scroll
to the top while a fragment is present. Document scrolling alone cannot reveal
a target hidden inside an independently scrolling panel.

Scrolling is instant and happens once after the destination form is attached.
Pending forms do not trigger it; error and not-found forms do. Canceled or failed
navigation that does not display a destination does not scroll. Targets added
later are not retried.
