import argparse
from pathlib import Path

from src.external_fetch import fetch_external_sources
from src.ingestion.audit import audit_data_root
from src.nodass_api_probe import probe_nodass_apis
from src.system_pipeline import run_initial_system


def audit(data_root: Path) -> None:
    """列出原始 NODASS 資料夾的快速盤點結果。"""
    summary = audit_data_root(data_root)
    report_lines = [
        "# NODASS 資料盤點結果",
        "",
        f"- 原始資料位置：{data_root}",
        "",
        "| 資料來源 | 測站資料夾 | CSV 檔案 | 估計資料筆數 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for item in summary:
        report_lines.append(
            f"| {item['source']} | {item['station_dirs']} | "
            f"{item['csv_files']} | {item['estimated_rows']} |"
        )
        print(
            f"{item['source']}：{item['station_dirs']} 個測站資料夾，"
            f"{item['csv_files']} 個 CSV 檔，約 {item['estimated_rows']} 筆資料"
        )
    report_path = Path("reports") / "data_audit_result.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"已輸出資料盤點報告：{report_path}")


def build_stations(data_root: Path) -> None:
    """建立測站中繼資料。"""
    print(f"將使用此資料來源建立測站資料：{data_root}")


def detect_anomalies(data_root: Path) -> None:
    """執行水質異常偵測流程。"""
    print(f"將使用此資料來源執行異常偵測：{data_root}")


def run_system(data_root: Path) -> None:
    """執行初版系統，產生異常事件、時空窗與來源排序結果。"""
    summary = run_initial_system(data_root=data_root, project_root=Path.cwd())
    print("初版系統執行完成")
    print(f"測站數：{summary['stations']}")
    print(f"候選來源數：{summary['sources']}")
    print(f"水質觀測筆數：{summary['observations']}")
    print(f"異常事件數：{summary['events']}")
    print(f"時空事件窗數：{summary['windows']}")
    print(f"來源排序結果數：{summary['rankings']}")
    print(f"雨量站串接數：{summary.get('rainfall_stations', 0)}")
    print("已更新 dashboard/index.html")


def fetch_external() -> None:
    """更新中央氣象署、環境部與水利署外部資料。"""
    status = fetch_external_sources(project_root=Path.cwd())
    print("外部資料更新完成")
    for name, item in status.get("sources", {}).items():
        print(f"{name}：{item.get('message')}")


def probe_nodass() -> None:
    """探測 NODASS API 服務狀態。"""
    summary = probe_nodass_apis(project_root=Path.cwd())
    print("NODASS API 探測完成")
    print(f"探測端點：{summary['total']}")
    print(f"可讀取端點：{summary['readable']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NODASS 海岸生態壓力與污染來源追蹤 AI 工具。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name in ("audit", "build-stations", "detect-anomalies", "run-system"):
        command_parser = subparsers.add_parser(command_name)
        command_parser.add_argument("--data-root", required=True, type=Path)
    subparsers.add_parser("fetch-external")
    subparsers.add_parser("probe-nodass")

    args = parser.parse_args()
    if args.command == "audit":
        audit(args.data_root)
    elif args.command == "build-stations":
        build_stations(args.data_root)
    elif args.command == "detect-anomalies":
        detect_anomalies(args.data_root)
    elif args.command == "run-system":
        run_system(args.data_root)
    elif args.command == "fetch-external":
        fetch_external()
    elif args.command == "probe-nodass":
        probe_nodass()


if __name__ == "__main__":
    main()
