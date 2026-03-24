"""Test constants for tuya-device-handlers."""

import glob

DEVICE_FIXTURES = [
    fixture_filename
    for fixture_filename in glob.glob(
        "*.json", root_dir="tests/fixtures/devices"
    )
    if fixture_filename
    not in {
        "cz_PGEkBctAbtzKOZng.json",
        "sd_i6hyjg3af7doaswm.json",
        "sfkzq_ed7frwissyqrejic.json",
        "sp_rudejjigkywujjvs.json",
    }
]
