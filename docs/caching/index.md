# Caching

The routing library provides simple caching mechanisms for forms and data.
By default, the routing library will **NOT** cache any forms or data.

## Form Caching

To override the default behaviour, you can set the `Route.cache_form` attribute to `True`. This will cause the routing library to cache all forms.

```python
from routing.router import Route

Route.cache_form = True
```

You can also set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_form = True
```

## Data Caching

The routing library can cache data loaded by the `load_data` method. If you are not using the `load_data` method, you can skip this section. For more details, see the [Data Loading](/data-loading) section.

You can enable data caching by setting the `cache_data` attribute on the route to `True`.

!!! Caching Forms with data loaders

    If you are using the `load_data` method and `cache_form` is set to `True`, then the `load_data` method will not be called if there is an existing cached form.

## Caching Keys

The routing library will cache forms and data using a cache key. The key is a combination of the path and the dictionary returned by the `cache_deps` method. By default, the `cache_deps` method returns the `query` dictionary.

## Clearing Cache

To clear all cached content, you can call the `clear_cache` function.

```python
from routing import router

router.clear_cache()
```

## Invalidating Cache

If you want to invalidate the cache for a specific path, you can call the `invalidate` function. Invalidating the cache will remove data and forms from the cache.

```python
from routing import router

router.invalidate(path="/articles")
```

The call signature for `invalidate` is:

```python
invalidate(*, path=None, deps=None, exact=False)
invalidate(path, **kws)
invalidate(routing_context, **kws)
```

`path`
: The path to invalidate.

`deps`
: The dependencies to invalidate. These are the same dependencies that are returned by the `cache_deps` method.

`exact`
: If `True`, then the path and deps must match exactly. If `False` (the default), then any path or deps that are a subset of the path and deps arguments will be invalidated.

## Partial Invalidation

```python
from routing.router import Route


class ArticlesRoute(Route):
    path = "/articles"
    form = "Pages.Articles"


class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"
```

In the above example, if you call `invalidate("/articles", exact=True)`, then data and forms associated with the `ArticlesRoute` will be invalidated. If you call `invalidate("/articles", exact=False)`, then data and forms associated with the `ArticlesRoute` and all cached `ArticleRoute` instances will be invalidated, since the `ArticleRoute` path is a subset of the `ArticlesRoute` path.

```python
from routing.router import Route


class ArticlesRoute(Route):
    path = "/articles"
    form = "Pages.Articles"

    def cache_deps(self, **loader_args):
        return {"page": loader_args["query"]["page"]}

    def parse_query(self, query):
        return {**query, "page": int(query.get("page", 1))}
```

In the above example, the data is cached depending on the `page` query parameter. If you call `invalidate("/articles")`, then all data associated with all pages will be invalidated. A deps value of `{"page": 1}` is considered a subset of an empty deps argument. If you call `invalidate("/articles", exact=True)`, then no data will be invalidated, since there is no exact match. Calling `invalidate("/articles", deps={"page": 1})` will invalidate only the data for the first page.

## Invalidating Contexts

A routing context also has an `invalidate` method for convenience.

```python
from routing import router


class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)

    def delete_button_click(self, **event_args):
        self.remove_from_parent()
        self.routing_context.invalidate(exact=True)
```
