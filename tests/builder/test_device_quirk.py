"""Tests for DatapointDefinition and DeviceQuirk."""

import json
import pathlib

import pytest
from tuya_sharing import (
    CustomerDevice,
    DeviceFunction,
    DeviceStatusRange,
    Manager,
)

from tuya_device_handlers.builder.device_quirk import (
    DatapointDefinition,
    DeviceQuirk,
    LocalConvertStrategy,
)
from tuya_device_handlers.const import DPMode, DPType
from tuya_device_handlers.registry import QuirksRegistry


def test_datapoint_definition_to_function() -> None:
    """to_function builds a DeviceFunction from the definition."""
    definition = DatapointDefinition(
        dpid=1,
        dpcode="x",
        dpmode=DPMode.READ | DPMode.WRITE,
        dptype=DPType.INTEGER,
        values='{"unit": "%"}',
    )
    function = definition.to_function()
    assert function.code == "x"
    assert function.type == DPType.INTEGER.value
    assert function.values == '{"unit": "%"}'


def test_datapoint_definition_to_local_strategy() -> None:
    """to_local_strategy builds the LocalStrategy dict for the device."""
    definition = DatapointDefinition(
        dpid=2,
        dpcode="y",
        dpmode=DPMode.READ,
        dptype=DPType.STRING,
        values="{}",
    )
    strategy = definition.to_local_strategy("my_product")
    assert strategy["status_code"] == "y"
    assert strategy["config_item"]["pid"] == "my_product"
    assert strategy["config_item"]["valueType"] == DPType.STRING.value
    assert json.loads(strategy["config_item"]["statusFormat"]) == {"y": "$"}


def test_datapoint_definition_to_status_range() -> None:
    """to_status_range builds a DeviceStatusRange from the definition."""
    definition = DatapointDefinition(
        dpid=3,
        dpcode="z",
        dpmode=DPMode.READ,
        dptype=DPType.BOOLEAN,
        values="{}",
    )
    status_range = definition.to_status_range()
    assert status_range.code == "z"
    assert status_range.type == DPType.BOOLEAN.value
    assert status_range.values == "{}"


def test_device_quirk_provenance() -> None:
    """quirk_file/quirk_file_line capture the calling site."""
    quirk = DeviceQuirk()
    assert isinstance(quirk.quirk_file, pathlib.Path)
    assert quirk.quirk_file.name == "test_device_quirk.py"
    assert quirk.quirk_file_line > 0


def test_add_dpid_bitmap() -> None:
    """add_dpid_bitmap stores a Bitmap definition with label range."""
    quirk = DeviceQuirk().add_dpid_bitmap(
        dpid=1, dpcode="bm", dpmode=DPMode.READ, label_range=["a", "b"]
    )
    definition = quirk._datapoint_definitions[(1, "bm")]
    assert definition is not None
    assert definition.dptype is DPType.BITMAP
    assert json.loads(definition.values or "")["label"] == ["a", "b"]


def test_add_dpid_boolean() -> None:
    """add_dpid_boolean stores a Boolean definition."""
    quirk = DeviceQuirk().add_dpid_boolean(
        dpid=2, dpcode="bo", dpmode=DPMode.WRITE
    )
    definition = quirk._datapoint_definitions[(2, "bo")]
    assert definition is not None
    assert definition.dptype is DPType.BOOLEAN


def test_add_dpid_enum() -> None:
    """add_dpid_enum stores an Enum definition with the range."""
    quirk = DeviceQuirk().add_dpid_enum(
        dpid=3, dpcode="en", dpmode=DPMode.READ, enum_range=["scene", "auto"]
    )
    definition = quirk._datapoint_definitions[(3, "en")]
    assert definition is not None
    assert definition.dptype is DPType.ENUM
    assert json.loads(definition.values or "")["range"] == ["scene", "auto"]


def test_add_dpid_integer() -> None:
    """add_dpid_integer stores an Integer definition incl. report_type."""
    quirk = DeviceQuirk().add_dpid_integer(
        dpid=4,
        dpcode="i",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=0,
        max=100,
        scale=1,
        step=1,
        report_type="sum",
    )
    definition = quirk._datapoint_definitions[(4, "i")]
    assert definition is not None
    assert definition.dptype is DPType.INTEGER
    assert definition.report_type == "sum"
    payload = json.loads(definition.values or "")
    assert payload == {"unit": "%", "min": 0, "max": 100, "scale": 1, "step": 1}


