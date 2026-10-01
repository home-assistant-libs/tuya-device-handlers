"""Test device-level quirk initialisation."""

from tests import create_device
from tuya_device_handlers.definition.climate import get_default_definition
from tuya_device_handlers.device_wrapper.common import DPCodeIntegerWrapper
from tuya_device_handlers.helpers.homeassistant import TuyaUnitOfTemperature
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk fixes temp_set's unit and remaps temp_current to WInTemp.

    Confirmed live against the real device, not just a config-valid guess
    (see docs/fairland-heat-pump-tuya.md in the consuming repo for the full
    investigation). Retiring dpid 124 also drops any cached status value
    for the "temp_current" dpcode (``_DatapointRemoval`` pops it), matching
    what was actually observed live: current_temperature read ``None`` for
    a few seconds right after the quirk took effect, then settled to a
    real value once the next status push for dpid 102 arrived. The test
    mirrors that by injecting the post-push value by hand rather than
    having it already present in the fixture.
    """
    device = create_device("rs_CGJ08iaKlWqKmVuX.json")

    # Before the quirk: temp_set has an empty unit, so climate.py falls
    # back to the live (wrong) temp_unit_convert value ("f") and treats
    # the already-Celsius value as Fahrenheit.
    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    set_wrapper = definition.set_temperature_wrapper
    assert isinstance(set_wrapper, DPCodeIntegerWrapper)
    assert set_wrapper.type_information.unit == "f"
    assert set_wrapper.read_device_status(device) == 31

    filled_quirks_registry.initialise_device_quirk(device)

    # After the quirk: temp_set's real unit ("c") is declared on the
    # datapoint itself, so the temp_unit_convert fallback is never
    # consulted; and current_temperature_wrapper now reads the real
    # WInTemp-backed value (dpid 102) instead of the dead dpid 124.
    definition = get_default_definition(device, TuyaUnitOfTemperature.CELSIUS)
    assert definition is not None
    set_wrapper = definition.set_temperature_wrapper
    assert isinstance(set_wrapper, DPCodeIntegerWrapper)
    assert set_wrapper.native_unit == "c"
    assert set_wrapper.read_device_status(device) == 31

    current_wrapper = definition.current_temperature_wrapper
    assert isinstance(current_wrapper, DPCodeIntegerWrapper)
    assert current_wrapper.native_unit == "c"
    # Retiring dpid 124 drops any value cached under the "temp_current"
    # dpcode; there is nothing to read until the next status push for the
    # newly-mapped dpid 102 arrives.
    assert current_wrapper.read_device_status(device) is None
    device.status["temp_current"] = 18
    assert current_wrapper.read_device_status(device) == 18
