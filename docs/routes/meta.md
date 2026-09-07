# Route Meta Method

The `meta` method on a `Route` class allows you to dynamically set the meta tags for each page, such as the title, description, Open Graph tags, and images. This is useful for SEO, social sharing, and customizing how your app appears in search engines and link previews.

## Defining Meta Tags

Override the `meta` method in your route class to return a dictionary of meta tags. Standard tags (like `title` or `description`) will be rendered as `<meta name="...">` tags, while Open Graph tags (such as `og:title` or `og:image`) will be rendered as `<meta property="...">` tags in the HTML.

### Basic Example

```python
from routing import Route


class ProductRoute(Route):
    path = "/product"
    form = "Pages.Product"

    def meta(self, **kwargs):
        meta_data = {}
        meta_data["title"] = "Product Page"
        meta_data["description"] = (
            "Details and specifications for our featured product."
        )
        meta_data["og:title"] = "Featured Product"
        meta_data["og:description"] = "Learn more about our latest product release."
        meta_data["og:image"] = "asset:product.jpeg"  # Use a theme asset
        return meta_data
```

### Using `get_app_origin()` for Absolute URLs

If you want to provide an absolute URL for Open Graph images (recommended for social sharing), you can use the `get_app_origin()` utility:

```python
from routing import Route, get_app_origin


class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

    def meta(self, **kwargs):
        origin = get_app_origin()
        meta_data = {
            "title": "About Us",
            "description": "Information about our company and team.",
            "og:title": "About Our Company",
            "og:description": "Discover our mission, values, and team members.",
            "og:image": f"{origin}/_/theme/about.jpeg",  # Absolute URL
        }
        return meta_data
```

## Notes

-   All meta tags will be injected into the page as `<meta ...>` tags, except for `title`, which will be used for both the `<title>` tag and a `<meta name="title">` tag.
-   You can set any meta tag supported by your app or required by social platforms. Arbitrary meta tags are supported (e.g., Twitter cards `twitter:card`, `twitter:image`).
-   If a meta value starts with `asset:`, such as `asset:foo.jpeg`, it will use the corresponding URL for an asset in your app’s Assets or theme assets folder.
-   For absolute URLs, use `get_app_origin()` to construct the full URL.
-   If a route does not define a particular meta tag, the value from a default or previously set meta tag may be used. For consistency and to avoid unexpected results, it’s recommended to explicitly define all relevant meta tags for each route.

### Example: Adding Twitter Card Tags

```python
class BlogPostRoute(Route):
    path = "/blog/post"
    form = "Pages.BlogPost"

    def meta(self, **kwargs):
        meta_data = {
            "title": "Blog Post Title",
            "description": "A summary of the blog post.",
            "twitter:card": "summary_large_image",
            "twitter:title": "Blog Post Title",
            "twitter:description": "A summary of the blog post.",
            "twitter:image": "asset:blogpost.jpeg",  # Uses an app asset
        }
        return meta_data
```

---

For more details on available meta tags and advanced usage, see the [SEO & Meta Tags guide](../seo.md) or the [Route class documentation](./index.md).
