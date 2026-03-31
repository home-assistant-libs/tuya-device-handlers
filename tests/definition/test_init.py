"""Tests for tuya-device-handlers."""


def test_import() -> None:
    """Test import of definitions"""
    # ruff: disable[F401, PLC0415]
    from tuya_device_handlers.definition.alarm_control_panel import (
        AlarmControlPanelDefinition,
    )
    from tuya_device_handlers.definition.binary_sensor import (
        BinarySensorDefinition,
    )
    from tuya_device_handlers.definition.button import ButtonDefinition
    from tuya_device_handlers.definition.camera import CameraDefinition
    from tuya_device_handlers.definition.climate import ClimateDefinition
    from tuya_device_handlers.definition.cover import CoverDefinition
    from tuya_device_handlers.definition.event import EventDefinition
    from tuya_device_handlers.definition.fan import FanDefinition
    from tuya_device_handlers.definition.humidifier import HumidifierDefinition
    from tuya_device_handlers.definition.light import LightDefinition
    from tuya_device_handlers.definition.number import NumberDefinition
    from tuya_device_handlers.definition.select import SelectDefinition
    from tuya_device_handlers.definition.sensor import SensorDefinition
    from tuya_device_handlers.definition.siren import SirenDefinition
    from tuya_device_handlers.definition.switch import SwitchDefinition
    from tuya_device_handlers.definition.vacuum import VacuumDefinition
    from tuya_device_handlers.definition.valve import ValveDefinition
    # ruff: enable[F401, PLC0415]
