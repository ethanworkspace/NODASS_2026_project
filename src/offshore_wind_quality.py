import json
from collections import Counter
from pathlib import Path


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def _record_groups(document: object) -> list[tuple[str, list[dict[str, object]]]]:
    if not isinstance(document, dict):
        return []
    element = document.get("DocumentElement", {})
    if not isinstance(element, dict):
        return []
    groups = []
    for name, rows in element.items():
        valid_rows = [row for row in _as_list(rows) if isinstance(row, dict)]
        if valid_rows:
            groups.append((name, valid_rows))
    return groups


def read_offshore_wind_quality_summary(project_root: Path) -> dict[str, object]:
    root = project_root / "data" / "external" / "offshore_wind_water_quality" / "expanded"
    if not root.exists():
        return {
            "available": False,
            "message": "尚未匯入離岸風電海域水質資料",
            "dataset_count": 0,
            "record_count": 0,
            "sampling_site_count": 0,
            "item_count": 0,
            "top_items": [],
            "top_sites": [],
            "datasets": [],
        }

    item_counter: Counter[str] = Counter()
    site_counter: Counter[str] = Counter()
    dataset_summaries: list[dict[str, object]] = []
    dates: list[str] = []
    total_records = 0

    for path in sorted(root.rglob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        for dataset_name, rows in _record_groups(document):
            total_records += len(rows)
            local_items: Counter[str] = Counter()
            local_sites: Counter[str] = Counter()
            for row in rows:
                item = str(row.get("檢測項目", "")).strip()
                site = str(row.get("採樣地點", "")).strip()
                date = str(row.get("日期(起)", "")).strip()
                if item:
                    item_counter[item] += 1
                    local_items[item] += 1
                if site:
                    site_counter[site] += 1
                    local_sites[site] += 1
                if date:
                    dates.append(date)
            dataset_summaries.append(
                {
                    "dataset_name": dataset_name,
                    "record_count": len(rows),
                    "top_items": [{"name": key, "count": value} for key, value in local_items.most_common(5)],
                    "top_sites": [{"name": key, "count": value} for key, value in local_sites.most_common(5)],
                }
            )

    return {
        "available": True,
        "message": "已匯入使用者提供的離岸風電海域水質資料",
        "dataset_count": len(dataset_summaries),
        "record_count": total_records,
        "sampling_site_count": len(site_counter),
        "item_count": len(item_counter),
        "date_min": min(dates) if dates else "",
        "date_max": max(dates) if dates else "",
        "top_items": [{"name": key, "count": value} for key, value in item_counter.most_common(12)],
        "top_sites": [{"name": key, "count": value} for key, value in site_counter.most_common(10)],
        "datasets": sorted(dataset_summaries, key=lambda item: int(item["record_count"]), reverse=True)[:10],
    }
