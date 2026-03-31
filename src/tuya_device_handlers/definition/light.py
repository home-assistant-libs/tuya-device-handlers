"""Tuya light definition."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import json
from typing import Any, cast

from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]

from ..device_wrapper import DeviceWrapper
from ..device_wrapper.common import (
    DPCodeBooleanWrapper,
    DPCodeEnumWrapper,
    DPCodeIntegerWrapper,
)
from ..device_wrapper.light import (
    DEFAULT_H_TYPE_V2,
    DEFAULT_S_TYPE_V2,
    DEFAULT_V_TYPE_V2,
    BrightnessWrapper,
    ColorDataWrapper,
    ColorTempWrapper,
)
from ..utils import RemapHelper
from .base import BaseEntityQuirk


@dataclass(kw_only=True)
class LightDefinition:
    brightness_wrapper: DeviceWrapper[int] | None
    color_data_wrapper: DeviceWrapper[tuple[float, float, float]] | None
    color_mode_wrapper: DeviceWrapper[str] | None
    color_temp_wrapper: DeviceWrapper[int] | None
    switch_wrapper: DeviceWrapper[bool]


# Deprecated alias for backward compatibility
TuyaLightDefinition = LightDefinition


@dataclass(kw_only=True)
class LightQuirk(BaseEntityQuirk):
    """Quirk for a light entity."""

    definition_fn: Callable[
        [CustomerDevice],
        LightDefinition | None,
    ]


class FallbackColorDataMode(StrEnum):
    """Fallback color data mode."""

    V1 = "v1"
    """hue: 0-360, saturation: 0-255, value: 0-255"""
    V2 = "v2"
    """hue: 0-360, saturation: 0-1000, value: 0-1000"""


def get_default_definition(
    device: CustomerDevice,
    *,
    switch_dpcode: str,
    brightness_dpcode: str | tuple[str, ...] | None,
    brightness_max_dpcode: str | None,
    brightness_min_dpcode: str | None,
    color_data_dpcode: str | tuple[str, ...] | None,
    color_mode_dpcode: str | None,
    color_temp_dpcode: str | tuple[str, ...] | None,
    fallback_color_data_mode: FallbackColorDataMode,
) -> LightDefinition | None:
    if not (
        switch_wrapper := DPCodeBooleanWrapper.find_dpcode(
            device, switch_dpcode, prefer_function=True
        )
    ):
        return None
    brightness_wrapper = _get_brightness_wrapper(
        device,
        brightness_dpcode=brightness_dpcode,
        brightness_max_dpcode=brightness_max_dpcode,
        brightness_min_dpcode=brightness_min_dpcode,
    )
    return LightDefinition(
        brightness_wrapper=brightness_wrapper,
        color_data_wrapper=_get_color_data_wrapper(
            device,
            brightness_wrapper,
            color_data_dpcode=color_data_dpcode,
            fallback_color_data_mode=fallback_color_data_mode,
        ),
        color_mode_wrapper=DPCodeEnumWrapper.find_dpcode(
            device, color_mode_dpcode, prefer_function=True
        ),
        color_temp_wrapper=ColorTempWrapper.find_dpcode(
            device, color_temp_dpcode, prefer_function=True
        ),
        switch_wrapper=switch_wrapper,
    )


def _get_brightness_wrapper(
    device: CustomerDevice,
    *,
    brightness_dpcode: str | tuple[str, ...] | None,
    brightness_max_dpcode: str | None,
    brightness_min_dpcode: str | None,
) -> BrightnessWrapper | None:
    if (
        brightness_wrapper := BrightnessWrapper.find_dpcode(
            device, brightness_dpcode, prefer_function=True
        )
    ) is None:
        return None
    if brightness_max := DPCodeIntegerWrapper.find_dpcode(
        device, brightness_max_dpcode, prefer_function=True
    ):
        brightness_wrapper.brightness_max = brightness_max
        brightness_wrapper.brightness_max_remap = (
            RemapHelper.from_type_information(
                brightness_max.type_information, 0, 255
            )
        )
    if brightness_min := DPCodeIntegerWrapper.find_dpcode(
        device, brightness_min_dpcode, prefer_function=True
    ):
        brightness_wrapper.brightness_min = brightness_min
        brightness_wrapper.brightness_min_remap = (
            RemapHelper.from_type_information(
                brightness_min.type_information, 0, 255
            )
        )
    return brightness_wrapper


def _get_color_data_wrapper(
    device: CustomerDevice,
    brightness_wrapper: BrightnessWrapper | None,
    *,
    color_data_dpcode: str | tuple[str, ...] | None,
    fallback_color_data_mode: FallbackColorDataMode,
) -> ColorDataWrapper | None:
    if (
        color_data_wrapper := ColorDataWrapper.find_dpcode(
            device, color_data_dpcode, prefer_function=True
        )
    ) is None:
        return None

    # Fetch color data type information
    if function_data := json.loads(
        color_data_wrapper.type_information.type_data
    ):
        color_data_wrapper.h_type = RemapHelper.from_function_data(
            cast(dict[str, Any], function_data["h"]), 0, 360
        )
        color_data_wrapper.s_type = RemapHelper.from_function_data(
            cast(dict[str, Any], function_data["s"]), 0, 100
        )
        color_data_wrapper.v_type = RemapHelper.from_function_data(
            cast(dict[str, Any], function_data["v"]), 0, 255
        )
    elif (
        fallback_color_data_mode == FallbackColorDataMode.V2
        or color_data_wrapper.dpcode == "colour_data_v2"
        or (brightness_wrapper and brightness_wrapper.max_value > 255)
    ):
        color_data_wrapper.h_type = DEFAULT_H_TYPE_V2
        color_data_wrapper.s_type = DEFAULT_S_TYPE_V2
        color_data_wrapper.v_type = DEFAULT_V_TYPE_V2

    return color_data_wrapper
