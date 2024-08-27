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

    Adding the `RoutingContext` type definition will allow anvil to show autocompletion for the `routing_context` property.

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

: The dependencies `dict` returned by the `loader_deps` method.

`nav_context`

: The navigation context for the current route. This is a `dict` and can be set by passing a `nav_context` argument to the `navigate` method. (Or equivalently by setting the `nav_context` attribute on a `NavLink`/`Anchor` component).

`form_properties`

: The form properties for the current route. This is a `dict` and can be set by passing a `form_properties` argument to the `navigate` method. (Or equivalently by setting the `form_properties` attribute on the `NavLink`/`Anchor` component). Note the `form_properties` are passed as keyword arguments when instantiating a form. For more details see the Navigation section.

`error`

: The error that occurred when loading the data, or the current route. This is particularly useful when displaying error messages in your error form.

`data`

: The data for the current route. This is the value returned from the `loader` method.

<!-- `match`

: The `Match` instance for the current route.

`location`

: The `Location` instance for the current route.

`route`

: The `Route` instance for the current route. -->

## Events

<!-- TODO determine if we should raise these events after form show e.g. should the query change event be fired after the form is shown -->

The `RoutingContext` instance will emit events when the route changes.

`data_loading`

: Emitted when the data is loading.

`data_loaded`

: Emitted when the data has been loaded.

`data_error`

: Emitted when the data has an error.

`query_changed`

: Emitted when the query parameters change.

`hash_changed`

: Emitted when the hash changes.