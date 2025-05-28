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

#### Composing `before_load` with Inheritance

When subclassing routes or using mixins, it is important to ensure that all `before_load` logic runs and that navigation context dictionaries are merged correctly. The recommended approach is to always call `super().before_load(**loader_args) or {}` in your subclass, and then merge or update the returned dictionary with your own additions.

**Example:**

```python
class AuthenticatedRoute(Route):
    def before_load(self, **loader_args):
        user = anvil.users.get_user()
        if user is None:
            raise Redirect(path="/login")
        return {"user": user}

class DashboardRoute(AuthenticatedRoute):
    def before_load(self, **loader_args):
        ctx = super().before_load(**loader_args) or {}
        ctx["dashboard_loaded"] = True
        return ctx
```

If you use mixins, always call `super().before_load(**loader_args) or {}` in each mixin as well. This ensures all hooks are run and their results are merged into the navigation context.
