---
weight: -8
---

# Route Class

The `Route` class is used to define routes for your app. When a user navigates to a path, the router will look for a matching route. The router will call `anvil.open_form` on the matching route's form.

```python
# routes.py
from routing.router import Route

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"

class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

class ContactRoute(Route):
    path = "/contact"
    form = "Pages.Contact"
```

The above code can use the `Route.create()` method for convenience:

```python
# routes.py
from routing.router import Route

IndexRoute = Route.create(path="/", form="Pages.Index")
AboutRoute = Route.create(path="/about", form="Pages.About")
ContactRoute = Route.create(path="/contact", form="Pages.Contact")
```

## Route Attributes

`path`
: The path to navigate to. e.g. `/`, `/articles` or `/articles/:id`.

`form`
: The form to open when the route is matched. e.g. `Pages.Index`.

`error_form (optional)`
: The form to open when an error occurs. e.g. `Pages.Error`.

`not_found_form (optional)`
: The form to open when the route is not found. e.g. `Pages.NotFound`.

`pending_form (optional)`
: The form to open when the data is loading. e.g. `Pages.Loading`.

`pending_delay=1`
: The delay before showing the pending form when the data is loading.

`pending_min=0.5`
: The minimum time to show the pending form when the data is loading.

`cache_form=False`
: Whether to cache the route's form. By default this is `False`.

`cache_data=False`
: Whether to cache data. By default this is `False`.

`gc_time=30*60`
: The time in seconds that determines when data is released from the cache for garbage collection. By default this is 30 minutes. When data is released from the cache, any cached forms with the same `path` and `cache_deps` will also be released.

`server_fn (optional str)`
: The server function to call when the route is matched. e.g. `"get_article"`. This server function will be called with the same keyword arguments as the route's `load_data` method. Note this is optional and equivalent to defining a `load_data` method that calls the same server function.

`server_silent=False`
: If `True` then the server function will be called using `anvil.server.call_s`. By default this is `False`.

## Route Methods

`before_load`
: Called before the route is matched. If it raises a `Redirect`, navigation is redirected. If it returns a dictionary, its contents are merged into the navigation context (`nav_context`).

Note - you may prefer not to override this method, and instead use the `@hooks.before_load` decorator.

See the navigation documentation for practical usage examples.


`parse_query`
: Should return a dictionary of query parameters. By default this returns the original query parameters.

`parse_params`
: Should return a dictionary of path parameters. By default this returns the original path parameters.

`meta`
: Should return a dictionary with the `title` and `description` of the page. This will be used to update the meta tags and the title of the page. By default this returns the original title and description.

`load_data`
: Called when the route is matched. The return value will be available in the `data` property of the `RoutingContext` instance. By default this returns `None`.

`load_form`
: This method is called with two arguments. The first argument is a form name (e.g. `"Pages.Index"`) or, if you are using cached forms, the cached form instance. The second argument is the `RoutingContext` instance. By default this calls `anvil.open_form` on the form.

`cache_deps`
: Returns an object, by default the `query` dictionary (more information in the [query section](/routes/query/) and the [RoutingContext section](/routing-context/)). This method is part of the process of creating caching keys.
: When a route needs to cache a form or data (more information in the [caching section](/caching/)), it does so by storing it in a global dictionary under a caching key. This key is composed of the route's path and the return of its `cache_deps` method at the moment of caching.
: If, when accessing the same route, its `cache_deps` method returns something different than when caching first occured, the caching key points to a different place within the cache, usually empty. The router thus understands this as a new route and navigates to it again.

## Setting Meta Tags Per Route

To control meta tags for SEO and social sharing, override the `meta` method on your `Route` class. Return a dictionary of tags you want to set for that route. You can set any meta tag, including Open Graph and custom tags.

**Example:**

