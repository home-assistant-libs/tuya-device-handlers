"""Tuya device wrapper."""

import json
from typing import Any

from tuya_sharing import CustomerDevice

from ..type_information import IntegerTypeInformation
from ..utils import RemapHelper
from .common import DPCodeIntegerWrapper, DPCodeJsonWrapper


class BrightnessWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper for brightness DP code.

    Handles brightness value conversion between device scale and Home Assistant's
    0-255 scale. Supports optional dynamic brightness_min and brightness_max
    wrappers that allow the device to specify runtime brightness range limits.
    """

    brightness_min: DPCodeIntegerWrapper | None = None
    brightness_max: DPCodeIntegerWrapper | None = None
    brightness_min_remap: RemapHelper | None = None
    brightness_max_remap: RemapHelper | None = None

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodeIntegerWrapper."""
        super().__init__(dpcode, type_information)
        self._remap_helper = RemapHelper.from_type_information(
            type_information, 0, 255
        )

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Return the brightness of this light between 0..255."""
        if (brightness := device.status.get(self.dpcode)) is None:
            return None

        # Remap value to our scale
        brightness = self._remap_helper.remap_value_to(brightness)

        # If there is a min/max value, the brightness is actually limited.
        # Meaning it is actually not on a 0-255 scale.
        if (
            self.brightness_max is not None
            and self.brightness_min is not None
            and self.brightness_max_remap is not None
            and self.brightness_min_remap is not None
            and (
                brightness_max := device.status.get(self.brightness_max.dpcode)
            )
            is not None
            and (
                brightness_min := device.status.get(self.brightness_min.dpcode)
            )
            is not None
        ):
            # Remap values onto our scale
            brightness_max = self.brightness_max_remap.remap_value_to(
                brightness_max
            )
            brightness_min = self.brightness_min_remap.remap_value_to(
                brightness_min
            )

            # Remap the brightness value from their min-max to our 0-255 scale
            brightness = RemapHelper.remap_value(
                brightness,
                from_min=brightness_min,
                from_max=brightness_max,
                to_min=0,
                to_max=255,
            )

        return round(brightness)

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: float
    ) -> Any:
        """Convert a Home Assistant value (0..255) back to a raw device value."""
        # If there is a min/max value, the brightness is actually limited.
        # Meaning it is actually not on a 0-255 scale.
        if (
            self.brightness_max is not None
            and self.brightness_min is not None
            and self.brightness_max_remap is not None
            and self.brightness_min_remap is not None
            and (
                brightness_max := device.status.get(self.brightness_max.dpcode)
            )
            is not None
            and (
                brightness_min := device.status.get(self.brightness_min.dpcode)
            )
            is not None
        ):
            # Remap values onto our scale
            brightness_max = self.brightness_max_remap.remap_value_to(
                brightness_max
            )
            brightness_min = self.brightness_min_remap.remap_value_to(
                brightness_min
            )

            # Remap the brightness value from our 0-255 scale to their min-max
            value = RemapHelper.remap_value(
                value,
                from_min=0,
                from_max=255,
                to_min=brightness_min,
                to_max=brightness_max,
            )
        return round(self._remap_helper.remap_value_from(value))


class ColorTempWrapper(DPCodeIntegerWrapper[int]):
    """Wrapper for color temperature DP code.

    A round-trip from Tuya range to Kelvin via Mireds is done for
    historical reason, and because mired scale is a better measure
    of perceptual color difference
    """

    MIN_KELVIN = 2000  # 500 mireds
    MAX_KELVIN = 6500  # 153 mireds

    @staticmethod
    def kelvin_to_mired(kelvin: int) -> float:
        return 1000000 / kelvin

    @staticmethod
    def mired_to_kelvin(mired: float) -> int:
        return round(1000000 / mired)

    def __init__(
        self, dpcode: str, type_information: IntegerTypeInformation
    ) -> None:
        """Init DPCodeIntegerWrapper."""
        super().__init__(dpcode, type_information)
        max_mireds = self.kelvin_to_mired(self.MIN_KELVIN)
        min_mireds = self.kelvin_to_mired(self.MAX_KELVIN)
        self._remap_helper = RemapHelper.from_type_information(
            type_information, min_mireds, max_mireds
        )

    def read_device_status(self, device: CustomerDevice) -> int | None:
        """Return the color temperature value in Kelvin."""
        if (temperature := device.status.get(self.dpcode)) is None:
            return None

        return self.mired_to_kelvin(
            self._remap_helper.remap_value_to(temperature, reverse=True)
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: int
    ) -> Any:
        """Convert a Home Assistant value (Kelvin) back to a raw device value."""
        return round(
            self._remap_helper.remap_value_from(
                self.kelvin_to_mired(value),
                reverse=True,
            )
        )


DEFAULT_H_TYPE = RemapHelper(
    source_min=1, source_max=360, target_min=0, target_max=360
)
DEFAULT_S_TYPE = RemapHelper(
    source_min=1, source_max=255, target_min=0, target_max=100
)
DEFAULT_V_TYPE = RemapHelper(
    source_min=1, source_max=255, target_min=0, target_max=255
)


DEFAULT_H_TYPE_V2 = RemapHelper(
    source_min=1, source_max=360, target_min=0, target_max=360
)
DEFAULT_S_TYPE_V2 = RemapHelper(
    source_min=1, source_max=1000, target_min=0, target_max=100
)
DEFAULT_V_TYPE_V2 = RemapHelper(
    source_min=1, source_max=1000, target_min=0, target_max=255
)


class ColorDataWrapper(DPCodeJsonWrapper[tuple[float, float, float]]):
    """Wrapper for color data DP code."""

    h_type = DEFAULT_H_TYPE
    s_type = DEFAULT_S_TYPE
    v_type = DEFAULT_V_TYPE

    def read_device_status(
        self, device: CustomerDevice
    ) -> tuple[float, float, float] | None:
        """Return a tuple (H, S, V) from this color data."""
        if (status := self._read_dpcode_value(device)) is None:
            return None
        return (
            self.h_type.remap_value_to(status["h"]),
            self.s_type.remap_value_to(status["s"]),
            self.v_type.remap_value_to(status["v"]),
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: tuple[float, float, float]
    ) -> Any:
        """Convert a Home Assistant tuple (H, S, V) back to a raw device value."""
        hue, saturation, brightness = value
        return json.dumps(
            {
                "h": round(self.h_type.remap_value_from(hue)),
                "s": round(self.s_type.remap_value_from(saturation)),
                "v": round(self.v_type.remap_value_from(brightness)),
            }
        )
