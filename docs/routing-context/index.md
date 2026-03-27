---
weight: -7
---

# Routing Context

A `RoutingContext` instance is passed to a form when it is instantiated.
It provides information about the current route and the current navigation context.

```python
from ._anvil_designer import IndexTemplate
from routing.router import RoutingContext

class IndexTemplate(IndexTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)
```

!!! Autocompletion

    Adding the `RoutingContext` type definition will allow Anvil to show autocompletion for the `routing_context` property.

## Properties

`path`
: The path for the current route.

`params`
: The parameters for the current route.

`query`
: The query parameters for the current route.

`hash`
: The hash for the current route.

`deps`
: The dependencies `dict` returned by the `cache_deps` method.

`nav_context`
: The navigation context for the current route. This is a `dict` and can be set by passing a `nav_context` argument to the `navigate` method. (Or equivalently by setting the `nav_context` attribute on a `NavLink`/`Anchor` component).

`form_properties`
: The form properties for the current route. This is a `dict` and can be set by passing a `form_properties` argument to the `navigate` method. (Or equivalently by setting the `form_properties` attribute on the `NavLink`/`Anchor` component). Note the `form_properties` are passed as keyword arguments when instantiating a form. For more details see the Navigation section.

`error`
: The error that occurred when loading the form or loading the data. This is particularly useful when displaying error messages in your error form.

`data`
: The data for the current route. This is the value returned from the `load_data` method.

`revalidating`
: `True` when routing is currently refreshing cached data in the background.


<!-- `match`

: The `Match` instance for the current route.

`location`

: The `Location` instance for the current route.

`route`

: The `Route` instance for the current route. -->

## Events

The `RoutingContext` instance will emit events when the route changes.

`data_loading`
: Emitted when the data is loading. This also fires from `raise_init_events()` if the current context already has cached data and is revalidating it in the background.

`data_loaded`
: Emitted when the data has been loaded, or when the data has an error. To determine if the data is loaded successfully, check the `error` property is `None`.

`data_error`
: Emitted when the data has an error.

`query_changed`
: Emitted when the query parameters change.

`hash_changed`
: Emitted when the hash changes.

## Methods

`invalidate(exact=False)`
: Invalidates any cached data or forms for this routing context. If `exact` is `True`, then the path and deps must match exactly. By default this is `False`. If `False` then any path or deps that are a subset of path and deps arguments will be invalidated.

`refetch(silent=None)`
: Invalidates the data for this routing context (with exact=True) and then loads the data again. The `silent` value is passed through to `load_data(...)` as a loader argument. For `server_fn` routes, `silent=True` uses `anvil.server.call_s(...)`, `silent=False` uses `anvil.server.call(...)`, and `silent=None` uses the route default. Custom `load_data(...)` implementations can inspect `silent` and choose how to handle loading indicators or silent/background fetches.

`raise_init_events()`
: Raises the `data_loaded`, `data_loading`, `data_error`, `query_changed` and `hash_changed` events.
This method is useful during instantiation of the form. First set up your event handlers, then call `raise_init_events()`.
