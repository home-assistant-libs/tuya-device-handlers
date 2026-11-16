"""Helpers for quirk switch tests.

The category mapping below mirrors the ``SWITCHES`` dictionary in Home
Assistant core, so tests can assert that a quirk produces the switches core
would build for a device.
https://github.com/home-assistant/core/blob/dev/homeassistant/components/tuya/switch.py
"""

from dataclasses import dataclass

from tuya_sharing import CustomerDevice

from tuya_device_handlers.definition.switch import (
    SwitchDefinition,
    get_default_definition,
)


@dataclass(frozen=True)
class SwitchEntityDescription:
    """Describes a Tuya switch, mirroring the Home Assistant core mapping.

    ``key`` doubles as the DPCode, as in Home Assistant core.
    """

    key: str


_PC_SWITCHES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription("child_lock"),
    SwitchEntityDescription("switch_1"),
    SwitchEntityDescription("switch_2"),
    SwitchEntityDescription("switch_3"),
    SwitchEntityDescription("switch_4"),
    SwitchEntityDescription("switch_5"),
    SwitchEntityDescription("switch_6"),
    SwitchEntityDescription("switch_usb1"),
    SwitchEntityDescription("switch_usb2"),
    SwitchEntityDescription("switch_usb3"),
    SwitchEntityDescription("switch_usb4"),
    SwitchEntityDescription("switch_usb5"),
    SwitchEntityDescription("switch_usb6"),
    SwitchEntityDescription("switch"),
)

_SP_SWITCHES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription("wireless_batterylock"),
    SwitchEntityDescription("cry_detection_switch"),
    SwitchEntityDescription("decibel_switch"),
    SwitchEntityDescription("record_switch"),
    SwitchEntityDescription("motion_record"),
    SwitchEntityDescription("basic_private"),
    SwitchEntityDescription("basic_flip"),
    SwitchEntityDescription("basic_osd"),
    SwitchEntityDescription("basic_wdr"),
    SwitchEntityDescription("motion_tracking"),
    SwitchEntityDescription("motion_switch"),
    SwitchEntityDescription("motion_area_switch"),
    SwitchEntityDescription("ipc_auto_siren"),
)

_SWITCHES: dict[str, tuple[SwitchEntityDescription, ...]] = {
    "bh": (
        SwitchEntityDescription("start"),
        SwitchEntityDescription("warm"),
    ),
    "bzyd": (
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("switch_music"),
        SwitchEntityDescription("snooze"),
    ),
    "cjkg": (
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("switch_3"),
        SwitchEntityDescription("switch_4"),
    ),
    "cl": (
        SwitchEntityDescription("control_back"),
        SwitchEntityDescription("opposite"),
    ),
    "cn": (
        SwitchEntityDescription("disinfection"),
        SwitchEntityDescription("water"),
    ),
    "cs": (
        SwitchEntityDescription("anion"),
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("filter_reset"),
    ),
    "cwjwq": (SwitchEntityDescription("switch"),),
    "cwwsq": (SwitchEntityDescription("slow_feed"),),
    "cwysj": (
        SwitchEntityDescription("filter_reset"),
        SwitchEntityDescription("pump_reset"),
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("water_reset"),
        SwitchEntityDescription("uv"),
    ),
    "cz": _PC_SWITCHES,
    "dghsxj": _SP_SWITCHES,
    "dj": (SwitchEntityDescription("switch"),),
    "dlq": (
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("switch"),
    ),
    "dr": (
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("preheat"),
        SwitchEntityDescription("preheat_1"),
        SwitchEntityDescription("preheat_2"),
    ),
    "fs": (
        SwitchEntityDescription("anion"),
        SwitchEntityDescription("humidifier"),
        SwitchEntityDescription("oxygen"),
        SwitchEntityDescription("fan_cool"),
        SwitchEntityDescription("fan_beep"),
        SwitchEntityDescription("child_lock"),
    ),
    "fsd": (SwitchEntityDescription("fan_beep"),),
    "ggq": (
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("switch_3"),
        SwitchEntityDescription("switch_4"),
        SwitchEntityDescription("switch_5"),
        SwitchEntityDescription("switch_6"),
        SwitchEntityDescription("switch_7"),
        SwitchEntityDescription("switch_8"),
    ),
    "hxd": (
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("switch_3"),
        SwitchEntityDescription("switch_4"),
        SwitchEntityDescription("switch_5"),
        SwitchEntityDescription("switch_6"),
    ),
    "jsq": (
        SwitchEntityDescription("switch_sound"),
        SwitchEntityDescription("sleep"),
        SwitchEntityDescription("sterilization"),
    ),
    "kg": (
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("switch_3"),
        SwitchEntityDescription("switch_4"),
        SwitchEntityDescription("switch_5"),
        SwitchEntityDescription("switch_6"),
        SwitchEntityDescription("switch_7"),
        SwitchEntityDescription("switch_8"),
        SwitchEntityDescription("switch_usb1"),
        SwitchEntityDescription("switch_usb2"),
        SwitchEntityDescription("switch_usb3"),
        SwitchEntityDescription("switch_usb4"),
        SwitchEntityDescription("switch_usb5"),
        SwitchEntityDescription("switch_usb6"),
        SwitchEntityDescription("switch"),
    ),
    "kj": (
        SwitchEntityDescription("anion"),
        SwitchEntityDescription("filter_reset"),
        SwitchEntityDescription("lock"),
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("wet"),
        SwitchEntityDescription("uv"),
    ),
    "kt": (
        SwitchEntityDescription("anion"),
        SwitchEntityDescription("lock"),
    ),
    "ks": (SwitchEntityDescription("anion"),),
    "mal": (
        SwitchEntityDescription("switch_alarm_sound"),
        SwitchEntityDescription("switch_alarm_light"),
    ),
    "msp": (SwitchEntityDescription("auto_clean"),),
    "mzj": (
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("start"),
    ),
    "pc": _PC_SWITCHES,
    "qccdz": (SwitchEntityDescription("switch"),),
    "qjdcz": (SwitchEntityDescription("switch_1"),),
    "qn": (
        SwitchEntityDescription("anion"),
        SwitchEntityDescription("lock"),
    ),
    "qxj": (SwitchEntityDescription("switch"),),
    "sd": (
        SwitchEntityDescription("switch_disturb"),
        SwitchEntityDescription("voice_switch"),
    ),
    "sgbj": (SwitchEntityDescription("muffling"),),
    "sjz": (SwitchEntityDescription("child_lock"),),
    "sp": _SP_SWITCHES,
    "sz": (
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("pump"),
    ),
    "szjqr": (SwitchEntityDescription("switch"),),
    "tdq": (
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
        SwitchEntityDescription("switch_3"),
        SwitchEntityDescription("switch_4"),
        SwitchEntityDescription("switch_5"),
        SwitchEntityDescription("switch_6"),
        SwitchEntityDescription("child_lock"),
    ),
    "tyndj": (SwitchEntityDescription("switch_save_energy"),),
    "wg2": (SwitchEntityDescription("muffling"),),
    "wk": (
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("frost"),
    ),
    "wkcz": (
        SwitchEntityDescription("switch_1"),
        SwitchEntityDescription("switch_2"),
    ),
    "wkf": (
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("window_check"),
    ),
    "wnykq": (SwitchEntityDescription("switch"),),
    "wsdcg": (SwitchEntityDescription("switch"),),
    "xdd": (SwitchEntityDescription("do_not_disturb"),),
    "xnyjcn": (SwitchEntityDescription("feedin_power_limit_enable"),),
    "xxj": (
        SwitchEntityDescription("switch"),
        SwitchEntityDescription("switch_spray"),
        SwitchEntityDescription("switch_voice"),
    ),
    "ywbj": (SwitchEntityDescription("muffling"),),
    "zndb": (SwitchEntityDescription("switch"),),
    "znjxs": (SwitchEntityDescription("switch"),),
    "znrb": (
        SwitchEntityDescription("child_lock"),
        SwitchEntityDescription("switch"),
    ),
}


def get_switch_default_definitions(
    device: CustomerDevice,
) -> dict[str, SwitchDefinition]:
    """Get the default switch definitions Home Assistant builds for a device."""
    return {
        description.key: definition
        for description in _SWITCHES.get(device.category, ())
        if (definition := get_default_definition(device, description.key))
    }
