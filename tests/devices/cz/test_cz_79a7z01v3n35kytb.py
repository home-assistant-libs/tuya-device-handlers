"""Regression checks for the Double Digital Meter quirk fixture."""

import ast
import json
from pathlib import Path


def test_double_digital_meter_fixture():
    root = Path(__file__).resolve().parents[3]
    fixture = json.loads((root / "tests/fixtures/devices/cz_79a7z01v3n35kytb.json").read_text())
    assert fixture["category"] == "cz"
    assert fixture["product_id"] == "79a7z01v3n35kytb"
    assert not fixture["function"]
    assert not fixture["status_range"]
    assert not fixture["local_strategy"]
    assert "id" not in fixture
    assert "terminal_id" not in fixture


def test_double_digital_meter_quirk_defines_expected_dps():
    root = Path(__file__).resolve().parents[3]
    path = root / "src/tuya_device_handlers/devices/cz/cz_79a7z01v3n35kytb.py"
    tree = ast.parse(path.read_text())
    codes = {kw.value.value for node in ast.walk(tree) if isinstance(node, ast.Call)
             for kw in node.keywords if kw.arg == "dpcode" and isinstance(kw.value, ast.Constant)}
    assert codes == {
        "device_state1", "device_state2", "cur_power1", "cur_power2",
        "cur_current1", "cur_current2", "cur_voltage1", "cur_voltage2",
        "total_energy1", "total_energy2", "today_acc_energy1",
        "today_acc_energy2", "warn_power1", "warn_power2", "all_energy",
    }
