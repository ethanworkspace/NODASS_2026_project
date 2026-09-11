import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CWA_RAINFALL_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0002-001"
MOENV_EMS_URL = "https://data.moenv.gov.tw/api/v2/EMS_S_03"
WRA_BASIN_URL = "https://fhy.wra.gov.tw/OpenApiv3/v2/Basic/Basin"


def _read_json(url: str, headers: dict[str, str] | None = None, timeout: int = 40) -> tuple[bool, object, str]:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8-sig")
        return True, json.loads(payload), "成功"
    except HTTPError as exc:
        return False, {}, f"HTTP {exc.code}"
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, {}, str(exc)


def fetch_external_sources(project_root: Path, moenv_limit: int = 1000) -> dict[str, object]:
    """下載可由目前授權取得的外部資料；授權碼只從環境變數讀取。"""
    output_dir = project_root / "data" / "external"
    output_dir.mkdir(parents=True, exist_ok=True)

    status: dict[str, object] = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sources": {},
    }

    cwa_key = os.getenv("CWA_API_KEY", "").strip()
    if cwa_key:
        url = f"{CWA_RAINFALL_URL}?{urlencode({'Authorization': cwa_key, 'format': 'JSON'})}"
        ok, data, message = _read_json(url, {"Accept": "application/json", "Accept-Encoding": "gzip"})
        status["sources"]["cwa_rainfall"] = {"ok": ok, "message": message}
        if ok:
            (output_dir / "cwa_rainfall_latest.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    else:
        status["sources"]["cwa_rainfall"] = {"ok": False, "message": "未設定 CWA_API_KEY"}

    moenv_key = os.getenv("MOENV_API_KEY", "").strip()
    if moenv_key:
        url = f"{MOENV_EMS_URL}?{urlencode({'api_key': moenv_key, 'limit': moenv_limit, 'format': 'json'})}"
        ok, data, message = _read_json(url, {"Accept": "application/json"})
        status["sources"]["moenv_ems_s_03"] = {"ok": ok, "message": message}
        if ok:
            (output_dir / "moenv_ems_s_03.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    else:
        status["sources"]["moenv_ems_s_03"] = {"ok": False, "message": "未設定 MOENV_API_KEY"}

    wra_key = os.getenv("WRA_API_KEY", "").strip()
    if wra_key:
        url = f"{WRA_BASIN_URL}?{urlencode({'$top': 15})}"
        ok, data, message = _read_json(url, {"Accept": "application/json", "apikey": wra_key})
        status["sources"]["wra_basin"] = {"ok": ok, "message": message}
        if ok:
            (output_dir / "wra_basin_sample.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    else:
        status["sources"]["wra_basin"] = {"ok": False, "message": "未設定 WRA_API_KEY"}

    (output_dir / "fetch_status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return status
