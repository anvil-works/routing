---
weight: -9.7
---

# API Reference

The routing library provides the following functions, classes, and attributes.
All attributes can be accessed from the `routing.router` module.

## Router Configuration

When adding the routing library as a dependency, in the Anvil IDE, click the "edit" icon next to the routing library in the dependencies list. This will allow you to change the configuration options.

### Config Options:

`sitemap`
: If `False`, disables the automatic `/sitemap.txt` route. Defaults to `False`.

`robots`
: If `False`, disables the automatic `/robots.txt` route. Defaults to `False`.

`routes_module`
: The module where your routes are defined (e.g. `utils.routes`). Defaults to `routes`.

#### `routes_module`

If set, the router will automatically import this module for you, and you do **not** need to explicitly import your routes module in client or server code. This is the preferred approach for most projects. By default this is set to `routes`.

If you do not set this option correctly, you must explicitly import your routes module in your startup and server code:

```python
  # In a startup module, e.g. startup.py
  from . import routes

  # In a server module, e.g. ServerRoutes.py
  from . import routes
```


## Functions

`navigate(*, path=None, params=None, query=None, hash=None, replace=False, nav_context=None, form_properties=None)`
`navigate(path, **kws)`
`navigate(url, **kws)`
`navigate(routing_context, **kws)`
: Navigates to a new page.

`launch()`
: Launches the routing library and navigates to the first route. Call this in your startup module.

`go(n=0)`
: Navigates to the nth page in the history stack.

`back()`
: Navigates back in the history stack.

`forward()`
: Navigates forward in the history stack.

`reload(hard=False)`
: Reloads the current page. If `hard` is `True`, the page will be reloaded from the server. If `hard` is `False`, the page will be removed from the cache and reloaded on the client.

`add_event_handler(event_name, handler)`
: Adds an event handler for the given event name. The event handler should take a `**event_args` argument. The `event_name` can be one of the following:

-   `"navigate"`: raised when the url changes.
-   `"pending"`: raised when the navigation starts.
-   `"idle"`: raised when the navigation is complete.

`remove_event_handler(event_name, handler)`
: Removes an event handler for the given event name.

`get_routing_context()`
: Returns the current routing context.

`use_data(context_or_path_or_url=None, *, path=None, params=None, query=None, hash=None)`
: Loads and returns the data for the specified url/context (or for the specified path/params/query/hash). Returns the data (or raises if there is an error). If called with no arguments, uses the current navigation context.

Can be useful for routes that share data. Or layouts that need access to the data for the current route.

`get_url()`
`get_url(*, path=None, params=None, query=None, hash=None, full=False)`
`get_url(path, **kws)`
`get_url(routing_context, **kws)`
: Gets the URL. If no keyword arguments are passed, the current URL will be returned. If `full` is `True`, the full URL will be returned (e.g., `http://my-app.anvil.app/articles/123?foo=bar#hash`). If `full` is `False`, the URL will be relative to the base URL (e.g., `/articles/123?foo=bar#hash`).

`debug_logging(enable=True)`
: Enables or disables debug logging.

`clear_cache()`
: Clears the cache of forms and data.

`invalidate(*, path=None, deps=None, exact=False)`
: Invalidates any cached data and forms based on the path and deps. The `exact` argument determines whether to invalidate based on an exact match or a partial match.

`open_form(form, **form_properties)`
: When migrating, you may be able to replace `anvil.open_form` with `router.open_form`. This will only work if you are not using `params`.

`alert(content, *args, dismissible=True, **kwargs)`
: Shows an alert. If `dismissible` is `True`, the alert will be dismissed when the user navigates to a new page. To override Anvil's default alert, you can set the `anvil.alert = router.alert`.

`confirm(content, *args, dismissible=True, **kwargs)`
: Shows a confirmation dialog. If `dismissible` is `True`, the dialog will be dismissed when the user navigates to a new page. To override Anvil's default alert, you can set the `anvil.alert = router.alert`.

`register_links(*dom_nodes, selector="a[href^='/']", active_class="active", active_callback=None, exact_path=False, exact_query=False, exact_hash=False)`
: Registers existing DOM links for client-side routing with active state tracking. Automatically detects if elements are `<a>` tags (registers directly) or containers (searches within using the selector). Returns a cleanup function to unregister links and remove event listeners. Useful for converting static HTML links to use the router without needing NavLink components.

`hooks.before_load(func)`
: Decorator to register a method as a before_load hook for a Route. Hooks are called in the order they are defined on the class. Each hook receives a `nav_context` keyword argument (the context dict accumulated so far), which can be read and updated for composable navigation logic.

```python
from routing.router import Route, hooks, Redirect

class AuthenticatedRoute(Route):
    # Style 1: Mutate nav_context directly
    @hooks.before_load
    def set_user(self, nav_context, **loader_args):
        nav_context["user"] = get_current_user()

    # Style 2: Return a partial dict to be merged into nav_context
    @hooks.before_load
    def set_user_partial(self, nav_context, **loader_args):
        return {"user": get_current_user()}

    @hooks.before_load
    def check_permissions(self, nav_context, **loader_args):
        user = nav_context.get("user")
        if not user or not user.has_permission():
            raise Redirect(path="/login")

# Both styles are supported; the returned dictionary (if any) will be merged into nav_context after the hook runs.
```

You may also attach hooks globally to all routes by assigning to the base class:

```python
@hooks.before_load
def global_hook(self, nav_context, **loader_args):
    nav_context["feature_enabled"] = True
Route.global_hook = global_hook
```

See the navigation documentation for advanced composition and usage patterns.

## Classes

`Route`
: The base class for all routes.

`RoutingContext`
: Provides information about the current route and navigation context. Passed to all forms instantiated by the routing library.

`sorted_routes`
: A list of all registered routes, sorted in the order they will be matched. Useful for introspection, generating sitemaps, or custom navigation logic.

## Components

`NavLink.NavLink`
: A link that you will likely use in your main layout's sidebar. Has an `active` property that is set when the NavLink's navigation properties match the current routing context.

`Anchor.Anchor`
: A link that you can use inline or as a container for other components.

## Context Managers

`NavigationBlocker`
: A context manager that will prevent the user from navigating away during the context.

## Exceptions

`Redirect`
: Raise during a route's `before_load` method to redirect to a different route.

`NotFound`
: Raised when a route is not found for a given path.
