"""Tests for binary sensor definition."""

import pytest

from tests import create_device
from tuya_device_handlers.definition.binary_sensor import get_default_definition
from tuya_device_handlers.device_wrapper.binary_sensor import (
    DPCodeBitmapBitWrapper,
    DPCodeInSetWrapper,
)
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper


@pytest.mark.parametrize(
    ("dpcode", "bitmap_code", "on_values", "wrapper_type"),
    [
        ("fault", "tankfull", True, DPCodeBitmapBitWrapper),
        ("countdown_set", None, True, DPCodeInSetWrapper),
        ("child_lock", None, True, DPCodeBooleanWrapper),
    ],
)
def test_get_default_definition(
    dpcode: str,
    bitmap_code: str | None,
    on_values: bool | float | int | str | set[bool | float | int | str],
    wrapper_type: type,
) -> None:
    """Test get_default_definition."""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert (
        definition := get_default_definition(
            device, dpcode, bitmap_code, on_values
        )
    )
    assert isinstance(definition.binary_sensor_wrapper, wrapper_type)


@pytest.mark.parametrize(
    "bitmap_code",
    [
        "on",
        None,
    ],
)
def test_get_default_definition_fails(bitmap_code: str | None) -> None:
    """Test get_default_definition."""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert not get_default_definition(device, "bad", bitmap_code, True)
