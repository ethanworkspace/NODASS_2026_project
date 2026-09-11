from pathlib import Path

import pandas as pd


METOCEAN_COLUMNS = {
    "測站編號": "station_id",
    "時間": "observed_at",
    "陣風_風速": "wind_gust_speed",
    "風速": "wind_speed",
    "風向": "wind_direction",
    "氣壓": "air_pressure",
    "氣溫": "air_temperature",
    "海面溫度": "sea_temperature",
    "示性波高": "wave_height_significant",
    "平均週期": "wave_mean_period",
    "波向": "wave_main_direction",
    "波浪尖峰週期": "wave_peak_period",
    "流速": "current_speed",
    "分層流速{深度:流速}": "current_speed_layer",
    "流向": "current_direction",
    "分層流向{深度:流向}": "current_direction_layer",
    "潮高": "tide_height",
    "中心經度": "lon",
    "中心緯度": "lat",
}


def load_metocean_csv(path: Path) -> pd.DataFrame:
    """Load one metocean CSV, skipping English-name and unit rows."""
    frame = pd.read_csv(path, encoding="utf-8-sig", skiprows=[1, 2])
    frame = frame.rename(columns=METOCEAN_COLUMNS)
    frame["observed_at"] = pd.to_datetime(frame["observed_at"], errors="coerce")
    numeric_columns = [
        c
        for c in frame.columns
        if c not in {"station_id", "observed_at", "current_speed_layer", "current_direction_layer"}
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame

