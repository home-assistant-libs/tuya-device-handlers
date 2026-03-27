"""Tuya entity definition."""

from dataclasses import dataclass

from tuya_device_handlers.helpers.homeassistant import TuyaEntityCategory


@dataclass(kw_only=True)
class BaseEntityQuirk:
    """Base quirk for a Tuya entity."""

    key: str

    device_class: str | None = None
    entity_category: TuyaEntityCategory | None = None
    entity_registry_enabled_default: bool = True
    icon: str | None = None
    translation_key: str | None = None
    translation_placeholders: dict[str, str] | None = None
