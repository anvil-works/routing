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

For existing HTML/DOM links, you can use `register_links()` to enable client-side routing without creating NavLink or Anchor components.

### Usage

```python
from routing import router

# In your form's __init__ or show event:
router.register_links(self.dom_nodes["header"])
```

### Features

- **Auto-detection**: Automatically detects if elements are `<a>` tags or containers
- **Flexible**: Works with individual links, containers, or a mix of both
- **Customizable**: Use custom CSS selectors to target specific links
- **Idempotent**: Safe to call multiple times on the same elements

### Examples

**Register a container** (finds all internal links):
```python
router.register_links(self.dom_nodes["header"])
```

**Register multiple containers**:
```python
router.register_links(
    self.dom_nodes["header"],
    self.dom_nodes["footer"]
)
```

**Register specific links directly** (auto-detected as `<a>` tags):
```python
router.register_links(
    self.dom_nodes["pricing-link"],
    self.dom_nodes["faq-link"]
)
```

**Mix containers and direct links**:
```python
router.register_links(
    self.dom_nodes["header"],        # container
    self.dom_nodes["special-link"]   # direct link
)
```

**Custom selector for containers**:
```python
router.register_links(
    self.dom_nodes["nav"],
    selector="a.internal-link, button[data-route]"
)
```

### Parameters

`*dom_nodes`
: DOM elements (links or containers) to register for routing

`selector`
: CSS selector for finding links in containers. Default: `"a[href^='/']"` (all internal links)

### Behavior

- For `<a>` tags: Registers them directly as navigation links
- For containers: Searches within using the selector
- Click handling:
    - Prevents default browser navigation
    - Respects modifier keys (Ctrl/Cmd/Shift) - lets browser handle
    - Uses router's navigation for client-side routing

### Comparison with NavLink

| Feature | `register_links()` | `NavLink` Component |
|---------|-------------------|---------------------|
| Use case | Existing HTML/DOM | Anvil components |
| Active state | ❌ No | ✅ Yes |
| Setup | One function call | Per-link component |
| Flexibility | High (any DOM) | Component-based |
| Path params | From href only | Full support |
| Query params | From href only | Full support |
