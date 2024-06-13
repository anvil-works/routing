from webbrowser import get
import anvil
from .routes import sorted_routes
from .matcher import get_matches
from .loader import load_data, cache
from urllib.parse import urlencode


if anvil.is_server_side():

    from anvil.history import Location

    def create():
        from anvil.server import route

        for route in sorted_routes:

            @route(route.path)
            def route_handler(*args, **kwargs):
                request = anvil.server.request
                path = request.path
                query_params = request.query_params
                search = f"?{urlencode(query_params)}" if query_params else ""
                location = Location(path=path, search=search, key="default")
                match = get_matches(location=location)
                load_data(match)
                return anvil.server.LoadAppResponse(data={"cache": cache})

else:

    def listener(args):
        # TODO:
        # call get_matches
        # if match:
        #   call the loader
        #   load the form with the data
        #   need to ensure that the correct form is open
        # loader needs to be clever!

        pass

    def create():
        from anvil.history import history

        from anvil.server import startup_data

        if startup_data is not None:
            startup_cache = startup_data.get("cache", {})

        print(startup_data)
        history.listen(listener)
        # TODO navigate to the first page
