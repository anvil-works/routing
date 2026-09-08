# Route meta

Override a route's `meta` method to return a dictionary of page metadata. The router calls it before loading data, so use its loader arguments rather than relying on `routing_context.data`.

```python
from routing.router import Route

class ProductRoute(Route):
    path = "/product"
    form = "Pages.Product"

    def meta(self, **loader_args):
        return {
            "title": "Product page",
            "description": "Details and specifications for our product.",
            "og:image": "asset:product.jpeg",
            "twitter:card": "summary_large_image",
        }
```

## Asset URLs

Use `asset:product.jpeg` to refer to an app theme asset. To construct an absolute URL yourself, use `anvil.server.get_app_origin()`:

```python
import anvil.server
from routing.router import Route

class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

    def meta(self, **loader_args):
        origin = anvil.server.get_app_origin()
        return {
            "title": "About us",
            "description": "Information about our company and team.",
            "og:image": f"{origin}/_/theme/about.jpeg",
        }
```

## Client and server behaviour

On a direct URL request, the router passes the metadata to Anvil's `AppResponder`, which controls the initial response's metadata. On client navigation, the router updates the document's `<title>` and writes metadata as `<meta name="..." content="...">` elements, including Open Graph names such as `og:image`.

The client supports arbitrary names, including Twitter card tags. A tag appearing after client navigation does not establish that it is present in the initial HTML read by a social preview crawler. Check the initial response when validating previews.

## Defaults

The base `Route.meta` method returns `{}`. On the client:

- `title` updates both `<title>` and `<meta name="title">`.
- `og:title` and `og:description` use `title` and `description` when those values are supplied without their Open Graph equivalents.
- When a tag is omitted, the current implementation restores the value captured before its most recent explicit update. This can restore metadata from an earlier route, so explicitly supply values that must be consistent across navigation. A newly created tag starts with an empty value.

See the [Route class](index.md) for the rest of the route lifecycle.
