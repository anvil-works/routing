## Redirecting

You can redirect to a different route by raising a `Redirect` exception in a route's `before_load` method.

```python
from routing.router import Route, Redirect


class IndexRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        raise Redirect(path="/dashboard")
```

In the above example, the user will be redirected to the `/dashboard` route when they navigate to your app.

A common use case for redirecting is to ensure that a user is logged in before navigating to a route.

```python
from routing.router import Route, Redirect
import anvil.users


class IndexRoute(Route):
    path = "/"

    def before_load(self, **loader_args):
        if anvil.users.get_user():
            raise Redirect(path="/dashboard")
        else:
            raise Redirect(path="/login")


class EnsureUserMixin:
    def before_load(self, **loader_args):
        if not anvil.users.get_user():
            # Note this will make a server call
            # so you may want to cache the call to anvil.users.get_user()
            raise Redirect(path="/login")


class DashboardRoute(EnsureUserMixin, Route):
    path = "/dashboard"
    form = "Pages.Dashboard"
```

!!! note

    A determined user will be able to bypass the redirect by opening the form directly.
    Always ensure you check the user is logged in on the server before sending sensitive data to the client.
