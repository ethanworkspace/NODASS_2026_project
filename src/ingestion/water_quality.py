from pathlib import Path

import pandas as pd


WATER_QUALITY_COLUMNS = {
    "測站編號": "station_id",
    "時間": "observed_at",
    "氣溫": "air_temperature",
    "鹽度": "salinity",
    "水溫": "water_temperature",
    "酸鹼值": "ph",
    "懸浮固體": "suspended_solid",
    "溶氧(電極法)": "dissolved_oxygen",
    "溶氧飽和度": "dissolved_oxygen_saturation",
    "葉綠素a": "chlorophyll_a",
    "氨氮": "ammonia_nitrogen",
    "硝酸鹽氮": "nitrate_nitrogen",
    "正磷酸鹽": "orthophosphate",
    "亞硝酸鹽氮": "nitrite_nitrogen",
    "矽酸鹽": "silicate",
    "鎘": "cadmium",
    "鉻": "chromium",
    "銅": "copper",
    "鋅": "zinc",
    "鉛": "lead",
    "汞": "mercury",
}


def load_water_quality_csv(path: Path) -> pd.DataFrame:
    """Load one OCA water quality CSV, skipping English-name and unit rows."""
    frame = pd.read_csv(path, encoding="utf-8-sig", skiprows=[1, 2])
    frame = frame.rename(columns=WATER_QUALITY_COLUMNS)
    frame["observed_at"] = pd.to_datetime(frame["observed_at"], errors="coerce")
    numeric_columns = [c for c in frame.columns if c not in {"station_id", "observed_at"}]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame

