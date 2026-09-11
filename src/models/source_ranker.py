import pandas as pd


def rule_based_source_score(candidates: pd.DataFrame) -> pd.DataFrame:
    """Score candidate sources with transparent MVP weights."""
    scored = candidates.copy()
    scored["source_score"] = (
        scored.get("distance_score", 0) * 0.25
        + scored.get("upwind_score", 0) * 0.2
        + scored.get("upstream_current_score", 0) * 0.25
        + scored.get("pollutant_match_score", 0) * 0.2
        + scored.get("hydrology_score", 0) * 0.1
    )
    return scored.sort_values("source_score", ascending=False)

