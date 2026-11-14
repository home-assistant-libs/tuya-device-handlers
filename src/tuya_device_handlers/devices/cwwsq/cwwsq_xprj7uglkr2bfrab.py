"""Quirk for the generic WiFi Feeder (product_id xprj7uglkr2bfrab).

The device is not in the feeder schedule registry, so Home Assistant refuses
`tuya.get_feeder_meal_plan` / `tuya.set_feeder_meal_plan` ("does not support
meal plan status"). Its `meal_plan` raw datapoint uses the same 5-byte entries
as the Cleverio PF100, except that the day bitmask is reversed: Sunday is bit 0,
Saturday bit 1, ..., Monday bit 6.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    ReversedDaysFeederScheduleWrapper,
)

(
    DeviceQuirk()
    .applies_to(product_id="xprj7uglkr2bfrab")
    .map_feeder_schedules_wrapper(
        wrapper_function=lambda device: (
            ReversedDaysFeederScheduleWrapper.find_dpcode(
                device, "meal_plan", prefer_function=True
            )
        )
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
