"""Device quirks for Tuya devices."""

import base64
from enum import IntFlag
from typing import Any, Literal, TypedDict

from tuya_sharing import CustomerDevice

from tuya_device_handlers.type_information import RawTypeInformation

from .base import DeviceWrapper
from .common import DPCodeRawWrapper


class FeederSchedule(TypedDict):
    """Public class for Home Assistant representation of a feeder schedule entry."""

    days: list[str]
    """Days (monday-sunday)."""
    time: str
    """In 24h format hh:mm."""
    portion: int
    """Portion size."""
    enabled: bool
    """True or False."""


class _DefaultFeederScheduleWrapper(DPCodeRawWrapper[list[FeederSchedule]]):
    """Wrapper for a schedule received in a base64 DPCode."""

    def __init__(
        self, dpcode: str, type_information: RawTypeInformation
    ) -> None:
        super().__init__(dpcode, type_information)
        template: list[tuple[_TEMPLATE_KEY, int]] = [
            ("days", 2),
            ("hour", 2),
            ("minute", 2),
            ("portion", 2),
            ("enabled", 2),
        ]
        day_mapping = [(i, i) for i in range(7)]

        self._template_encoder = _TemplateEncoder(
            template, _DayTransformer(day_mapping)
        )

    def read_device_status(
        self, device: CustomerDevice
    ) -> list[FeederSchedule] | None:
        """Decode the meal plan data."""
        if (data := self._read_dpcode_value(device)) is None:
            return None
        hex_str = "".join(f"{byte:02x}" for byte in data)
        return _internal_list_to_home_assistant(
            self._template_encoder.decode(hex_str)
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: list[FeederSchedule]
    ) -> Any:
        """Convert display value back to a raw device value."""
        converted_data = _home_assistant_list_to_internal(value)
        hex_str = self._template_encoder.encode(converted_data)
        payload_bytes = bytes(
            int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2)
        )
        return base64.b64encode(payload_bytes).decode("utf-8")


def get_feeder_schedule_wrapper(
    device: CustomerDevice,
) -> DeviceWrapper[list[FeederSchedule]] | None:
    if device.product_id == "wfkzyy0evslzsmoi":
        return _DefaultFeederScheduleWrapper.find_dpcode(
            device, "meal_plan", prefer_function=True
        )
    return None


# Internal representation of a feeding time entry to keep it easier to tell what we expect.
_TEMPLATE_KEY = Literal["days", "hour", "minute", "portion", "enabled"]


class _DaysOfWeek(IntFlag):
    """Bitmask for days of the week."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 4
    THURSDAY = 8
    FRIDAY = 16
    SATURDAY = 32
    SUNDAY = 64


class _InternalFeederSchedule(TypedDict):
    """Internal class for representation of a feeder schedule entry."""

    days: _DaysOfWeek
    """Days bitmap. Bit 0 is Monday, bit 1 is Tuesday, ..., bit 6 is Sunday."""
    hour: int
    """Hour in 24h format."""
    minute: int
    """Minute in 24h format."""
    portion: int
    """Portion size."""
    enabled: int
    """0 or 1."""


def _home_assistant_list_to_internal(
    entries: list[FeederSchedule],
) -> list[_InternalFeederSchedule]:
    """Convert Home Assistant list to internal representation.

    Days are converted from list of day names to bitmap integer.
    Time is split from "hh:mm" string to separate hour and minute integers.
    """
    result: list[_InternalFeederSchedule] = []
    for item in entries:
        days_bitmask = _DaysOfWeek(0)
        for i in _DaysOfWeek:
            if i.name.lower() in item["days"]:  # type: ignore[union-attr]
                days_bitmask |= i
        hour, minute = map(int, item["time"].split(":"))
        result.append(
            _InternalFeederSchedule(
                days=days_bitmask,
                hour=hour,
                minute=minute,
                portion=item["portion"],
                enabled=item["enabled"],
            )
        )
    return result


def _internal_list_to_home_assistant(
    entries: list[_InternalFeederSchedule],
) -> list[FeederSchedule]:
    """Convert internal representation to Home Assistant list.

    Days are converted from bitmap integer to list of day names.
    Time is merged from separate hour and minute integers to "hh:mm" string.
    """

    result: list[FeederSchedule] = []
    for item in entries:
        result.append(
            FeederSchedule(
                days=[
                    i.name.lower()  # type: ignore[union-attr]
                    for i in _DaysOfWeek
                    if item["days"] & i
                ],
                time=f"{item['hour']:02d}:{item['minute']:02d}",
                portion=item["portion"],
                enabled=bool(item["enabled"]),
            )
        )
    return result


class _DayTransformer:
    """Helper class to encode/decode days between bitmap and list of names."""

    def __init__(self, day_mapping: list[tuple[int, int]]) -> None:
        """mapping: list of (internal_bit, device_bit)."""
        self._day_mapping = day_mapping

    def encode_entry(
        self, entry: _InternalFeederSchedule
    ) -> _InternalFeederSchedule:
        val = 0
        for internal, device in self._day_mapping:
            if entry["days"] & (1 << internal):
                val |= 1 << device
        entry["days"] = _DaysOfWeek(val & 0x7F)
        return entry

    def decode_entry(
        self, entry: _InternalFeederSchedule
    ) -> _InternalFeederSchedule:
        val = _DaysOfWeek(0)
        masked = entry["days"] & 0x7F
        for internal, device in self._day_mapping:
            if masked & (1 << device):
                val |= 1 << internal
        entry["days"] = val
        return entry


class _TemplateEncoder:
    """Encoder/decoder for templated meal plan data."""

    def __init__(
        self,
        template: list[tuple[_TEMPLATE_KEY, int]],
        day_transformer: _DayTransformer,
    ) -> None:
        """Initialize TemplateEncoder."""
        self._template = template
        self._day_transformer = day_transformer

    def encode(self, data: list[_InternalFeederSchedule]) -> str:
        """Encode meal plan data to hex string."""
        return "".join(self.serialize_entry(entry) for entry in data)

    def decode(self, data: str) -> list[_InternalFeederSchedule]:
        """Decode hex string to meal plan data."""
        chunk_len = sum(width for _, width in self._template)
        return [
            self.parse_entry(data[i : i + chunk_len])
            for i in range(0, len(data), chunk_len)
        ]

    def serialize_entry(self, data: _InternalFeederSchedule) -> str:
        """Serialize a single meal plan entry to hex string."""
        entry = self._day_transformer.encode_entry(data)
        return "".join(
            f"{entry.get(field, 0):0{width}x}"
            for field, width in self._template
        )

    def parse_entry(self, chunk: str) -> _InternalFeederSchedule:
        """Parse a single meal plan entry from hex string."""
        entry = _InternalFeederSchedule(
            days=_DaysOfWeek(0), hour=0, minute=0, portion=0, enabled=0
        )
        pos = 0
        for field, width in self._template:
            segment = chunk[pos : pos + width]
            pos += width
            if segment:
                if field == "days":
                    entry[field] = _DaysOfWeek(int(segment, 16))
                else:
                    entry[field] = int(segment, 16)
        return self._day_transformer.decode_entry(entry)
