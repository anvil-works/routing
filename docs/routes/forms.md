## Forms

The `Route.load_form` method is called when the route is matched. The default implementation will call `anvil.open_form` on the matching route's form.

```python
class Route:
    def load_form(self, form, routing_context):
        return anvil.open_form(
            form, routing_context=routing_context, **routing_context.form_properties
        )
```

This method will be called with the form attribute (e.g. `"Pages.Index"`) or, if you are using cached forms, the cached form instance.

### `open_form` Alternative

If you are using traditional routing in your Anvil app, you may have a template with a `content_panel`, and during navigation, you clear the content panel and then add the new form to the panel.

If you want to use this style of routing, the routing library provides a `TemplateWithContainerRoute` class. This class overrides the `load_form` method.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"


class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"
```

In this case, the `load_form` method will call `anvil.open_form` on the template form (if it is not already the current open form). It will then instantiate the form, clear the `content_panel` of the template, and add the form to the panel.

If you are using something other than `content_panel`, you can set the `template_container` attribute to the container name.

You can also set the `template_container_properties` attribute to a dictionary of container properties. This is useful if you want to set the `full_width_row` attribute.

```python
from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"
BaseRoute.template_container = "content_panel"
BaseRoute.template_container_properties = {"full_width_row": True}


class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"
```
