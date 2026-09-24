from __future__ import annotations

from pathlib import Path

import pandas as pd

COLUMN_MAP = {
    "Type": "type",
    "Air temperature [K]": "air_temperature",
    "Process temperature [K]": "process_temperature",
    "Rotational speed [rpm]": "rotational_speed",
    "Torque [Nm]": "torque",
    "Tool wear [min]": "tool_wear",
    "Machine failure": "machine_failure",
    "TWF": "twf",
    "HDF": "hdf",
    "PWF": "pwf",
    "OSF": "osf",
    "RNF": "rnf",
}
FAILURE_MODE_COLUMNS = ["twf", "hdf", "pwf", "osf", "rnf"]


def load_dataset(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path).rename(columns=COLUMN_MAP)
    required = set(COLUMN_MAP.values())
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset missing expected columns: {sorted(missing)}")
    return frame


def validate_dataset(frame: pd.DataFrame) -> dict[str, object]:
    subtype_any = frame[FAILURE_MODE_COLUMNS].max(axis=1)
    inconsistent = int((subtype_any != frame["machine_failure"]).sum())
    return {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "missing_values": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "failure_count": int(frame["machine_failure"].sum()),
        "failure_rate": float(frame["machine_failure"].mean()),
        "failure_mode_target_inconsistencies": inconsistent,
        "type_distribution": frame["type"].value_counts().sort_index().to_dict(),
        "failure_modes": frame[FAILURE_MODE_COLUMNS].sum().astype(int).to_dict(),
    }
