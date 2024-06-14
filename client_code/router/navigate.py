from anvil.history import history, Location
import json

from .segments import Segment
from .utils import trim_path, url_encode, encode_search_params
from .constants import NOT_FOUND


def navigate(path=None, search_params=None, path_params=None, hash="", replace=False):
    real_path = None
    search = ""
    path_params = path_params or {}
    search_params = search_params or {}

    if path is not None:
        real_path = ""
        path = trim_path(path)
        segments = Segment.from_path(path)
        for segment in segments:
            if segment.is_static():
                real_path += "/" + url_encode(segment.value)
            elif segment.is_param():
                value = path_params.get(segment.value, NOT_FOUND)
                if value is NOT_FOUND:
                    raise Exception(f"No path param for {segment.value}")
                real_path += "/" + url_encode(str(value))
    if search_params:
        real_search_params = {}
        keys = sorted(search_params.keys())
        for key in keys:
            real_search_params[key] = json.dumps(search_params[key], sort_keys=True)

        search = encode_search_params(real_search_params)

    location = Location(path=real_path, search=search, hash=hash)
    current_location = history.location
    print("LOCATION", location, current_location)

    if (
        current_location.path == location.path
        and current_location.search == location.search
        and current_location.hash == location.hash
    ):
        print("early exit")
        return

    if replace:
        history.replace(location)
    else:
        history.push(location)
