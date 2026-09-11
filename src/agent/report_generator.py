from pathlib import Path


def write_event_report(output_path: Path, event: dict[str, object], ranked_sources: list[dict[str, object]]) -> None:
    """輸出簡潔的 Markdown 異常事件報告。"""
    lines = [
        f"# 異常事件 {event.get('event_id', 'unknown')}",
        "",
        f"- 測站：{event.get('station_id')}",
        f"- 時間：{event.get('detected_at')}",
        f"- 污染物：{event.get('pollutant_name')}",
        f"- 異常分數：{event.get('anomaly_score')}",
        "",
        "## 候選來源",
    ]
    for source in ranked_sources:
        lines.append(
            f"- {source.get('source_name', source.get('source_id'))}: "
            f"{source.get('source_score', source.get('posterior_probability', 'n/a'))}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
