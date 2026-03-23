"""Tests for tuya-device-handlers."""


def test_import() -> None:
    """Test import of definitions"""
    # ruff: disable[F401, PLC0415]
    from tuya_device_handlers.definitions.alarm_control_panel import (
        TuyaAlarmControlPanelDefinition,
    )
    from tuya_device_handlers.definitions.binary_sensor import (
        TuyaBinarySensorDefinition,
    )
    from tuya_device_handlers.definitions.button import TuyaButtonDefinition
    from tuya_device_handlers.definitions.camera import TuyaCameraDefinition
    from tuya_device_handlers.definitions.climate import TuyaClimateDefinition
    from tuya_device_handlers.definitions.cover import TuyaCoverDefinition
    from tuya_device_handlers.definitions.event import TuyaEventDefinition
    from tuya_device_handlers.definitions.fan import TuyaFanDefinition
    from tuya_device_handlers.definitions.humidifier import (
        TuyaHumidifierDefinition,
    )
    from tuya_device_handlers.definitions.light import TuyaLightDefinition
    from tuya_device_handlers.definitions.number import TuyaNumberDefinition
    from tuya_device_handlers.definitions.select import TuyaSelectDefinition
    from tuya_device_handlers.definitions.sensor import TuyaSensorDefinition
    from tuya_device_handlers.definitions.siren import TuyaSirenDefinition
    from tuya_device_handlers.definitions.switch import TuyaSwitchDefinition
    from tuya_device_handlers.definitions.vacuum import TuyaVacuumDefinition
    from tuya_device_handlers.definitions.valve import TuyaValveDefinition
    # ruff: enable[F401, PLC0415]
