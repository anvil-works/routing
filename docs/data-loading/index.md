# Data Loading

The `load_data` method allows data to be sent from the server during the initial page request, rather than loading data during form instantiation.

Most apps will not need to use the `load_data` method and will load data during the form's instantiation or pass data through form properties. Many of the advantages of data loading can be achieved by using [cached forms](/caching#form-caching).

## Limitations

* Since the routing library takes advantage of client-side routing after the initial page request, the advantages of data loading are limited to the first page request.
* Data caching is determined by the `path` and the dictionary returned by the `cache_deps` method. If your App needs to share data between routes, you may find that data caching is not sufficient and results in duplicate data being loaded. You can mitigate duplicate data by using `form_properties` or `nav_context` for simple data sharing.

## Example

**Without a load_data method**

```python
# routes.py
from routing.router import Route

Route.cache_form = True


class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"
```

```python
from routing import router


class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        if properties.get("item") is None:
            # The user navigated directly to the form by changing the URL
            properties["item"] = anvil.server.call(
                "get_article", routing_context.params["id"]
            )

        self.init_components(**properties)
```

In the above example, if a user goes directly to the URL `/articles/123`, the initial page request will send the user to the `ArticleForm`, but there will be no data. The App will then need to make a server call to get the data.

Note that during normal navigation, i.e. when the user clicks a link, we can take advantage of the `form_properties` attribute to ensure we do not load unnecessary data.

```python
class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def on_button_click(self, **event_args):
        router.navigate(
            path="/articles/:id",
            params={"id": self.item["id"]},
            form_properties={"item": self.item},
        )
```

**With a load_data method**

```python
# routes.py
from routing.router import Route


class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"

    def load_data(self, **loader_args):
        row = loader_args["nav_context"].get("row")
        if row is None:
            id = loader_args["path_params"]["id"]
            row = anvil.server.call("get_row", id)
        return row
```

```python
from routing import router


class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        properties["item"] = routing_context.data
        self.init_components(**properties)
```

In the above example, the `load_data` is called whenever the user navigates. If a user navigates directly to the URL `/articles/123`, the initial page request will come in, the load_data method will be called (on the server), and the user will be directed to the `ArticleForm` with the data already loaded. During normal navigation, i.e. when the user clicks a link, we can take advantage of the `nav_context` (or `form_properties`) attribute to ensure we do not make unnecessary server calls during client-side navigation.

```python
class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def on_button_click(self, **event_args):
        router.navigate(
            path="/articles/:id",
            params={"id": self.item["id"]},
            nav_context={"row": self.item},
        )
```

## Invalidating Data

See [Invalidating Cache](/caching#invalidating-cache).

## Pending Form

When data is loading for the first time, a user can provide a loading form. This form will be shown while the data is loading.

The pending form is determined by the `Route.pending_form` attribute. When the data is loading, the routing library will wait for the `pending_delay` seconds before showing the pending form. It will show the pending form for at least `pending_min` seconds.

```python
from routing.router import Route


class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"
    pending_form = "Pages.Loading"
    pending_delay = 1  # default is 1
    pending_min = 0.5  # default is 0.5
```

A common implementation will be to create a pending form with the same layout as the form. Where the content would be, place an `Anvil.Spacer` component. Inside the `show` and `hide` event handlers, call the `anvil.server.loading_indicator.start` and `anvil.server.loading_indicator.stop` functions.

```python
from anvil.server import loading_indicator


class LoadingForm(LoadingFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.loading_indicator = anvil.server.loading_indicator(self.spacer_1)

    def show(self, **event_args):
        self.loading_indicator.start()

    def hide(self, **event_args):
        self.loading_indicator.stop()
```
