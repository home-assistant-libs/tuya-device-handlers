"""Test device-level quirk initialisation."""

import json

from tests import create_device
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.device_wrapper.common import DPCodeEnumWrapper
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_adds_confirmed_mode_values(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk extends the `mode` enum range."""
    device = create_device("znrb_zqrzsid4zllmowtt.json")
    assert device.status["mode"] == "make_hot"

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["auto"]
    assert wrapper.read_device_status(device) is None

    filled_quirks_registry.initialise_device_quirk(device)

    wrapper = DPCodeEnumWrapper.find_dpcode(
        device, "mode", prefer_function=True
    )
    assert wrapper is not None
    assert wrapper.options == ["auto", "make_hot", "make_cold"]
    assert wrapper.read_device_status(device) == "make_hot"


def test_quirk_removes_eev_temperature_sensor(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk removes `temp_current`, which reports the EEV opening."""
    device = create_device("znrb_zqrzsid4zllmowtt.json")

    definitions = get_sensor_default_definitions(device)
    assert "temp_current" in definitions

    filled_quirks_registry.initialise_device_quirk(device)

    assert "temp_current" not in device.status_range
    definitions = get_sensor_default_definitions(device)
    assert "temp_current" not in definitions


def test_quirk_adds_missing_temperature_sensors(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk declares the reported but undeclared temperature DPs."""
    device = create_device("znrb_zqrzsid4zllmowtt.json")

    for dpcode in (
        "temp_coiler",
        "temp_venting",
        "temp_effluent",
        "temp_around",
    ):
        assert dpcode not in device.status_range

    filled_quirks_registry.initialise_device_quirk(device)

    definitions = get_sensor_default_definitions(device)
    for dpcode in (
        "temp_coiler",
        "temp_venting",
        "temp_effluent",
        "temp_around",
    ):
        assert dpcode in device.status_range
        assert dpcode in definitions


def test_quirk_raises_minimum_set_temperature(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Test quirk raises the `temp_set` minimum to 59°F."""
    device = create_device("znrb_zqrzsid4zllmowtt.json")

    assert json.loads(device.function["temp_set"].values)["min"] == 47

    filled_quirks_registry.initialise_device_quirk(device)

    assert json.loads(device.function["temp_set"].values)["min"] == 59
