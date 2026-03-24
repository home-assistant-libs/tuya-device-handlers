"""Test constants for tuya-device-handlers."""

import glob

DEVICE_FIXTURES = [
    fixture_filename
    for fixture_filename in glob.glob(
        "*.json", root_dir="tests/fixtures/devices"
    )
    if fixture_filename
    not in {
        "cl_zah67ekd.json",
        "cs_zibqa9dutqyaxym2.json",
        "cz_guitoc9iylae4axs.json",
        "cz_PGEkBctAbtzKOZng.json",
        "dj_mki13ie507rlry4r.json",
        "kt_5wnlzekkstwcdsvm.json",
        "mal_gyitctrjj1kefxp2.json",
        "sd_i6hyjg3af7doaswm.json",
        "sd_lr33znaodtyarrrz.json",
        "sfkzq_ed7frwissyqrejic.json",
        "sp_rudejjigkywujjvs.json",
        "sp_sdd5f5f2dl5wydjf.json",
        "wk_B0eP8qYAdpUo4yR9.json",
    }
]
