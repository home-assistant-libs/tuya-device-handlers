"""Test device-level quirk initialisation."""

from tests import create_device
from tests.integration_helpers.fan import get_fan_default_definition
from tests.integration_helpers.select import get_select_default_definitions
from tuya_device_handlers.registry import QuirksRegistry


def test_quirk_overrides(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """CZTF423S tower fan has limited enum ranges.

    The device's mode enum is missing "normal" and countdown_set only
    supports up to 6h. The quirk expands both to their full range.
    """
    device = create_device("fs_xwv3jifdbhbolgh3.json")

    # BEFORE quirk: verify limited enum ranges
    fan_definition = get_fan_default_definition(device)
    assert fan_definition is not None
    assert fan_definition.mode_wrapper is not None
    assert fan_definition.mode_wrapper.options == ["nature", "sleep"]
    select_defininitions = get_select_default_definitions(device)
    assert select_defininitions is not None
    countdown_definition = select_defininitions.get("countdown_set")
    assert countdown_definition is not None
    assert countdown_definition.select_wrapper.options == [
        "cancel",
        "1h",
        "2h",
        "3h",
        "4h",
        "5h",
        "6h",
    ]

    # APPLY quirk
    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER quirk: verify expanded enum ranges
    fan_definition = get_fan_default_definition(device)
    assert fan_definition is not None
    assert fan_definition.mode_wrapper is not None
    assert fan_definition.mode_wrapper.options == ["normal", "nature", "sleep"]
    select_defininitions = get_select_default_definitions(device)
    assert select_defininitions is not None
    countdown_definition = select_defininitions.get("countdown_set")
    assert countdown_definition is not None
    assert countdown_definition.select_wrapper.options == [
        "cancel",
        "1h",
        "2h",
        "3h",
        "4h",
        "5h",
        "6h",
        "7h",
        "8h",
        "9h",
        "10h",
        "11h",
        "12h",
    ]