def test_remove_dpid() -> None:
    """remove_dpid stores None to mark the dpid for removal."""
    quirk = DeviceQuirk().remove_dpid(dpid=5, dpcode="rm")
    assert quirk._datapoint_definitions[(5, "rm")] is None


def test_override_category() -> None:
    """override_category stores the new category on the quirk."""
    quirk = DeviceQuirk().override_category("kg")
    assert quirk._override_category == "kg"


def test_set_dpid_strategy_to_enum() -> None:
    """set_dpid_strategy_to_enum stores an enum LocalConvertStrategy."""
    quirk = DeviceQuirk().set_dpid_strategy_to_enum(
        dpid=1,
        dpcode="x",
        enum_mapping_map={"on": True, "off": False},
    )
    strategy = quirk._local_strategy[(1, "x")]
    assert isinstance(strategy, LocalConvertStrategy)
    assert strategy.value_convert == "enum"
    assert strategy.enum_mapping_map == {
        "on": {"value": True},
        "off": {"value": False},
    }


def test_remove_dpid_strategy() -> None:
    """remove_dpid_strategy stores None to mark the strategy for removal."""
    quirk = DeviceQuirk().remove_dpid_strategy(dpid=2, dpcode="y")
    assert quirk._local_strategy[(2, "y")] is None


def test_initialise_device_read_and_write_with_local(
    mock_device: CustomerDevice,
) -> None:
    """READ adds status_range; WRITE adds function."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    quirk = DeviceQuirk().add_dpid_integer(
        dpid=1,
        dpcode="x",
        dpmode=DPMode.READ | DPMode.WRITE,
        unit="%",
        min=0,
        max=100,
        scale=1,
        step=1,
    )
    quirk.initialise_device(mock_device)
    assert "x" in mock_device.status_range
    assert "x" in mock_device.function
    assert 1 in mock_device.local_strategy


def test_initialise_device_read_only_no_local(
    mock_device: CustomerDevice,
) -> None:
    """No WRITE: function popped. support_local=False: local_strategy popped."""
    mock_device.support_local = False
    mock_device.local_strategy = {2: {"some": "thing"}}
    mock_device.function["y"] = DeviceFunction(
        code="y", type="Boolean", values="{}"
    )
    quirk = DeviceQuirk().add_dpid_boolean(
        dpid=2, dpcode="y", dpmode=DPMode.READ
    )
    quirk.initialise_device(mock_device)
    assert "y" in mock_device.status_range
    assert "y" not in mock_device.function
    assert 2 not in mock_device.local_strategy


def test_initialise_device_write_only_clears_status_range(
    mock_device: CustomerDevice,
) -> None:
    """No READ: status_range popped (in case the cloud already had it)."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    mock_device.status_range["w"] = DeviceStatusRange(
        code="w", type="Boolean", values="{}"
    )
    quirk = DeviceQuirk().add_dpid_boolean(
        dpid=3, dpcode="w", dpmode=DPMode.WRITE
    )
    quirk.initialise_device(mock_device)
    assert "w" not in mock_device.status_range
    assert "w" in mock_device.function


