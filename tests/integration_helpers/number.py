"""Helpers for quirk number tests.

The category mapping below mirrors the ``NUMBERS`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the numbers core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/number.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.number import (
    NumberDefinition,
    get_default_definition,
)


@dataclass(frozen=True)
class NumberEntityDescription:
    """Describes a Tuya number, mirroring the Home Assistant core mapping.

    ``key`` doubles as the DPCode, as in Home Assistant core.
    """

    key: str


_SP_NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription("basic_device_volume"),
    NumberEntityDescription("ipc_bright"),
    NumberEntityDescription("ipc_contrast"),
    NumberEntityDescription("ipc_sharp"),
)

_NUMBERS: dict[str, tuple[NumberEntityDescription, ...]] = {
    "bh": (
        NumberEntityDescription("temp_set"),
        NumberEntityDescription("temp_set_f"),
        NumberEntityDescription("temp_boiling_c"),
        NumberEntityDescription("temp_boiling_f"),
        NumberEntityDescription("warm_time"),
    ),
    "bzyd": (NumberEntityDescription("volume_set"),),
    "co2bj": (NumberEntityDescription("alarm_time"),),
    "cwwsq": (
        NumberEntityDescription("manual_feed"),
        NumberEntityDescription("voice_times"),
    ),
    "dghsxj": _SP_NUMBERS,
    "dgnbj": (NumberEntityDescription("alarm_time"),),
    "fs": (NumberEntityDescription("temp"),),
    "hps": (
        NumberEntityDescription("sensitivity"),
        NumberEntityDescription("near_detection"),
        NumberEntityDescription("far_detection"),
        NumberEntityDescription("target_dis_closest"),
    ),
    "jsq": (
        NumberEntityDescription("temp_set"),
        NumberEntityDescription("temp_set_f"),
    ),
    "kfj": (
        NumberEntityDescription("water_set"),
        NumberEntityDescription("temp_set"),
        NumberEntityDescription("warm_time"),
        NumberEntityDescription("powder_set"),
    ),
    "mal": (
        NumberEntityDescription("delay_set"),
        NumberEntityDescription("alarm_delay_time"),
        NumberEntityDescription("alarm_time"),
    ),
    "msp": (NumberEntityDescription("delay_clean_time"),),
    "mzj": (
        NumberEntityDescription("cook_temperature"),
        NumberEntityDescription("cook_time"),
        NumberEntityDescription("cloud_recipe_number"),
    ),
    "sd": (NumberEntityDescription("volume_set"),),
    "sfkzq": (
        NumberEntityDescription("countdown"),
        NumberEntityDescription("countdown_1"),
        NumberEntityDescription("countdown_2"),
        NumberEntityDescription("countdown_3"),
        NumberEntityDescription("countdown_4"),
        NumberEntityDescription("countdown_5"),
        NumberEntityDescription("countdown_6"),
        NumberEntityDescription("countdown_7"),
        NumberEntityDescription("countdown_8"),
    ),
    "sgbj": (NumberEntityDescription("alarm_time"),),
    "sp": _SP_NUMBERS,
    "swtz": (
        NumberEntityDescription("cook_temperature"),
        NumberEntityDescription("cook_temperature_2"),
    ),
    "szjqr": (
        NumberEntityDescription("arm_down_percent"),
        NumberEntityDescription("arm_up_percent"),
        NumberEntityDescription("click_sustain_time"),
    ),
    "tgkg": (
        NumberEntityDescription("brightness_min_1"),
        NumberEntityDescription("brightness_max_1"),
        NumberEntityDescription("brightness_min_2"),
        NumberEntityDescription("brightness_max_2"),
        NumberEntityDescription("brightness_min_3"),
        NumberEntityDescription("brightness_max_3"),
    ),
    "tgq": (
        NumberEntityDescription("brightness_min_1"),
        NumberEntityDescription("brightness_max_1"),
        NumberEntityDescription("brightness_min_2"),
        NumberEntityDescription("brightness_max_2"),
    ),
    "wg2": (
        NumberEntityDescription("delay_set"),
        NumberEntityDescription("alarm_delay_time"),
        NumberEntityDescription("alarm_time"),
    ),
    "wk": (NumberEntityDescription("temp_correction"),),
    "xnyjcn": (
        NumberEntityDescription("backup_reserve"),
        NumberEntityDescription("output_power_limit"),
    ),
    "ywcgq": (
        NumberEntityDescription("max_set"),
        NumberEntityDescription("mini_set"),
        NumberEntityDescription("installation_height"),
        NumberEntityDescription("liquid_depth_max"),
    ),
    "zd": (NumberEntityDescription("sensitivity"),),
    "znrb": (NumberEntityDescription("temp_set"),),
}


def get_number_default_definitions(
    device: CustomerDevice,
) -> dict[str, NumberDefinition]:
    """Get the default number definitions Home Assistant builds for a device."""
    return {
        description.key: definition
        for description in _NUMBERS.get(device.category, ())
        if (definition := get_default_definition(device, description.key))
    }
