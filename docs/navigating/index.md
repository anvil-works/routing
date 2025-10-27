---
weight: -9
---

# Navigation

There are two ways to navigate. The first is with the `navigate` function, and the second is with a [navigation component](/navigating/navigation-components).

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
        self.init_components(**properties)

    def button_click(self, **event_args):
        router.navigate(
            path="/articles/:id",
            params={"id": self.item["id"]},
            form_properties={"item": self.item}
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

        self.init_components(**properties)
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
        self.init_components(**properties)

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

You can attach a hook to the `Route` base class to apply it to all routes:

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
from routing.router import Route, hooks, Redirect, Redirect

class AuthenticatedRoute(Route):
    @hooks.before_load
    def set_user(self, nav_context, **loader_args):
        nav_context["user"] = get_current_user()

    @hooks.before_load
    def check_permissions(self, nav_context, **loader_args):
        user = nav_context.get("user")
        if not user or not user.has_permission():
            raise Redirect(path="/login")

class FeatureRoute(AuthenticatedRoute):
    @hooks.before_load
    def add_feature_flag(self, nav_context, **loader_args):
        nav_context["feature_enabled"] = True
```

Hooks are called in order, and each can build on the output of previous hooks via `nav_context`.