def test_initialise_device_local_strategy_enum_with_local(
    mock_device: CustomerDevice,
) -> None:
    """set_dpid_strategy_to_enum writes the enum strategy to local_strategy."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    quirk = (
        DeviceQuirk()
        .add_dpid_boolean(dpid=1, dpcode="x", dpmode=DPMode.READ)
        .set_dpid_strategy_to_enum(
            dpid=1,
            dpcode="x",
            enum_mapping_map={"on": True, "off": False},
        )
    )
    quirk.initialise_device(mock_device)
    strategy = mock_device.local_strategy[1]
    assert strategy["value_convert"] == "enum"
    assert strategy["status_code"] == "x"
    assert strategy["config_item"]["enumMappingMap"] == {
        "on": {"value": True},
        "off": {"value": False},
    }
    assert strategy["config_item"]["valueType"] == DPType.BOOLEAN.value


def test_initialise_device_local_strategy_enum_no_local(
    mock_device: CustomerDevice,
) -> None:
    """Without support_local, the enum strategy is not applied."""
    mock_device.support_local = False
    mock_device.local_strategy = {}
    quirk = DeviceQuirk().set_dpid_strategy_to_enum(
        dpid=1, dpcode="x", enum_mapping_map={"on": True}
    )
    quirk.initialise_device(mock_device)
    assert 1 not in mock_device.local_strategy


def test_initialise_device_remove_dpid_strategy(
    mock_device: CustomerDevice,
) -> None:
    """remove_dpid_strategy pops the dpid from local_strategy."""
    mock_device.support_local = True
    mock_device.local_strategy = {1: {"some": "thing"}}
    quirk = DeviceQuirk().remove_dpid_strategy(dpid=1, dpcode="x")
    quirk.initialise_device(mock_device)
    assert 1 not in mock_device.local_strategy


def test_mqtt_enum_strategy_mapping(
    mock_device: CustomerDevice, mock_manager: Manager
) -> None:
    """_on_device_report maps raw enum values via the enum strategy."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    quirk = (
        DeviceQuirk()
        .add_dpid_boolean(dpid=1, dpcode="x", dpmode=DPMode.READ)
        .set_dpid_strategy_to_enum(
            dpid=1,
            dpcode="x",
            enum_mapping_map={"on": True, "off": False},
        )
    )
    quirk.initialise_device(mock_device)
    mock_manager.device_map[mock_device.id] = mock_device

    assert "x" not in mock_device.status

    # Trigger mqtt updates
    mock_manager._on_device_report(
        mock_device.id,
        [{"dpId": 1, "t": 1752456620499, "value": "off"}],
    )
    assert mock_device.status["x"] is False

    mock_manager._on_device_report(
        mock_device.id,
        [{"dpId": 1, "t": 1752456620499, "value": "on"}],
    )
    assert mock_device.status["x"] is True

    # Unmapped raw value falls back to the Boolean default (False).
    mock_manager._on_device_report(
        mock_device.id,
        [{"dpId": 1, "t": 1752456620499, "value": True}],
    )
    assert mock_device.status["x"] is False


def test_initialise_device_none_definition_removes_everything(
    mock_device: CustomerDevice,
) -> None:
    """remove_dpid: function, strategy, status all popped."""
    mock_device.support_local = True
    mock_device.local_strategy = {7: {"some": "thing"}}
    mock_device.function["g"] = DeviceFunction(
        code="g", type="Boolean", values="{}"
    )
    mock_device.status["g"] = True
    mock_device.status_range["g"] = DeviceStatusRange(
        code="g", type="Boolean", values="{}"
    )
    quirk = DeviceQuirk().remove_dpid(dpid=7, dpcode="g")
    quirk.initialise_device(mock_device)
    assert "g" not in mock_device.function
    assert 7 not in mock_device.local_strategy
    assert "g" not in mock_device.status
    assert "g" not in mock_device.status_range


def test_initialise_device_override_category(
    mock_device: CustomerDevice,
) -> None:
    """initialise_device remaps device.category when an override is set."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    mock_device.category = "original"
    quirk = DeviceQuirk().override_category("kg")
    quirk.initialise_device(mock_device)
    assert mock_device.category == "kg"


def test_initialise_device_without_override_category(
    mock_device: CustomerDevice,
) -> None:
    """initialise_device leaves device.category alone without an override."""
    mock_device.support_local = True
    mock_device.local_strategy = {}
    mock_device.category = "original"
    quirk = DeviceQuirk()
    quirk.initialise_device(mock_device)
    assert mock_device.category == "original"


def test_applies_to_records_manufacturer_and_model() -> None:
    """applies_to stores manufacturer and model as readable attributes."""
    quirk = DeviceQuirk().applies_to(
        product_id="abc",
        manufacturer="Acme",
        model="Widget",
        model_id="Wid-1",
    )
    assert quirk.manufacturer == "Acme"
    assert quirk.model == "Widget"
    assert quirk.model_id == "Wid-1"


def test_applies_to_called_twice_raises() -> None:
    """Calling applies_to a second time raises ValueError."""
    quirk = DeviceQuirk().applies_to(product_id="abc")
    with pytest.raises(ValueError, match="already has an applies_to condition"):
        quirk.applies_to(product_id="def")


def test_register_without_applies_to_raises() -> None:
    """Register raises ValueError when applies_to was never called."""
    quirk = DeviceQuirk()
    with pytest.raises(
        ValueError, match="does not have an applies_to condition"
    ):
        quirk.register(QuirksRegistry())
