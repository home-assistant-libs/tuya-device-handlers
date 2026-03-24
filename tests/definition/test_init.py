"""Tests for tuya-device-handlers."""


def test_import() -> None:
    """Test import of definitions"""
    # ruff: disable[F401, PLC0415]
    from tuya_device_handlers.definition.alarm_control_panel import (
        TuyaAlarmControlPanelDefinition,
    )
    from tuya_device_handlers.definition.binary_sensor import (
        TuyaBinarySensorDefinition,
    )
    from tuya_device_handlers.definition.button import TuyaButtonDefinition
    from tuya_device_handlers.definition.camera import TuyaCameraDefinition
    from tuya_device_handlers.definition.climate import TuyaClimateDefinition
    from tuya_device_handlers.definition.cover import TuyaCoverDefinition
    from tuya_device_handlers.definition.event import TuyaEventDefinition
    from tuya_device_handlers.definition.fan import TuyaFanDefinition
    from tuya_device_handlers.definition.humidifier import (
        TuyaHumidifierDefinition,
    )
    from tuya_device_handlers.definition.light import TuyaLightDefinition
    from tuya_device_handlers.definition.number import TuyaNumberDefinition
    from tuya_device_handlers.definition.select import TuyaSelectDefinition
    from tuya_device_handlers.definition.sensor import TuyaSensorDefinition
    from tuya_device_handlers.definition.siren import TuyaSirenDefinition
    from tuya_device_handlers.definition.switch import TuyaSwitchDefinition
    from tuya_device_handlers.definition.vacuum import TuyaVacuumDefinition
    from tuya_device_handlers.definition.valve import TuyaValveDefinition
    # ruff: enable[F401, PLC0415]
