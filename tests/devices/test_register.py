"""Tests for quirk registration."""

import pathlib

from tuya_device_handlers.devices import register_tuya_quirks
from tuya_device_handlers.registry import QuirksRegistry

_CUSTOM_QUIRK = '''\
"""Custom quirk used by the test suite."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="{product_id}")
    .add_dpid_integer(
        dpid=101,
        dpcode="{dpcode}",
        dpmode=DPMode.READ,
        unit="C",
        min=0,
        max=100,
        scale=0,
        step=1,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
'''


def _write_quirk(
    root: pathlib.Path, name: str, product_id: str, dpcode: str
) -> None:
    """Write a custom quirk module into `root`."""
    (root / f"{name}.py").write_text(
        _CUSTOM_QUIRK.format(product_id=product_id, dpcode=dpcode)
    )


def test_custom_quirk_shadowing_a_builtin_is_undone_on_removal(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """Deleting a custom quirk uncovers the built-in it was shadowing.

    Quirks register as an import side effect, so a built-in cannot register
    twice in one process. Without a cached snapshot, purging the custom
    quirk would drop support for the device until the host restarts.
    """
    builtin_product = "m7kacaxrxbxeegfs"
    builtin = filled_quirks_registry._quirks[builtin_product]

    _write_quirk(tmp_path, "shadow", builtin_product, "shadowed_code")
    register_tuya_quirks(str(tmp_path))
    shadowing = filled_quirks_registry._quirks[builtin_product]
    assert shadowing is not builtin
    assert shadowing.quirk_file.is_relative_to(tmp_path)

    (tmp_path / "shadow.py").unlink()
    register_tuya_quirks(str(tmp_path))

    assert filled_quirks_registry._quirks[builtin_product] is builtin


def test_custom_quirk_not_shadowing_a_builtin_is_removed(
    filled_quirks_registry: QuirksRegistry, tmp_path: pathlib.Path
) -> None:
    """A custom quirk for its own product_id is dropped outright."""
    _write_quirk(tmp_path, "own", "custom_only_product", "ext_temp")
    register_tuya_quirks(str(tmp_path))
    assert "custom_only_product" in filled_quirks_registry._quirks

    (tmp_path / "own.py").unlink()
    register_tuya_quirks(str(tmp_path))

    assert "custom_only_product" not in filled_quirks_registry._quirks
