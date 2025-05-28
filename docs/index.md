# Overview

Routing lets you configure URL paths to allow your users to navigate to specific parts and states of your app directly through their browser's address bar.

In general, this brings your app closer to a regular web page in terms of usage standards. For example, this can be useful for letting users bookmark specific parts of your app, or enabling usage of the back and forward buttons to navigate throughout your app.

## Routing Basics

A route is an object with, among other attributes, a URL path, and a form to open when navigating to this route.

As an app developer, you will need to define routes for your app.
When the URL changes, the router will look for a matching route.
The ultimate goal is to open the form associated with the given URL.

The router will attempt to match routes in the order they are defined.

When a route is found, the router will call the route's `before_load` method.
- If the `before_load` method raises a `Redirect`, the router will navigate to the redirected URL.
- If the `before_load` method returns a dictionary, its contents will be merged into the navigation context (`nav_context`) for the route.

If the route has a `load_data` method, it will be called, and the return value will be available as the `data` property on the `RoutingContext`.

Once the `load_data` method has been called, the router will call the route's `load_form` method. A `routing_context` will be passed to this method. By default, the `load_form` method will call `anvil.open_form` on the matching route's form, with `routing_context` passed as a keyword argument.

## Caching

There are two types of caching: form caching and data caching.

If a form is cached, instead of creating a new instance, the router will call the route's `load_form` method with the cached form instance.

If data is cached, the router will only call the `load_data` method if the data is stale. See the [Caching](/caching) section for more details.

## Server vs Client Routing

Should the user open the app directly through a URL as their initial page request, the routing process will occur entirely on the server. Otherwise, if the user is navigating from within the app, the process occurs on the client.
