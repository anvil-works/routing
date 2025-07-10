---
weight: -9.9
---

# Quick Start

## From a Clone

Clone the following Anvil app: [https://anvil.works/build#clone:34ZTMM7IQRTCMIAD=PPWCEPHZKQ3VYBIEF6T7GWOY](https://anvil.works/build#clone:34ZTMM7IQRTCMIAD=PPWCEPHZKQ3VYBIEF6T7GWOY)

## From a New App

Create a new app.

### Client Code Structure

The client code structure should look like this:

```
- Layouts (Package)
    - Main (Form - ensure you tick "Use as layout")
- Pages (Package)
    - Index (Form choosing Layouts.Main as the layout)
    - About (Form choosing Layouts.Main as the layout)
    - Contact (Form choosing Layouts.Main as the layout)
- routes (Module)
- startup (Module)
```

### Startup Module

```python
# startup.py
from routing.router import launch

if __name__ == "__main__":
    launch()
```

### Routes Module

```python
# routes.py
from routing.router import Route

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"

class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

class ContactRoute(Route):
    path = "/contact"
    form = "Pages.Contact"
```


### Navigation

In `Layouts.Main`, include a `SideBar` and add 3 `NavLink` components.
(The `NavLink` component should come from the routing library)

Ensure the nav links have the following properties set:

-   The first `NavLink` should have `path="/"`.
-   The second `NavLink` should have `path="/about"`.
-   The third `NavLink` should have `path="/contact"`.

Add a title `slot` to the `Layouts.Main` form. Inside `Pages.Index`, add a label component to the title slot with the `text` property set to `"Home"`. Do the same for `Pages.About` and `Pages.Contact`.

You should now be able to navigate using the sidebar nav links.


### Troubleshooting

If your routes aren't working, make sure your file structure is correct. The routes must be defined in the `routes` module.

If you have named the routes module something else, you will need to change the configuration options for the routing library. See the API Reference for more information.

**Preferred:** Set the `routes_module` config option so imports happen automatically.

**Alternatively**, you can explicitly import the routes module in your startup form and server code:

```python
# In a startup module, e.g. startup.py
from . import routes

# In a server module, e.g. ServerRoutes.py
from . import routes
```
