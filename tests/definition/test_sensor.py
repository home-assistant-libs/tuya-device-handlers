"""Tests for sensor definition."""

import pytest

from tests import create_device
from tuya_device_handlers.definition.sensor import get_default_definition
from tuya_device_handlers.helpers.homeassistant import TuyaSensorDeviceClass
from tuya_device_handlers.device_wrapper.common import (
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
)
from tuya_device_handlers.device_wrapper.sensor import DeltaIntegerWrapper


@pytest.mark.parametrize(
    ("fixture_filename", "dpcode", "lookup_type", "wrapper_type"),
    [
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_left",
            (DPCodeIntegerWrapper,),
            DPCodeIntegerWrapper,
        ),
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_left",
            None,
            DPCodeIntegerWrapper,
        ),
        (
            "cs_zibqa9dutqyaxym2.json",
            "countdown_set",
            (DPCodeEnumWrapper,),
            DPCodeEnumWrapper,
        ),
        ("cs_zibqa9dutqyaxym2.json", "countdown_set", None, DPCodeEnumWrapper),
        ("cz_guitoc9iylae4axs.json", "add_ele", None, DeltaIntegerWrapper),
    ],
)
def test_get_default_definition(
    fixture_filename: str,
    dpcode: str,
    lookup_type: tuple[type, ...] | None,
    wrapper_type: type,
) -> None:
    """Test get_default_definition."""
    device = create_device(fixture_filename)
    assert (definition := get_default_definition(device, dpcode, lookup_type))  # ty: ignore[invalid-argument-type]
    assert isinstance(definition.sensor_wrapper, wrapper_type)


@pytest.mark.parametrize(
    "lookup_type",
    [
        None,
        (DPCodeEnumWrapper,),
    ],
)
def test_get_default_definition_fails(
    lookup_type: tuple[type, ...] | None,
) -> None:
    """Test get_default_definition."""
    device = create_device("cs_zibqa9dutqyaxym2.json")
    assert not get_default_definition(device, "bad", lookup_type)  # ty: ignore[invalid-argument-type]


def test_sensor_device_class_override_tdq() -> None:
    """TDQ quirk registers explicit sensor device classes."""
    device = create_device("tdq_x3o8epevyeo3z3oa.json")
    temp = get_default_definition(device, "temp_current")
    assert temp is not None
    assert temp.device_class == TuyaSensorDeviceClass.TEMPERATURE
    humidity = get_default_definition(device, "humidity_value")
    assert humidity is not None
    assert humidity.device_class == TuyaSensorDeviceClass.HUMIDITY
    battery = get_default_definition(device, "battery_state")
    assert battery is not None
    assert battery.device_class == TuyaSensorDeviceClass.ENUM
