## Params

The path may contain one or more path parameters, denoted by the `:` character, e.g. `/authors/:id`.

```python
from routing.router import Route

class AuthorRoute(Route):
    path = "/authors/:id"
    form = "Pages.Author"
```

When a user navigates to `/authors/123`, the routing context will include the path params `{"id": "123"}`.

```python
from ._anvil_designer import AuthorTemplate
from routing.router import RoutingContext

class Author(AuthorTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.routing_context = routing_context
        self.author = anvil.server.call("get_author", routing_context.params.get("id"))
        self.init_components(**properties)
```

## Parsing Params

Path parameters are always strings (they come from URL path segments). If you want to parse the params into a different type, you can use the `parse_params` method.

```python
class AuthorRoute(Route):
    path = "/authors/:id"
    form = "Pages.Author"

    def parse_params(self, params):
        return {"id": int(params["id"])}  # Convert string to int
```

!!! note

    Path params are always strings. If you need them as numbers or other types, convert them in your `parse_params` method.

## Navigating with Params

You can navigate to a route with params by passing the params option to the `navigate` function.

```python
from routing.router import navigate

...
    def button_click(self, **event_args):
        navigate(path="/authors/:id", params={"id": 123})
```

Or equivalently with routing `NavLink` or `Anchor` components.

```python
from ._anvil_designer import RowTemplateTemplate
from routing.router import NavLink

class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        self.add_component(
            NavLink(
                text=f"Author {self.item['name']}",
                path="/authors/:id",
                params={"id": self.item["id"]},
            )
        )
```

**Other equivalent ways to navigate include:**

```python
from routing.router import navigate
navigate(path="/authors/123")
# the params will still become {"id": "123"}
```

```python
from routing.router import navigate
from ...routes import AuthorRoute

navigate(path=AuthorRoute.path, params={"id": 123})
```
