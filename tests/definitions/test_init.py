"""Tests for tuya-device-handlers."""


def test_import() -> None:
    """Test import of definitions"""
    # ruff: disable[F401, PLC0415]
    from tuya_device_handlers.definitions.alarm_control_panel import (
        AlarmControlPanelDefinition,
    )
    from tuya_device_handlers.definitions.binary_sensor import (
        BinarySensorDefinition,
    )
    from tuya_device_handlers.definitions.button import ButtonDefinition
    from tuya_device_handlers.definitions.climate import ClimateDefinition
    from tuya_device_handlers.definitions.cover import CoverDefinition
    from tuya_device_handlers.definitions.event import EventDefinition
    from tuya_device_handlers.definitions.fan import FanDefinition
    from tuya_device_handlers.definitions.humidifier import HumidifierDefinition
    from tuya_device_handlers.definitions.light import LightDefinition
    from tuya_device_handlers.definitions.number import NumberDefinition
    from tuya_device_handlers.definitions.select import SelectDefinition
    from tuya_device_handlers.definitions.sensor import SensorDefinition
    from tuya_device_handlers.definitions.siren import SirenDefinition
    from tuya_device_handlers.definitions.switch import SwitchDefinition
    from tuya_device_handlers.definitions.vacuum import VacuumDefinition
    from tuya_device_handlers.definitions.valve import ValveDefinition
    # ruff: enable[F401, PLC0415]
