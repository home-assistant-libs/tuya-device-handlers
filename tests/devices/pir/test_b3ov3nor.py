"""Tests for the b3ov3nor PIR device."""

from tests import create_device
from tests.integration_helpers.binary_sensor import (
    get_binary_sensor_default_definitions,
)
from tests.integration_helpers.sensor import get_sensor_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_b3ov3nor_pir_wrapper(filled_quirks_registry: QuirksRegistry) -> None:
    """測試 PIR 人體感測器 Wrapper 能否正確讀取並解析狀態。"""
    device = create_device("pir_b3ov3nor.json")
    filled_quirks_registry.initialise_device_quirk(device)

    # 透過 integration_helper 取得動態綁定的 binary_sensor wrapper
    binary_defs = get_binary_sensor_default_definitions(device)
    wrapper = binary_defs["pir"].binary_sensor_wrapper
    assert wrapper is not None

    # 1. 模擬動態變更狀態：有人移動 (True)
    device.status["pir"] = True
    assert wrapper.read_device_status(device) is True

    # 2. 模擬動態變更狀態：無人移動 (False)
    device.status["pir"] = False
    assert wrapper.read_device_status(device) is False


def test_b3ov3nor_battery_wrapper(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """測試電池電量感測器 Wrapper 能否正確讀取並解析狀態。"""
    device = create_device("pir_b3ov3nor.json")
    filled_quirks_registry.initialise_device_quirk(device)

    # 透過 integration_helper 取得動態綁定的 sensor wrapper
    sensor_defs = get_sensor_default_definitions(device)
    wrapper = sensor_defs["battery_percentage"].sensor_wrapper
    assert wrapper is not None

    # 1. 模擬動態變更狀態：電量 85%
    device.status["battery_percentage"] = 85
    assert wrapper.read_device_status(device) == 85

    # 2. 模擬動態變更狀態：低電量 15%
    device.status["battery_percentage"] = 15
    assert wrapper.read_device_status(device) == 15
