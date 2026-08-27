"""Device quirks for Tuya devices."""

import base64
from typing import Any, TypedDict

from tuya_sharing import CustomerDevice

from tuya_device_handlers.raw_data_model import (
    FeederScheduleData as _RawFeederScheduleData,
    FeederScheduleDataEntry as _RawFeederScheduleDataEntry,
)

from .base import DeviceWrapper
from .common import DPCodeRawWrapper


class FeederSchedule(TypedDict):
    """HA representation of a feeder schedule entry."""

    days: list[str]
    """Days (monday-sunday)."""
    time: str
    """In 24h format hh:mm."""
    portion: int
    """Portion size."""
    enabled: bool
    """True or False."""


_DAYS_OF_WEEK: list[str] = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class DefaultFeederScheduleWrapper(DPCodeRawWrapper[list[FeederSchedule]]):
    """Wrapper for a schedule received in a base64 DPCode."""

    def read_device_status(
        self, device: CustomerDevice
    ) -> list[FeederSchedule] | None:
        """Decode the meal plan data."""
        if (data := self._read_dpcode_value(device)) is None:
            return None
        if (entries := _RawFeederScheduleData.from_bytes(data)) is None:
            return None
        return [self._decode_entry(entry) for entry in entries]

    @staticmethod
    def _decode_entry(
        entry: _RawFeederScheduleDataEntry,
    ) -> FeederSchedule:
        """Convert a raw entry to a HA FeederSchedule dict."""
        bitmask = entry.days & 0x7F
        return FeederSchedule(
            # Bit 0 = Monday … bit 6 = Sunday; bit 7 unused.
            days=[
                name
                for i, name in enumerate(_DAYS_OF_WEEK)
                if bitmask & (1 << i)
            ],
            time=f"{entry.hour:02d}:{entry.minute:02d}",
            portion=entry.portion,
            enabled=bool(entry.enabled),
        )

    def _convert_value_to_raw_value(
        self, device: CustomerDevice, value: list[FeederSchedule]
    ) -> Any:
        """Convert display value back to a raw device value."""
        payload = _RawFeederScheduleData.to_bytes(
            [self._encode_entry(item) for item in value]
        )
        return base64.b64encode(payload).decode("utf-8")

    @staticmethod
    def _encode_entry(
        item: FeederSchedule,
    ) -> _RawFeederScheduleDataEntry:
        """Convert a HA FeederSchedule dict to a raw entry."""
        # Bit 0 = Monday … bit 6 = Sunday; bit 7 unused.
        bitmask = 0
        for i, name in enumerate(_DAYS_OF_WEEK):
            if name in item["days"]:
                bitmask |= 1 << i
        hour, minute = map(int, item["time"].split(":"))
        return _RawFeederScheduleDataEntry(
            days=bitmask,
            hour=hour,
            minute=minute,
            portion=item["portion"],
            enabled=int(item["enabled"]),
        )


def get_feeder_schedule_wrapper(
    device: CustomerDevice,
) -> DeviceWrapper[list[FeederSchedule]] | None:
    """Get the feeder schedules wrapper for a device."""
    from tuya_device_handlers import (  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
        TUYA_QUIRKS_REGISTRY,
    )

    if (quirk := TUYA_QUIRKS_REGISTRY.get_quirk_for_device(device)) is not None:
        return quirk.get_feeder_schedules_wrapper(device)

    return None
