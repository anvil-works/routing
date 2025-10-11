# Navigation Components

A Navigation Component is useful over a Button with a click handler because it supports `Ctrl/Cmd` clicking a route to open in a new tab and should provide the correct href value for the browser.

The routing library provides two Navigation Components:

-   [NavLink](#navlink)
-   [Anchor](#anchor)

Navigation Components by default are subclasses of the `Anvil.Link` component. However, this can be customised. See [Themes](/theme) for details.

## NavLink

The NavLink component is a link that you will likely use in your main layout's sidebar. The routing library will set the `active` property on the NavLink to `True` when the NavLink's properties match the current routing context.

If you are using the default NavLink component, then `active` means it will set its `role` property to `active`. If the NavLink component is not the default, then how the `active` property behaves is determined by the Base class of the NavLink component.

### Navigation Attributes

`path`
: The path to navigate to. e.g. `/articles/123` or `/articles` or `/articles/:id`. The path can be relative `./`. If not set, then the path will be the current path.

`params`
: The params for the path. e.g. `{"id": 123}`

`query`
: The query parameters to navigate to. e.g. `{"tab": "income"}`. This can be a function that takes the current query parameters as an argument and returns the new query parameters.

`form_properties`
: The form properties to pass to the form when it is opened.

`nav_context`
: The nav context for this navigation.

`hash`
: The hash to navigate to.

!!! Tip

    If you want to set `params` or `query` in the designer, you can use the data binding feature of the designer.

    ![Data Binding](/img/screenshots/data-binding.png)

### Active State

`active`
: The active state of the NavLink. You probably don't want to set this. The routing library will set it to `True` when the NavLink's properties match the current routing context.

`exact_path`
: If `True`, then the path must match exactly. By default, this is `False`. This means a NavLink with a path of `/articles` will match the path `/articles`, `/articles/123` and `/articles/123/456`.

`exact_query`
: If `True`, then the query must inclusively match the current routing context's query. By default, this is `False`.

`exact_hash`
: If `True`, then the hash must match exactly. By default, this is `False`.

You can set most properties in code or in the designer. In the designer, it is recommended to set `query` properties by using data bindings.

## Anchor

Anchor is a link that you can use inline or as a container for other components. Unlike the NavLink, the Anchor component has no `active` property.

## register_links()

For existing HTML/DOM links, you can use `register_links()` to enable client-side routing with active state tracking without creating NavLink or Anchor components.

### Why Use This?

Use `register_links()` when you have navigation links defined in an HTML template component. Instead of manually creating a NavLink component for each link, you can register all links in your HTML with a single function call.

### Usage

**Automatic lifecycle management** (recommended):
```python
from routing import router

class MainLayout(MainLayoutTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        # Register links tied to component lifecycle
        router.register_links(
            self.dom_nodes["header"],
            active_class="active",
            component=self  # Auto setup on page added, cleanup on page removed
        )
```

**Manual cleanup**:
```python
class MainLayout(MainLayoutTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._cleanup_links = None

    def form_show(self, **event_args):
        # Register links and store cleanup function
        self._cleanup_links = router.register_links(
            self.dom_nodes["header"],
            active_class="active"
        )

    def form_hide(self, **event_args):
        # Manually call cleanup when form is hidden
        if self._cleanup_links:
            self._cleanup_links()
            self._cleanup_links = None
```

**Register all links in the entire component**:
```python
def form_show(self, **event_args):
    # Register ALL internal links in this component's HTML
    self._cleanup_links = router.register_links(
        self,  # The component itself
        active_class="active"
    )
```

This will find all `<a href="/...">` links in your HTML template and enable routing for them.

### Features

- **Auto-detection**: Automatically detects if elements are `<a>` tags or containers
- **Active state tracking**: Links automatically receive active styling when they match the current route
- **Flexible styling**: Use CSS classes or custom callbacks for active state
- **Cleanup function**: Returns a function to unregister and clean up event listeners
- **Exact matching**: Support for `exact_path`, `exact_query`, and `exact_hash` options
- **Customizable**: Use custom CSS selectors to target specific links
- **Idempotent**: Safe to call multiple times on the same elements

### Examples

**Basic usage with active class**:
```python
cleanup = router.register_links(
    self.dom_nodes["nav"],
    active_class="active"  # CSS class added to matching links
)
```

**Custom active state callback**:
```python
def style_active_link(element, is_active):
    if is_active:
        element.style.fontWeight = "bold"
        element.style.color = "#007bff"
    else:
        element.style.fontWeight = "normal"
        element.style.color = ""

cleanup = router.register_links(
    self.dom_nodes["nav"],
    active_callback=style_active_link
)
```

**Exact path matching** (for breadcrumbs):
```python
cleanup = router.register_links(
    self.dom_nodes["breadcrumbs"],
    active_class="current",
    exact_path=True  # Only active if path matches exactly
)
```

**Register specific link elements directly**:
```python
# Register individual <a> tag dom_nodes
cleanup = router.register_links(
    self.dom_nodes["home_link"],
    self.dom_nodes["about_link"],
    self.dom_nodes["contact_link"],
    active_class="active"
)
```

**Register multiple containers**:
```python
cleanup = router.register_links(
    self.dom_nodes["header"],
    self.dom_nodes["footer"],
    active_class="active"
)
```

**Custom selector to target specific links**:
```python
# Only register links with a specific class
cleanup = router.register_links(
    self.dom_nodes["nav"],
    selector="a.nav-link",  # Only <a> tags with class="nav-link"
    active_class="active"
)

# Or target links by attribute
cleanup = router.register_links(
    self,
    selector="a[data-route]",  # Only <a> tags with data-route attribute
    active_class="active"
)
```

**Fire and forget** (for persistent sidebars that never hide):
```python
# No need to store cleanup if form never hides
router.register_links(
    self.dom_nodes["sidebar"],
    active_class="active"
)
```

### Parameters

`*dom_nodes`
: DOM elements (links or containers) to register for routing

`selector`
: CSS selector for finding links in containers. Default: `"a[href^='/']"` (all internal links)

`active_class`
: CSS class to add/remove when link matches current route. Default: `"active"`

`active_callback`
: Custom callback `function(element, is_active)` for styling. Overrides `active_class` if provided

`exact_path`
: If `True`, path must match exactly. Default: `False` (parent paths also match)

`exact_query`
: If `True`, query parameters must match exactly. Default: `False`

`exact_hash`
: If `True`, hash must match exactly. Default: `False`

`component`
: Anvil component to tie lifecycle to (auto setup on page added, cleanup on page removed). Default: `None`

**Returns**: Cleanup function to unregister links and remove event listeners (or `None` if `component` is used)

### Behavior

- For `<a>` tags: Registers them directly as navigation links
- For containers: Searches within using the selector
- Click handling:
    - Prevents default browser navigation
    - Respects modifier keys (Ctrl/Cmd/Shift) - lets browser handle
    - Uses router's navigation for client-side routing
- Active state:
    - Updates automatically on every navigation
    - Uses same matching logic as `NavLink` component
    - Applies CSS class or calls custom callback

### Cleanup

The returned cleanup function should be called when:
- The form is hidden (in the `hide` event handler)
- The form is removed from the page
- You want to unregister the links

The cleanup function:
- Removes navigation event listeners
- Clears active state from all registered links
- Prevents memory leaks

### Comparison with NavLink

| Feature | `register_links()` | `NavLink` Component |
|---------|-------------------|---------------------|
| Use case | Existing HTML/DOM | Anvil components |
| Active state | ✅ Yes (CSS class or callback) | ✅ Yes (component property) |
| Setup | One function call | Per-link component |
| Flexibility | High (any DOM) | Component-based |
| Path params | From href only | Full support |
| Query params | From href only | Full support |
| Cleanup | Manual (via returned function) | Automatic |
| Exact matching | ✅ Yes | ✅ Yes |
