# Query

Query parameters are encoded in a URL following a `?`, e.g. `/dashboard?tab=sales&page=1`.
Query parameters may be referred to by different names, e.g. search, search params, query params, etc.

Query parameters are used to make the URL reflect the state of the page. When the page updates in response to user interaction, the URL can be made to change to reflect those changes. Loading a URL with specific query parameters will also load the page in the state indicated by the parameters.

For example, if you have a dashboard page with a tab component, you can use the query to encode the active tab.

In this routing library, we will refer to `query` as a dictionary of query parameters.
And a `query string` will be the URL-encoded version of the `query`.

## Navigating

When navigating with `navigate` or `NavLink`, you should pass the query as a decoded Python dictionary (not a URL-encoded string). The routing library will handle encoding it into the URL automatically.

Let's say you have a dashboard page with a tab component.
The tab component has 2 tabs, income and expenses.

```python
from ._anvil_designer import DashboardTemplate
from routing.router import navigate, RoutingContext

class Dashboard(DashboardTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        routing_context.add_event_handler("query_changed", self.on_query_change)
        routing_context.raise_init_events() # raises the query_changed event

    def on_query_change(self, **event_args):
        query = self.routing_context.query
        self.tab_1.value = query.get("tab", "income")

    def tab_changed(self, **event_args):
        tab_value = self.tab_1.value
        navigate(query={"tab": tab_value})  # Pass decoded dict with proper types
```

Note that in the `tab_changed` event handler, we are navigating to the same path, and so, we don't need to include the `path` in the `navigate` call.
If we want to be explicit, we can use `path="./"` or `path="/dashboard"`.

### Query as a function

The `query` argument to `navigate` or `NavLink` can also be a function that takes the current query parameters as an argument and returns the new query parameters. This is useful for updating query parameters based on the current state.

```python
def toggle_filter(self, **event_args):
    def query(prev):
        return {**prev, "open": not prev.get("open", False)}
    navigate(query=query)
```

When using a query function, avoid modifying the query parameters directly. Instead, return a new dictionary.

By default, if the query parameters change, a new instance of the form will be loaded (even if `cache_form` is set to `True`). See `cache_deps` below for more details.
When the query parameters change, we can listen for the `query_changed` event and update our page state accordingly.

## Parsing Query Parameters

Since query parameters are encoded in the URL, we may need to decode them.
It's also generally a good idea to ignore unknown query parameters and provide sensible defaults if any are missing or incorrect. This provides a better user experience.

```python
from routing.router import Route

class DashboardRoute(Route):
    path = "/dashboard"
    form = "Pages.Dashboard"

    def parse_query(self, query):
        valid_tabs = ["income", "expenses"]
        tab = query.get("tab", "income")
        if tab not in valid_tabs:
            tab = "income"

        return {"tab": tab}
```

### Using a query validator

You can use a validator library. And if the validator has a `parse` method, it can be used as the `parse_query` attribute.

```python
from anvil_extras import zod as z

class DashboardRoute(Route):
    path = "/dashboard"
    form = "Pages.Dashboard"

    parse_query = z.typed_dict({
        "tab": z.enum(["income", "expenses"]).catch("income")
    })
```

## Query encoding

The routing library can encode any JSON-able object as a query parameter.
Where a query parameter is a `str`, `int`, `float`, `bool` or `None`, this will be flat.

e.g. `?foo=bar&baz=1&eggs=true` will be decoded as `{"foo": "bar", "baz": 1, "eggs": True}`.

For nested, JSON-able objects, i.e. `lists` and `dicts`, the routing library will encode the object as a JSON string in the query string.

e.g. `foo=%5B1%2C+%22a%22%2C+true%5D'` will be decoded as `{"foo": [1, "a", true]}`.

!!! note

    When you pass query parameters to `navigate` or `NavLink`, you should pass them as decoded Python objects (e.g., `{"page": 1}` not `{"page": "1"}`). The routing library handles encoding automatically.

    However, when reading query parameters from the URL (in `parse_query`), numbers will be decoded as integers/floats. If you need them as strings, you can convert them in your `parse_query` method.

## Loading a new instance of a form

By default, the routing library will load a new instance of a form when the query parameters change.

If you do NOT wish to load a new instance of a form when certain query parameters change, you can override the `cache_deps` method.

This method should return a `dict` of dependencies, which determine when a form and its data should be loaded from `cache`. The return value from `cache_deps` should be JSON-able.

```python
from routing.router import Route

class DashboardRoute(Route):
    path = "/dashboard"
    form = "DashboardForm"
    cache_form = True

    def cache_deps(self, **loader_args):
        # this form is cached uniquely by the `path` only - there are no `query` dependencies
        # i.e. if the `tab` changes, we keep the same instance of the form
        return None
```

For more details on `cache_deps`, see the data loading section.
