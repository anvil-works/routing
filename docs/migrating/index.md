---
weight: 9
---

# Migrating

## From an app that navigates with `anvil.open_form`

Define your routes. If you are not using `params` in any routes, you should be able to replace all calls to `anvil.open_form` with `router.open_form`. To begin with, make sure to set `cached_forms` to `False`. As you decide certain routes should have `params`, you will need to replace `router.open_form` with `router.navigate`. The keyword arguments to `open_form` will be a dictionary you pass to the `form_properties` argument of `navigate`.

A common pitfall will be that a Form could previously rely on the `item` property always being passed to the form. However, this will not be the case if a user navigates directly to the form. In this case, the `item` property will be `None`, and you will have to fetch the item based on the `routing_context`.

## From `anvil_extras.routing` (`HashRouting`)

Define your routes. Each route definition will be similar to the hash routing `@route` decorator.

By default, when a route subclasses from `Route`, the routing library will call `anvil.open_form` on the matching route's form. For hash routing apps, this is not what you want. Instead, you should subclass from `TemplateWithContainerRoute` and set the `template` attribute to the template form.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"


class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"
```

If you have a single template in your hash routing app, then set `BaseRoute.template = "MyTemplate"`.

If you have multiple templates, then you can set the `template` attribute on individual routes. See the section below that elaborates on how to work with multiple templates.

### `set_url_hash`

Instead of calling hash routing's `set_url_hash` method, use the `navigate` function.

Or, if the `set_url_hash` call is inside a `Link`'s click handler, replace the `Link` with a `NavLink`/`Anchor`. Set the `path` and `query` attribute appropriately and remove the click handler.

### `full_width_row`

If the route decorator uses `full_width_row`, you should configure the `Route.template_container_properties` attribute.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"


class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"
    template_container_properties = {"full_width_row": True}
```

If you are using `full_width_row` on all routes then you can set the `full_width_row` attribute on the `Route` class.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"
BaseRoute.template_container_properties = {"full_width_row": True}
```

### Navigation Links

Replace regular HTML links with `NavLink` components. Instead of using click handlers and manually managing navigation, configure the path directly on the component (either in code or in the designer):

```python
from ._anvil_designer import MainTemplate
from routing import router


class Main(MainTemplate):
    def __init__(self, **properties):
        self.nav_home.path = "/home"
        self.nav_settings.path = "/settings"
        self.init_components(**properties)
```

NavLinks provide several advantages:
- Automatic active state management
- Support for ctrl+click to open in new tab
- Native browser link preview behavior
- No need for click handlers
- Improved accessibility


### `on_navigation` callback

In hash routing the `on_navigation` method is called on the Template form when the hash changes. This is often used to update the active nav link in the sidebar. If you are using `Link` components in your sidebar, we recommend replacing these with `NavLink` components (see previous section).

If you want to keep your existing `on_navigation` method, you can achieve this through the `router`'s event system. The `router` will emit a `navigation` event when the url changes.

```python
from ._anvil_designer import MainTemplate
from routing import router


class Main(MainTemplate):
    def __init__(self, **properties):
        self.links = {"/": self.home_nav, "/about": self.about_nav}
        self.init_components(**properties)

    def on_navigate(self, **event_args):
        context = router.get_routing_context()
        for path, link in self.links.items():
            if path == context.path:
                link.role = "selected"
            else:
                link.role = None

    def home_nav_click(self, **event_args):
        router.navigate("/")

    def about_nav_click(self, **event_args):
        router.navigate("/about")

    def form_show(self, **event_args):
        router.add_event_handler("navigate", self.on_navigate)
        self.on_navigate()

    def form_hide(self, **event_args):
        router.remove_event_handler("navigate", self.on_navigate)
```

If you have multiple Templates, we recommend subscribing to the `navigation` event in the `form_show` method of your template form, and unsubscribing in the `form_hide` method. If you only have a single template, you can subscribe to the `navigation` event in the `__init__` method of your template form and there is no need to unsubscribe.

### Using multiple templates, redirects, and other advanced usage

When migrating from anvil_extras, you might have different templates for different parts of your application. For example, you might have:
- A main template with navigation for authenticated users
- A minimal template for authentication pages
- A specialized template for admin sections

You can configure this by setting different templates for different routes. You can also configure redirects and caching settings within each route class. Below is an example with two templates - one for authentication and one for the main app.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute
from routing.router import Redirect
from .Global import Global  # if you have a module for global (cached) variables


class EnsureUserMixin:
    def before_load(self, **loader_args):
        # Runs this method before loading the route form.
        if not Global.user:
            # Redirect if there is no logged in user.
            raise Redirect(path="/signin")


class SigninRoute(BaseRoute):
    template = "Templates.Static"  # Template for auth screen
    path = "/signin"
    form = "Pages.Signin"
    cache_form = True  # Cache settings for this route form.


class SignupRoute(BaseRoute):
    template = "Templates.Static"  # Template for auth screen
    path = "/signup"
    form = "Pages.Signup"
    cache_form = True


class HomeRoute(EnsureUserMixin, BaseRoute):
    # This route and ones below inherits from two classes,
    # which propagates the redirect from EnsureUserMixin
    template = "Templates.Router"  # Main template for app
    path = "/app/home"
    form = "Pages.Home"
    cache_form = True


class SettingsRoute(EnsureUserMixin, BaseRoute):
    template = "Templates.Router"
    path = "/app/settings"
    form = "Pages.Settings"
    cache_form = True


class AdminRoute(EnsureUserMixin, BaseRoute):
    template = "Templates.Router"
    path = "/app/admin"
    form = "Pages.Admin"
    cache_form = True
```

Note that redirects are no longer defined in the startup form, but the routes module. In addition, caching is defined for each route, not as a parameter in the navigation function (anvil_extras `set_url_hash`). Any common attributes and methods can be set on base classes or mix-in classes.
