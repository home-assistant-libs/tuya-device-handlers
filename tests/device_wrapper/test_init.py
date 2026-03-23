"""Tests for tuya-device-handlers."""


def test_import() -> None:
    """Test import of definitions"""
    # ruff: disable[F401, PLC0415]
    from tuya_device_handlers.device_wrapper.alarm_control_panel import (
        TuyaAlarmControlPanelDefinition,
    )
    from tuya_device_handlers.device_wrapper.binary_sensor import (
        TuyaBinarySensorDefinition,
    )
    from tuya_device_handlers.device_wrapper.button import TuyaButtonDefinition
    from tuya_device_handlers.device_wrapper.camera import TuyaCameraDefinition
    from tuya_device_handlers.device_wrapper.climate import (
        TuyaClimateDefinition,
    )
    from tuya_device_handlers.device_wrapper.cover import TuyaCoverDefinition
    from tuya_device_handlers.device_wrapper.event import TuyaEventDefinition
    from tuya_device_handlers.device_wrapper.fan import TuyaFanDefinition
    from tuya_device_handlers.device_wrapper.humidifier import (
        TuyaHumidifierDefinition,
    )
    from tuya_device_handlers.device_wrapper.light import TuyaLightDefinition
    from tuya_device_handlers.device_wrapper.number import TuyaNumberDefinition
    from tuya_device_handlers.device_wrapper.select import TuyaSelectDefinition
    from tuya_device_handlers.device_wrapper.sensor import TuyaSensorDefinition
    from tuya_device_handlers.device_wrapper.siren import TuyaSirenDefinition
    from tuya_device_handlers.device_wrapper.switch import TuyaSwitchDefinition
    from tuya_device_handlers.device_wrapper.vacuum import TuyaVacuumDefinition
    from tuya_device_handlers.device_wrapper.valve import TuyaValveDefinition
    # ruff: enable[F401, PLC0415]
