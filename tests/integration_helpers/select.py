"""Helpers for quirk select tests.

The category mapping below mirrors the ``SELECTS`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the selects core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/select.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.select import (
    SelectDefinition,
    get_default_definition,
)


@dataclass(frozen=True)
class SelectEntityDescription:
    """Describes a Tuya select, mirroring the Home Assistant core mapping.

    ``key`` doubles as the DPCode, as in Home Assistant core.
    """

    key: str


_KG_SELECTS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription("relay_status"),
    SelectEntityDescription("light_mode"),
)

_SP_SELECTS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription("ipc_work_mode"),
    SelectEntityDescription("decibel_sensitivity"),
    SelectEntityDescription("record_mode"),
    SelectEntityDescription("basic_nightvision"),
    SelectEntityDescription("basic_anti_flicker"),
    SelectEntityDescription("motion_sensitivity"),
)

_SELECTS: dict[str, tuple[SelectEntityDescription, ...]] = {
    "bh": (
        SelectEntityDescription("temp_setting_quick_c"),
        SelectEntityDescription("work_type"),
    ),
    "cl": (
        SelectEntityDescription("control_back_mode"),
        SelectEntityDescription("mode"),
    ),
    "co2bj": (SelectEntityDescription("alarm_volume"),),
    "cs": (
        SelectEntityDescription("countdown_set"),
        SelectEntityDescription("dehumidify_set_enum"),
    ),
    "cwjwq": (SelectEntityDescription("work_mode"),),
    "cz": _KG_SELECTS,
    "dghsxj": _SP_SELECTS,
    "dgnbj": (SelectEntityDescription("alarm_volume"),),
    "dr": (
        SelectEntityDescription("level"),
        SelectEntityDescription("level_1"),
        SelectEntityDescription("level_2"),
    ),
    "fs": (
        SelectEntityDescription("fan_vertical"),
        SelectEntityDescription("fan_horizontal"),
        SelectEntityDescription("countdown"),
        SelectEntityDescription("countdown_set"),
    ),
    "jsq": (
        SelectEntityDescription("spray_mode"),
        SelectEntityDescription("level"),
        SelectEntityDescription("moodlighting"),
        SelectEntityDescription("countdown"),
        SelectEntityDescription("countdown_set"),
    ),
    "kfj": (
        SelectEntityDescription("cup_number"),
        SelectEntityDescription("concentration_set"),
        SelectEntityDescription("material"),
        SelectEntityDescription("mode"),
    ),
    "kg": _KG_SELECTS,
    "kj": (
        SelectEntityDescription("countdown"),
        SelectEntityDescription("countdown_set"),
    ),
    "pc": _KG_SELECTS,
    "qn": (SelectEntityDescription("level"),),
    "sd": (
        SelectEntityDescription("cistern"),
        SelectEntityDescription("collection_mode"),
        SelectEntityDescription("mode"),
    ),
    "sfkzq": (SelectEntityDescription("weather_delay"),),
    "sgbj": (
        SelectEntityDescription("alarm_state"),
        SelectEntityDescription("alarm_volume"),
        SelectEntityDescription("bright_state"),
    ),
    "sjz": (
        SelectEntityDescription("level"),
        SelectEntityDescription("up_down"),
    ),
    "sp": _SP_SELECTS,
    "szjqr": (SelectEntityDescription("mode"),),
    "tdq": _KG_SELECTS,
    "tgkg": (
        SelectEntityDescription("relay_status"),
        SelectEntityDescription("light_mode"),
        SelectEntityDescription("led_type_1"),
        SelectEntityDescription("led_type_2"),
        SelectEntityDescription("led_type_3"),
    ),
    "tgq": (
        SelectEntityDescription("led_type_1"),
        SelectEntityDescription("led_type_2"),
    ),
    "xnyjcn": (SelectEntityDescription("work_mode"),),
}


def get_select_default_definitions(
    device: CustomerDevice,
) -> dict[str, SelectDefinition]:
    """Get the default select definitions Home Assistant builds for a device."""
    return {
        description.key: definition
        for description in _SELECTS.get(device.category, ())
        if (definition := get_default_definition(device, description.key))
    }
