# Theme

When creating a custom theme for your Anvil app, you may want to implement your own components for the `NavLink` and `Anchor` base classes.

## Default NavLink and Anchor Components

The default implementations for the `NavLink` and `Anchor` base classes are as follows:

```python
import anvil


class NavLinkBase(anvil.Link):
    def __init__(self, active=None, **properties):
        self._props = properties
        super().__init__(**properties)

    @property
    def active(self):
        return self._props.get("active")

    @active.setter
    def active(self, value):
        self._props["active"] = value
        self.role = "selected" if value else None


class AnchorBase(anvil.Link):
    pass
```

## Customising the NavLink and Anchor Components

To configure the routing library to use your custom base classes, follow these steps:

1. Create a preload module in your project:

        # preload module: _preload.py
        import anvil
        from ...MyNavLink import MyNavLink
        from ...MyAnchor import MyAnchor

        anvil.pluggable_ui.provide(
            "MY_PACKAGE_NAME", {"routing.NavLink": MyNavLink, "routing.Anchor": MyAnchor}
        )


2. Configure the client initialisation module:

    The client initialisation module runs when the client starts up. As there is currently no way to set this through the Anvil editor, you'll need to modify your `anvil.yaml` file locally by adding:

        client_init_module: _preload

!!! Note

    If multiple themes define `NavLink` and `Anchor` base classes, the most recently loaded theme's implementations will take precedence.

## Supported Themes

Currently supported themes include:

-   M3
