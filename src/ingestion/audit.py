from pathlib import Path


METOCEAN_ROOT = "歷史品管、即時海氣象水文觀測資料"


def audit_data_root(data_root: Path) -> list[dict[str, object]]:
    """Return a compact inventory for agencies under the metocean/water-quality root."""
    root = data_root / METOCEAN_ROOT
    if not root.exists():
        raise FileNotFoundError(f"Missing data folder: {root}")

    summary: list[dict[str, object]] = []
    for agency_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        station_dirs = [p for p in agency_dir.iterdir() if p.is_dir()]
        csv_files = [p for p in agency_dir.rglob("*.csv") if p.name.lower() != "lonlat.csv"]
        estimated_rows = 0
        for csv_file in csv_files:
            try:
                with csv_file.open("r", encoding="utf-8-sig", errors="ignore") as handle:
                    estimated_rows += max(sum(1 for _ in handle) - 1, 0)
            except OSError:
                continue
        summary.append(
            {
                "source": agency_dir.name,
                "station_dirs": len(station_dirs),
                "csv_files": len(csv_files),
                "estimated_rows": estimated_rows,
            }
        )
    return summary

