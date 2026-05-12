"""Tests for climate definition."""

import pytest

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
)
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature


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
