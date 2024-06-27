import anvil.server

from ._navigate import nav_args_to_location
from ._exceptions import Redirect

from ._segments import Segment
from ._utils import trim_path, encode_search_params
from ._constants import STALE_WHILE_REVALIDATE, NETWORK_FIRST


sorted_routes = []


def _create_server_route(cls):
    # local for now while anvil uplink doesn't have history
    from anvil.history import Location
    from ._loader import load_data, cache, CachedData
    from ._matcher import get_match

    path = cls.path

    if path is None:
        return

    # print("registering route", "/" + path, cls.form)

    @anvil.server.route("/" + path)
    def route_handler(*args, **kwargs):
        request = anvil.server.request
        path = request.path
        search = encode_search_params(request.query_params)
        location = Location(path=path, search=search, key="default")
        match = get_match(location=location)
        if match is None:
            raise Exception("No match")

        route = match.route
        search_params = match.search_params
        path_params = match.path_params
        deps = match.deps

        try:
            route.before_load()
        except Redirect as r:
            location = nav_args_to_location(**r.__dict__)
            url = (
                anvil.server.get_app_origin()
                + location.path
                + location.search
                + location.hash
            )
            return anvil.server.HttpResponse(status=302, headers={"Location": url})

        data = route.loader(
            location=location,
            search_params=search_params,
            path_params=path_params,
            deps=deps,
        )

        cached_data = CachedData(data=data, location=location, mode=route.cache_mode)
        cache = {match.key: cached_data}

        return anvil.server.LoadAppResponse(data={"cache": cache})


class Route:
    path = None
    segments = []
    form = None
    stale_time = 0
    pending_form = None
    pending_min = 0.5
    pending_delay = 1
    cache_mode = NETWORK_FIRST
    error_form = None
    not_found_form = None

    def before_load(self):
        pass

    def loader_deps(self, **loader_args):
        return {}

    def loader(self, **loader_args):
        return None

    def parse_path_params(self, path_params):
        return path_params

    def prepare_path_params(self, path_params):
        return path_params

    def parse_search_params(self, search_params):
        return search_params

    def prepare_search_params(self, search_params):
        return search_params

    def __init_subclass__(cls) -> None:
        if cls.path is not None:
            cls.path = trim_path(cls.path)
            cls.segments = Segment.from_path(cls.path)
            sorted_routes.append(cls())

        if anvil.is_server_side():
            _create_server_route(cls)
