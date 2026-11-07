"""Test device quirk module naming."""

import pathlib

import pytest

_DEVICES_DIR = (
    pathlib.Path(__file__).parents[2]
    / "src"
    / "tuya_device_handlers"
    / "devices"
)
_QUIRK_MODULES = sorted(
    str(path.relative_to(_DEVICES_DIR))
    for path in _DEVICES_DIR.glob("*/*.py")
    if path.name != "__init__.py"
)


@pytest.mark.parametrize("module", _QUIRK_MODULES)
def test_quirk_module_naming(module: str) -> None:
    """Ensure quirk modules are named `<category>_<product_id>.py`."""
    category, _, name = module.partition("/")
    assert name.startswith(f"{category}_"), (
        f"Quirk module `{module}` should be named"
        f" `{category}/{category}_<product_id>.py`"
    )
