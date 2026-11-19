"""Tests for climate definition."""

import pytest

from tests import create_device
from tuya_device_handlers.definition.climate import (
    InfraredAcFanModeWrapper,
    InfraredAcHVACModeWrapper,
    InfraredAcPowerWrapper,
    InfraredAcTemperatureWrapper,
    get_default_definition,
    get_infrared_ac_definition,
)
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
)
from tuya_device_handlers.helpers.homeassistant import (
    TuyaClimateHVACMode,
    TuyaUnitOfTemperature,
)


@pytest.mark.parametrize(
    "unit", [TuyaUnitOfTemperature.CELSIUS, TuyaUnitOfTemperature.FAHRENHEIT]
)
def test_get_default_definition(unit: TuyaUnitOfTemperature) -> None:
    """Test get_default_definition."""
    device = create_device("kt_5wnlzekkstwcdsvm.json")
    assert (definition := get_default_definition(device, unit))
    assert not definition.current_humidity_wrapper
    assert isinstance(
        definition.current_temperature_wrapper, DPCodeIntegerWrapper
    )
    assert isinstance(definition.set_temperature_wrapper, DPCodeIntegerWrapper)
    assert isinstance(definition.fan_mode_wrapper, DPCodeEnumWrapper)
    assert not definition.hvac_mode_wrapper
    assert not definition.preset_wrapper
    assert isinstance(definition.switch_wrapper, DPCodeBooleanWrapper)
    assert not definition.swing_wrapper
    assert not definition.target_humidity_wrapper


@pytest.mark.parametrize(
    "unit", [TuyaUnitOfTemperature.CELSIUS, TuyaUnitOfTemperature.FAHRENHEIT]
)
def test_get_default_definition_with_convert(
    unit: TuyaUnitOfTemperature,
) -> None:
    """Test get_default_definition."""
    device = create_device("wk_B0eP8qYAdpUo4yR9.json")
    assert (definition := get_default_definition(device, unit))
    assert not definition.current_humidity_wrapper
    assert isinstance(
        definition.current_temperature_wrapper, DPCodeIntegerWrapper
    )
    assert isinstance(definition.set_temperature_wrapper, DPCodeIntegerWrapper)
    assert not definition.fan_mode_wrapper
    assert not definition.hvac_mode_wrapper
    assert not definition.preset_wrapper
    assert not definition.switch_wrapper
    assert not definition.swing_wrapper
    assert not definition.target_humidity_wrapper


def test_get_infrared_ac_definition() -> None:
    """Test the definition for IR air conditioners."""
    device = create_device("infrared_ac_1ownck.json")

    definition = get_infrared_ac_definition(device)
    assert definition

    assert not definition.current_humidity_wrapper
    assert not definition.current_temperature_wrapper
    assert isinstance(definition.fan_mode_wrapper, InfraredAcFanModeWrapper)
    assert definition.fan_mode_wrapper.options == [
        "auto",
        "low",
        "medium",
        "high",
    ]
    assert isinstance(definition.hvac_mode_wrapper, InfraredAcHVACModeWrapper)
    assert definition.hvac_mode_wrapper.options == [
        "cool",
        "heat",
        "heat_cool",
        "fan_only",
        "dry",
    ]
    assert not definition.preset_wrapper
    assert isinstance(
        definition.set_temperature_wrapper, InfraredAcTemperatureWrapper
    )
    assert definition.set_temperature_wrapper.min_value == 16
    assert definition.set_temperature_wrapper.max_value == 30
    assert definition.set_temperature_wrapper.value_step == 1
    assert not definition.swing_wrapper
    assert isinstance(definition.switch_wrapper, InfraredAcPowerWrapper)
    assert not definition.target_humidity_wrapper
    assert definition.temperature_unit == TuyaUnitOfTemperature.CELSIUS

    assert definition.switch_wrapper.get_update_commands(device, True) == [
        {"code": "PowerOn", "value": "PowerOn"}
    ]
    assert definition.switch_wrapper.get_update_commands(device, False) == [
        {"code": "PowerOff", "value": "PowerOff"}
    ]
    assert definition.hvac_mode_wrapper.get_update_commands(
        device, TuyaClimateHVACMode.HEAT
    ) == [{"code": "M", "value": 1}]
    assert definition.fan_mode_wrapper.get_update_commands(device, "high") == [
        {"code": "F", "value": 3}
    ]
    assert definition.set_temperature_wrapper.get_update_commands(
        device, 24
    ) == [{"code": "T", "value": 24}]
