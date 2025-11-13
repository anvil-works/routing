# Copyright (c) 2024-2025 Anvil
# SPDX-License-Identifier: MIT

import anvil

from ._logger import logger
from ._non_blocking import call_async
from ._utils import await_promise

__version__ = "0.5.0"


def get_package_name():
    try:
        return anvil.app.package_name
    except Exception:
        pass
    try:
        from anvil.js.window import anvilAppMainPackage

        return anvilAppMainPackage
    except Exception:
        pass
    try:
        from anvil.js.window import debugAnvilData

        return debugAnvilData.appPackage
    except Exception:
        pass

    raise Exception("Could not determine package name")


_INFLIGHT_MODULE_PROMISES = {}


def get_cached_mod(module_name):
    module_promise = _INFLIGHT_MODULE_PROMISES.get(module_name)
    if module_promise is None:
        return None
    mod, error = await_promise(module_promise)

    _INFLIGHT_MODULE_PROMISES.pop(module_name, None)

    if error is not None:
        raise error
    return mod


def import_module(module_name):
    mod = get_cached_mod(module_name)
    if mod is not None:
        return mod

    package_name = get_package_name()

    _INFLIGHT_MODULE_PROMISES[module_name] = call_async(
        __import__, module_name, {"__package__": package_name}, level=1
    )

    mod = get_cached_mod(module_name)

    attrs = module_name.split(".")[1:]
    for attr in attrs:
        mod = getattr(mod, attr)

    return mod


def import_form(form, *args, **kws):
    if anvil.is_server_side():
        raise RuntimeError("open_form is not available on the server")

    if isinstance(form, anvil.Component):
        return form

    if not isinstance(form, str):
        raise TypeError(f"expected a form instance or a string, got {form!r}")

    mod = import_module(form)
    attrs = form.split(".")
    form_cls = getattr(mod, attrs[-1])

    return form_cls(*args, **kws)


def import_routes():
    try:
        mod = anvil.app.get_client_config("routing").get("routes_module")
        logger.debug(f"Attempting to import routes module: {mod!r}")
        import_module(mod)
    except ModuleNotFoundError as e:
        logger.debug(
            f"routes module {mod!r} does not exist {e!r}"
            ", make sure you import it manually,"
            " or set the correct routes_module in the dependency config options"
        )
    # otherwise raise the exception - the module exists but failed
    else:
        logger.debug(f"Successfully imported routes module: {mod!r}")
