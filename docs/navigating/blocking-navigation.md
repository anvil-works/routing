---
weight: 10
---

# Blocking Navigation

You may want to prevent the user from navigating away from a page, for example, if they are editing a form.

```python
from routing.router import RoutingContext, navigate

class EditForm(EditFormTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.routing_context = routing_context
        self.routing_context.register_blocker(self.prevent_navigation)
        self.init_components(**properties)

    def prevent_navigation(self, **event_args):
        c = confirm("Are you sure you want to leave this page? Your changes will be lost.")
        return not c

    def save_button_click(self, **event_args):
        self.routing_context.unregister_blocker(self.prevent_navigation)
        navigate(path="/dashboard")
```

!!! note

    When you register a blocker, if a user navigates to another website, the browser dialogue asking if they want to leave the current page will be shown.

Alternatively, you can use the `NavigationBlocker` context manager.

```python
from routing.router import NavigationBlocker

class Form(FormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def run_important_alert(self, **event_args):
        with NavigationBlocker(warn_before_unload=True):
            alert("Important Alert", dismissible=False)
```

The above navigation blocker will prevent the user from navigating away from the page while the alert is open.
`warn_before_unload` will show the browser dialogue asking if the user wants to leave the page if they navigate to a new website. By default, this is `False`.

## Alerts

The `alert` and `confirm` functions are provided by the routing library. These functions behave similarly to Anvil's default `alert` and `confirm` functions, but they will block navigation when `dismissible` is `True`, or close the alert when the user navigates to a new page.

You can override the default `alert` and `confirm` functions by setting the `anvil.alert` and `anvil.confirm` attributes in your startup module.

```python
# startup.py
import anvil
from routing import router

anvil.alert = router.alert
anvil.confirm = router.confirm

if __name__ == "__main__":
    router.launch()
```
