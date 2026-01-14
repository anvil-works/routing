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

If your routes aren't working, make sure your file structure is correct.

The router **automatically imports** a module named `routes` by default — you do not need to manually import it. Just define your routes in a `routes` module and they will be discovered automatically.

If you have named the routes module something else, set the `routes_module` config option to the correct module name. See the [API Reference](./api-reference.md#routes_module) for more information.
