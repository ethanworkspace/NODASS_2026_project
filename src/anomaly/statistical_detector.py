import pandas as pd


def detect_group_anomalies(
    observations: pd.DataFrame,
    value_columns: list[str],
    station_column: str = "station_id",
    time_column: str = "observed_at",
    zscore_threshold: float = 3.0,
) -> pd.DataFrame:
    """Detect simple station-level z-score anomalies for MVP validation."""
    events: list[dict[str, object]] = []
    for station_id, station_frame in observations.groupby(station_column):
        for value_column in value_columns:
            series = station_frame[value_column].dropna()
            if len(series) < 8:
                continue
            mean = series.mean()
            std = series.std()
            if not std:
                continue
            scored = station_frame[[time_column, value_column]].dropna().copy()
            scored["anomaly_score"] = (scored[value_column] - mean) / std
            flagged = scored[scored["anomaly_score"] >= zscore_threshold]
            for _, row in flagged.iterrows():
                events.append(
                    {
                        "station_id": station_id,
                        "detected_at": row[time_column],
                        "pollutant_name": value_column,
                        "observed_value": row[value_column],
                        "baseline_value": mean,
                        "anomaly_score": row["anomaly_score"],
                        "anomaly_method": "station_zscore",
                    }
                )
    return pd.DataFrame(events)

