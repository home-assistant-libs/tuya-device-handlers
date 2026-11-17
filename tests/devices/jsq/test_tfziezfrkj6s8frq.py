"""Test the HQ-JS2326 humidifier quirk."""

from tuya_sharing import CustomerDevice, Manager

from tests import create_device
from tests.integration_helpers.select import get_select_default_definitions
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tests.integration_helpers.switch import get_switch_default_definitions
from tuya_device_handlers.definition.humidifier import (
    HumidifierDefinition,
    get_default_definition as get_humidifier_default_definition,
)
from tuya_device_handlers.device_wrapper.common import DPCodeBooleanWrapper
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeRoundedIntegerWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry

FIXTURE = "jsq_tfziezfrkj6s8frq.json"


def _get_humidifier_definition(
    device: CustomerDevice,
) -> HumidifierDefinition | None:
    """Mirror the JSQ humidifier description in Home Assistant core."""
    return get_humidifier_default_definition(
        device,
        switch_dpcode=("switch", "switch_spray"),
        current_humidity_dpcode="humidity_current",
        humidity_dpcode="humidity_set",
    )


def test_quirk_adds_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk registers the datapoints from the device's thing model."""
    device = create_device(FIXTURE)
    assert device.function == {}
    assert device.status_range == {}

    filled_quirks_registry.initialise_device_quirk(device)

    assert set(device.function) == {
        "switch_spray",
        "humidity_set",
        "sleep",
        "level",
    }
    assert set(device.status_range) == {
        "switch_spray",
        "humidity_set",
        "humidity_current",
        "sleep",
        "level",
    }


def test_default_definitions(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Quirk gives Home Assistant a humidifier and its extra entities."""
    device = create_device(FIXTURE)
    assert _get_humidifier_definition(device) is None
    assert get_select_default_definitions(device) == {}
    assert get_sensor_default_definitions(device) == {}
    assert get_switch_default_definitions(device) == {}

    filled_quirks_registry.initialise_device_quirk(device)

    definition = _get_humidifier_definition(device)
    assert definition
    switch = definition.switch_wrapper
    assert isinstance(switch, DPCodeBooleanWrapper)
    assert switch.dpcode == "switch_spray"
    target = definition.target_humidity_wrapper
    assert isinstance(target, DPCodeRoundedIntegerWrapper)
    assert target.dpcode == "humidity_set"
    current = definition.current_humidity_wrapper
    assert isinstance(current, DPCodeRoundedIntegerWrapper)
    assert current.dpcode == "humidity_current"
    assert definition.mode_wrapper is None

    assert set(get_select_default_definitions(device)) == {"level"}
    assert set(get_sensor_default_definitions(device)) == {"humidity_current"}
    assert set(get_switch_default_definitions(device)) == {"sleep"}


def test_commands(filled_quirks_registry: QuirksRegistry) -> None:
    """Commands use the cloud DPCodes from the thing model."""
    device = create_device(FIXTURE)
    filled_quirks_registry.initialise_device_quirk(device)
    definition = _get_humidifier_definition(device)
    assert definition
    assert definition.switch_wrapper
    assert definition.target_humidity_wrapper

    assert definition.switch_wrapper.get_update_commands(device, True) == [
        {"code": "switch_spray", "value": True}
    ]
    assert definition.target_humidity_wrapper.get_update_commands(
        device, 55
    ) == [{"code": "humidity_set", "value": 55}]


def test_mqtt(
    filled_quirks_registry: QuirksRegistry, mock_manager: Manager
) -> None:
    """Check local strategy handling of MQTT reports."""
    device = create_device(FIXTURE)
    mock_manager.device_map[device.id] = device
    filled_quirks_registry.initialise_device_quirk(device)

    mock_manager._on_device_report(
        device.id,
        [
            {"dpId": 2, "t": 1794158153000, "value": True},
            {"dpId": 13, "t": 1794158153000, "value": 60},
            {"dpId": 14, "t": 1794158153000, "value": 47},
            {"dpId": 16, "t": 1794158153000, "value": False},
            {"dpId": 23, "t": 1794158153000, "value": "level_3"},
        ],
    )
    assert device.status["switch_spray"] is True
    assert device.status["humidity_set"] == 60
    assert device.status["humidity_current"] == 47
    assert device.status["sleep"] is False
    assert device.status["level"] == "level_3"
