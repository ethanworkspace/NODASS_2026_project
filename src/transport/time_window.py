import pandas as pd


def event_window(
    observations: pd.DataFrame,
    event_time: pd.Timestamp,
    time_column: str = "observed_at",
    hours: int = 72,
) -> pd.DataFrame:
    """Return observations within +/- hours around an event."""
    start = event_time - pd.Timedelta(hours=hours)
    end = event_time + pd.Timedelta(hours=hours)
    return observations[(observations[time_column] >= start) & (observations[time_column] <= end)]

