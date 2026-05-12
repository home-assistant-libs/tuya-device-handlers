"""Quirks for Tuya."""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.device_wrapper.service_feeder_schedule import (
    DefaultFeederScheduleWrapper,
)

(
    DeviceQuirk()
    .applies_to(
        product_id="wfkzyy0evslzsmoi",
        manufacturer="Cleverio",
        model="Automatic pet feeder",
        model_id="PF100",
    )
    .map_feeder_schedules_wrapper(
        wrapper_function=lambda device: (
            DefaultFeederScheduleWrapper.find_dpcode(
                device, "meal_plan", prefer_function=True
            )
        )
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