```python
from routing.router import Route

class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"

    def meta(self, **loader_args):
        query = loader_args["query"]  # Use query params for dynamic meta
        title = f"Article: {query.get('title', 'Untitled')}"
        return {
            "title": title,
            "description": f"Viewing article: {title}",

            "og:image": "asset:article_cover.png",  # use asset: prefix or a full URL
            "twitter:card": "summary_large_image",  # arbitrary tags supported
        }
```

**Fallbacks:**

-   `og:title` and `og:description` will automatically use `title` and `description` if not set.
-   If a meta tag is not set for a route, it falls back to the value present at app load.

**Server vs Client Meta Tags:**

-   `title`, `description`, `og:title` and `og:description` are set on the server.
-   All other tags are set after page load on the client.

**og:image and other assets:**

-   Use a full URL (e.g., `"https://my-app.anvil.app/_/theme/image.png"`)
-   Or use an asset from your app: `"asset:image.png"` and it will be resolved to the full URL

## Not Found Form

There are two ways a route can be not found. The first is when the user navigates to a path that does not match any routes. The second is when a user raises a `NotFound` exception in a route's `before_load` or `load_data` method.

### Not Found Route

By definition, if there is no matching route, the router has no route to navigate to. If you want to handle this case, you can define a not found route.

```python
from routing.router import Route

class NotFoundRoute(Route):
    form = "Pages.NotFound"
    default_not_found = True
```

The `NotFoundRoute` will be used when the user navigates to a path that does not match any routes. The `path` attribute should not be set, since this will be determined based on the path the user navigates to.

If no `default_not_found` attribute is set, then the router will raise a `NotFound` exception, which will be caught by Anvil's exception handler.

### Raising a NotFound Exception

If you raise a `NotFound` exception in a route's `before_load` or `load_data` method, the router will call the route's `load_form` method with the route's not found form.

```python
from routing.router import Route

class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"
    not_found_form = "Pages.ArticleNotFound"

    def load_data(self, **loader_args):
        id = loader_args["params"]["id"]
        article = app_tables.articles.get(id=id)
        if article is None:
            raise NotFound(f"No article with id {id}")
        return article
```

If a route raises a `NotFound` exception and there is no `not_found_form` attribute, the router will raise the exception, which will be caught by Anvil's exception handler.

## Error Form

When a route throws an exception, the router will call `anvil.open_form` on the matching route's error form.

If no error form is defined, the error will be caught by Anvil's exception handler.

```python
from routing.router import Route

# Either define the error form globally
Route.error_form = "Pages.Error"

# or define the error form per route
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    error_form = "Pages.Error"
```

```python
# Pages.Error
import anvil

class Error(ErrorTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        self.label.text = (
            f"Error when navigating to {routing_context.path!r}, got {routing_context.error!r}"
        )

    def form_show(self, **event_args):
        if anvil.app.environment.name.startswith("Debug"):
            raise self.routing_context.error
```

## Ordering Routes

The router will try to match routes in the order they are defined.

```python
from routing.router import Route

class AuthorsRoute(Route):
    path = "/authors"
    form = "Pages.Authors"

class NewAuthorRoute(Route):
    path = "/authors/new"
    form = "Pages.NewAuthor"

class AuthorRoute(Route):
    path = "/authors/:id"
    form = "Pages.Author"
```

In the above example, it's important that the `NewAuthorRoute` comes before the `AuthorRoute` in the list of routes. This is because `/authors/new` is a valid path for the `AuthorRoute`, so the router would successfully match the route and open the form.

## Server Routes

When a user navigates to a URL directly, the router will match routes on the server.

When you import your routes in server code, the router will automatically create a server route for each route.

```python
# ServerRoutes.py
from . import routes
```

Under the hood this will look something like:

```python
# ServerRoutes.py
from . import routes

# pseudo code - for illustration only
for route in Routes.__subclasses__():
    if route.path is None:
        continue

    @anvil.server.route(route.path)
    def server_route(**params):
        ...
        # return a response object that will open the form on the client
```
