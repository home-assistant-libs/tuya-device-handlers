"""Tests for the 68nvbio9 cover position quirk.

Tuya blind motor (product_id 68nvbio9) reports percent_state in HA
convention (0=closed, 100=open).  Without the quirk the default
DPCodeInvertedPercentageWrapper incorrectly inverts position values.

See https://github.com/home-assistant/core/issues/159800.
"""

from tests import create_device
from tests.integration_helpers.cover import get_cover_default_definitions
from tuya_device_handlers.device_wrapper.extended import (
    DPCodeInvertedPercentageWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information_ex import (
    InvertedIntegerTypeInformationEx,
)


def test_default_definitions_without_quirk() -> None:
    """Without quirk, 68nvbio9 uses DPCodeInvertedPercentageWrapper."""
    device = create_device("cl_68nvbio9.json")
    definitions = get_cover_default_definitions(device)
    assert len(definitions) == 1
    wrapper = definitions["control"].current_position_wrapper
    assert isinstance(wrapper, DPCodeInvertedPercentageWrapper)


def test_quirk_applies_inverted_type_information(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, percent_state uses InvertedIntegerTypeInformationEx."""
    device = create_device("cl_68nvbio9.json")
    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert isinstance(wrapper, DPCodeInvertedPercentageWrapper)
    assert isinstance(
        wrapper.type_information, InvertedIntegerTypeInformationEx
    )


def test_quirk_corrects_position_read(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, percent_state=52 reads as 52 (not inverted to 48)."""
    device = create_device("cl_68nvbio9.json")
    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.read_device_status(device) == 52


def test_quirk_corrects_position_write(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """With quirk, setting position 70 sends raw value 70 (not 30)."""
    device = create_device("cl_68nvbio9.json")
    filled_quirks_registry.initialise_device_quirk(device)
    definitions = get_cover_default_definitions(device)
    wrapper = definitions["control"].current_position_wrapper
    assert wrapper is not None
    assert wrapper.get_update_commands(device, 70) == [
        {"code": "percent_state", "value": 70}
    ]
