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

The routing library can cache data loaded by the `load_data` method. If you are not using the `load_data` method, you can skip this section. For more details, see the [Data Loading](../data-loading/index.md) section.

Set `cache_data` to one of the constants exported by `routing.router`:

| Policy | Behaviour when navigation needs data |
| --- | --- |
| `NO_CACHE` (`False`, default) | Load data without retaining it for later navigation. Initial data sent by the server is still used once. |
| `CACHE_FIRST` (`True`) | Reuse cached data until it is invalidated or garbage-collected. |
| `NETWORK_FIRST` | Load again, retaining cached data as a fallback after offline retries. |
| `STALE_WHILE_REVALIDATE` | Return cached data immediately and refresh it in the background when stale. |

For `STALE_WHILE_REVALIDATE`, `stale_time` sets the freshness period in seconds and defaults to `0`. `gc_time` defaults to 30 minutes and controls when navigation can remove old cached data and any form with the same cache key.

```python
from routing.router import Route, STALE_WHILE_REVALIDATE

class ArticlesRoute(Route):
    path = "/articles"
    form = "Pages.Articles"
    cache_data = STALE_WHILE_REVALIDATE
    stale_time = 60
```

Forms that display refreshing data should handle the routing context's `data_loaded` and `data_error` events. Register handlers before calling `raise_init_events()`, and use `revalidating` to check for an active refresh. See [Routing context](../routing-context/index.md).

!!! Caching Forms with data loaders

    If you are using the `load_data` method and `cache_form` is set to `True`, then the `load_data` method will not be called if there is an existing cached form.

## Caching Keys

The routing library will cache forms and data using a cache key. The key combines the concrete URL path, such as `/articles/123`, and the dictionary returned by `cache_deps`. By default, the `cache_deps` method returns the `query` dictionary.

## Clearing Cache

To clear all cached content, you can call the `clear_cache` function.

```python
from routing import router
router.clear_cache()
```

## Invalidating Cache

If you want to invalidate the cache for a specific path, you can call the `invalidate` function. Invalidation removes matching cached forms. It also removes matching data, except for `STALE_WHILE_REVALIDATE` data, which is kept and marked stale for the next load. Invalidation alone does not navigate or refresh the displayed form. Use the current routing context's `refetch()` to reload its data immediately.

```python
from routing import router
router.invalidate(path="/articles")
```

The call signature for `invalidate` is:

```text
invalidate(*, path=None, deps=None, exact=False)
invalidate(path, **kws)
invalidate(routing_context, **kws)
```

`path`
: The path to invalidate.

`deps`
: The dependencies to invalidate. These are the same dependencies that are returned by the `cache_deps` method.

`exact`
: If `True`, then the path and deps must match exactly. If `False` (the default), the path matches itself and its descendants. Cached dependencies must contain all entries supplied in `deps`; omitted dependencies do not restrict the match.

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

In the above example, if you call `invalidate("/articles", exact=True)`, then data and forms associated with the `ArticlesRoute` will be invalidated. If you call `invalidate("/articles", exact=False)`, then data and forms associated with the `ArticlesRoute` and all cached `ArticleRoute` instances will be invalidated, because concrete paths such as `/articles/123` are descendants of `/articles`.

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

In the above example, the data is cached depending on the `page` query parameter. If you call `invalidate("/articles")`, then all data associated with all pages will be invalidated. Omitting `deps` imposes no dependency filter. If you call `invalidate("/articles", exact=True)`, then no data will be invalidated, since there is no exact match. Calling `invalidate("/articles", deps={"page": 1})` will invalidate only the data for the first page.

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
