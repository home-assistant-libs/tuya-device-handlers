"""Test device-level quirk initialisation."""

from tests import create_device
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
    mode_func = device.function.get("mode")
    assert mode_func is not None
    assert '"range":["nature","sleep"]' in mode_func.values
    assert "normal" not in mode_func.values

    countdown_func = device.function.get("countdown_set")
    assert countdown_func is not None
    assert '"range":["cancel","1h","2h","3h","4h","5h","6h"]' in (
        countdown_func.values
    )
    assert "12h" not in countdown_func.values

    # APPLY quirk
    filled_quirks_registry.initialise_device_quirk(device)

    # AFTER quirk: verify expanded enum ranges
    mode_func = device.function.get("mode")
    assert mode_func is not None
    assert '"range": ["normal", "nature", "sleep"]' in mode_func.values

    countdown_func = device.function.get("countdown_set")
    assert countdown_func is not None
    expected_countdown_range = (
        '"range": ["cancel", "1h", "2h", "3h", "4h", "5h", "6h", '
        '"7h", "8h", "9h", "10h", "11h", "12h"]'
    )
    assert expected_countdown_range in countdown_func.values
