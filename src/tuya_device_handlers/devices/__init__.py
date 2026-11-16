"""Quirks for Tuya."""

import importlib
import importlib.util
import logging
import pathlib
import pkgutil
import sys
from typing import TYPE_CHECKING

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY

_LOGGER = logging.getLogger(__name__)


def register_tuya_quirks(custom_quirks_path: str | None = None) -> None:
    """Register all available quirks.

    - remove custom quirks from `custom_quirks_path`
    - add quirks from `devices` subfolder
    - add custom quirks from `custom_quirks_path`
    """
    _register_builtin_quirks()
    # Snapshot them before any custom quirk can shadow one.
    TUYA_QUIRKS_REGISTRY.capture_builtin_quirks()

    if custom_quirks_path is None:
        return

    # Hold the registry across the purge and the reload, so that a concurrent
    # caller (Home Assistant sets up each config entry in its own executor
    # job) can neither observe the registry with custom quirks purged but not
    # yet reloaded, nor interleave its own purge with ours.
    with TUYA_QUIRKS_REGISTRY.reloading():
        TUYA_QUIRKS_REGISTRY.purge_custom_quirks(custom_quirks_path)
        _register_custom_quirks(custom_quirks_path)


def _register_builtin_quirks() -> None:
    """Import every built-in quirk module.

    Deliberately not short-circuited by a "loaded once" flag. Registration
    happens as an import side effect, so a flag would save only the repeat
    package walk -- which is already a no-op, since `import_module` is served
    from `sys.modules` and the module bodies do not re-run. That is an
    unrelated optimisation, and it made the loader's state observable in a
    way that complicated test isolation.
    """
    for _importer, modname, _ispkg in pkgutil.walk_packages(
        path=__path__,
        prefix=__name__ + ".",
    ):
        _LOGGER.debug("Loading quirks module %r", modname)
        importlib.import_module(modname)


def _register_custom_quirks(custom_quirks_path: str) -> None:
    """Import every custom quirk module found under `custom_quirks_path`."""
    path = pathlib.Path(custom_quirks_path)
    _LOGGER.debug("Loading custom quirks from %r", path)

    loaded = False

    # Treat the custom quirk path (e.g. `/config/tuya_quirks/`)
    # itself as a module
    for importer, modname, _ispkg in pkgutil.walk_packages(path=[str(path)]):
        _LOGGER.debug("Loading custom quirk module %r", modname)

        try:
            spec = importer.find_spec(modname)  # ty: ignore[missing-argument]
            if TYPE_CHECKING:
                assert spec is not None
                assert spec.loader is not None

            module = importlib.util.module_from_spec(spec)
            sys.modules[modname] = module
            spec.loader.exec_module(module)
        except Exception:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(
                "Unexpected exception importing custom quirk %r", modname
            )
        else:
            loaded = True

    if loaded:
        _LOGGER.warning(
            "Loaded custom quirks. Please contribute them to https://github.com/home-assistant-libs/tuya-device-handlers"
        )
