import anvil.server
from anvil.history import history

from ._cached import CACHED_DATA
from ._constants import NO_CACHE
from ._exceptions import Redirect
from ._import_utils import import_form
from ._logger import logger
from ._meta import get_default_meta
from ._navigate import nav_args_to_location, navigate
from ._segments import Segment
from ._utils import encode_query_params, trim_path

sorted_routes = []
LoadAppResponse = None

default_not_found_route_cls = None


def _get_load_app_response():
    global LoadAppResponse

    if LoadAppResponse is not None:
        return LoadAppResponse

    try:
        from anvil.server import LoadAppResponse as LAR
    except ImportError:
        from anvil.server import _LoadAppResponse as LAR

    try:
        LAR(data={}, meta={})
    except TypeError:
        # meta not yet supported
        def LoadAppResponse(data=None, meta=None):
            return LAR(data=data)
    else:
        LoadAppResponse = LAR

    return LoadAppResponse


def _create_server_route(cls):
    # local for now while anvil uplink doesn't have history
    import traceback

    from anvil.history import Location

    from ._context import RoutingContext
    from ._loader import CachedData
    from ._matcher import get_match

    path = cls.path

    if path is None:
        return

    LoadAppResponse = _get_load_app_response()

    # remove on next deploy
    Location.__repr__ = dict.__repr__

    def __str__(self):
        return (
            self.get("path", "")
            + (self.get("search", "") or "")
            + (self.get("hash", "") or "")
        )

    Location.__str__ = __str__

    @anvil.server.route(path)
    def route_handler(*args, **kwargs):
        request = anvil.server.request
        path = request.path
        search = encode_query_params(request.query_params)
        location = Location(path=path, search=search, key="default")
        match = get_match(location=location)
        logger.debug(f"serving route from the server: {location}")
        if match is None:
            # this shouldn't happen
            raise Exception(f"No match for '{location}'")

        route = match.route
        context = RoutingContext(match=match)

        try:
            route.before_load(**context._loader_args)
        except Redirect as r:
            location = nav_args_to_location(
                path=r.path,
                query=r.query,
                params=r.params,
                hash=r.hash,
            )
            logger.debug(f"redirecting to {location}")
            url = location.get_url(True)
            return anvil.server.HttpResponse(status=302, headers={"Location": url})
        except Exception as e:
            # TODO: handle error on the client
            logger.error(
                f"{location}: error serving route from the server: {e!r}\n"
                f"{traceback.format_exc()}"
            )
            return LoadAppResponse(data={"cache": CACHED_DATA})

        try:
            meta = route.meta(**context._loader_args)
        except Exception as e:
            logger.error(
                f"error getting meta data for {location}: got {e!r}\n"
                f"{traceback.format_exc()}"
            )
            meta = None

        try:
            data = route.load_data(**context._loader_args)
        except Exception as e:
            logger.error(
                f"error loading data for {location}, got {e!r}\n"
                f"{traceback.format_exc()}"
            )
            # TODO: handle error on the client
            return LoadAppResponse(data={"cache": CACHED_DATA}, meta=meta)

        mode = route.cache_data
        gc_time = route.gc_time
        cached_data = CachedData(
            data=data, location=location, mode=mode, gc_time=gc_time
        )
        CACHED_DATA[match.key] = cached_data

        return LoadAppResponse(data={"cache": CACHED_DATA}, meta=meta)


class Route:
    path = None
    segments = []
    form = None
    error_form = None
    not_found_form = None
    pending_form = None
    pending_delay = 1
    pending_min = 0.5
    cache_data = NO_CACHE
    stale_time = 0
    cache_form = False
    server_fn = None
    server_silent = False
    gc_time = 30 * 60
    default_not_found = False

    @classmethod
    def create(cls, *, path=None, form=None, server_fn=None, **props):
        name = f"{form or 'CreatedRoute'}Route"
        cls_dict = {"path": path, "form": form, "server_fn": server_fn}
        for key, value in props.items():
            if callable(value):
                cls_dict[key] = staticmethod(value)
            else:
                cls_dict[key] = value

        return type(name, (cls,), cls_dict)

    def before_load(self, **loader_args):
        pass

    def cache_deps(self, **loader_args):
        return loader_args["query"]

    def load_data(self, **loader_args):
        return None

    def meta(self, **loader_args):
        return get_default_meta()

    def parse_params(self, params):
        return params

    def load_form(self, form, routing_context):
        return anvil.open_form(
            form, routing_context=routing_context, **routing_context.form_properties
        )

    def get_template(self, **loader_args):
        return None

    def parse_query(self, query):
        return query

    @classmethod
    def set_default_not_found(cls, not_found_route):
        global default_not_found_route_cls
        if issubclass(not_found_route, Route):
            assert not_found_route.path is None, "not_found_route must not set a path"
            default_not_found_route_cls = not_found_route
        else:
            raise TypeError(
                f"not_found_route must be a Route subclass, got {not_found_route}"
            )

    # def prepare_query(self, query):
    #     return query

    def __init_subclass__(cls) -> None:
        if cls.__dict__.get("default_not_found"):
            cls.set_default_not_found(cls)

        if cls.path is None:
            return

        if not isinstance(cls.path, str):
            raise TypeError("path must be a string")

        trimmed_path = trim_path(cls.path)
        cls.segments = Segment.from_path(trimmed_path)
        if trimmed_path.startswith("."):
            raise ValueError("Route path cannot be relative")

        if not trimmed_path.startswith("/"):
            cls.path = "/" + trimmed_path
        else:
            cls.path = trimmed_path

        sorted_routes.append(cls())

        server_fn = cls.__dict__.get("server_fn")
        existing_loader = cls.__dict__.get("load_data")
        if server_fn is not None and existing_loader is None:

            def load_data(self, **loader_args):
                if self.server_silent:
                    return anvil.server.call_s(server_fn, **loader_args)
                else:
                    return anvil.server.call(server_fn, **loader_args)

            cls.load_data = load_data

        if anvil.is_server_side():
            _create_server_route(cls)


def open_form(form, **form_properties):
    if anvil.is_server_side():
        raise RuntimeError("open_form is not available on the server")

    if not isinstance(form, str):
        raise TypeError("form must be a string")

    for route in sorted_routes:
        if route.form != form:
            continue

        if any(segment.is_param() for segment in route.segments):
            raise ValueError(
                f"Tried to call open_form with {form} but {route.path} requires path params"
            )

        return navigate(path=route.path, form_properties=form_properties)

    raise ValueError(f"No route found for form {form}")


class TemplateWithContainerRoute(Route):
    template = None
    template_container = "content_panel"
    template_container_properties = {}

    def load_form(self, form, routing_context):
        location = history.location
        key = location.key

        def is_stale():
            return key != history.location.key

        template = self.template

        if isinstance(template, str):
            template_form_name = template.split(".").pop()
            if type(anvil.get_open_form()).__name__ == template_form_name:
                template = anvil.get_open_form()

        template_form = import_form(template)

        if template_form is not anvil.get_open_form() and not is_stale():
            anvil.open_form(template_form)

        form = import_form(
            form, routing_context=routing_context, **routing_context.form_properties
        )

        if is_stale():
            return form

        container = getattr(template, self.template_container)
        container.clear()
        container.add_component(form, **self.template_container_properties)

        return form
