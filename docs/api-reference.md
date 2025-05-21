---
weight: -9.7
---

# API Reference

The routing library provides the following functions, classes, and attributes.
All attributes can be accessed from the `routing.router` module.

## Router Configuration

The router exposes a `config` dictionary for enabling or disabling advanced features. You should set these options where you define your routes (typically in your `routes.py` or equivalent):

```python
from routing import router

# Opt out of automatic /sitemap.txt and /robots.txt
router.config.update(
    sitemap=False,
    robots=False,
)
```

**Config Options:**
- `sitemap`: If `False`, disables the automatic `/sitemap.txt` route. Defaults to `True`.
- `robots`: If `False`, disables the automatic `/robots.txt` route. Defaults to `True`.

By default, both features are enabled.


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
