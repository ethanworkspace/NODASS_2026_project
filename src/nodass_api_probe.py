import json
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NODASS_PROBE_URLS = [
    ("OLNT_S3_CHL", "Sentinel-3 chlorophyll image", "2021-03-01", "2021-03-02", "high", "images/OLNT_S3_CHL?date1=2021-03-01&date2=2021-03-02"),
    ("OLNT_S3_CHL", "Sentinel-3 chlorophyll image", "2020-01-01", "2020-03-02", "high", "images/OLNT_S3_CHL?date1=2020-01-01&date2=2020-03-02"),
    ("OLNT_S3_TSM", "Sentinel-3 total suspended materials image", "2021-03-01", "2021-03-02", "high", "images/OLNT_S3_TSM?date1=2021-03-01&date2=2021-03-02"),
    ("OLNT_S3_TSM", "Sentinel-3 total suspended materials image", "2020-01-01", "2020-03-02", "high", "images/OLNT_S3_TSM?date1=2020-01-01&date2=2020-03-02"),
    ("Sentinel2_CHL", "Sentinel-2 chlorophyll image", "2021-03-01", "2021-03-02", "high", "images/Sentinel2_CHL?date1=2021-03-01&date2=2021-03-02"),
    ("Sentinel2_CHL", "Sentinel-2 chlorophyll image", "2020-01-01", "2020-03-02", "high", "images/Sentinel2_CHL?date1=2020-01-01&date2=2020-03-02"),
    ("Sentinel2_TSM", "Sentinel-2 total suspended materials image", "2021-03-01", "2021-03-02", "high", "images/Sentinel2_TSM?date1=2021-03-01&date2=2021-03-02"),
    ("Sentinel2_TSM", "Sentinel-2 total suspended materials image", "2020-01-01", "2020-03-02", "high", "images/Sentinel2_TSM?date1=2020-01-01&date2=2020-03-02"),
    ("GOCI_CHL", "GOCI chlorophyll image", "2021-03-01", "2021-03-02", "high", "images/GOCI_CHL?date1=2021-03-01&date2=2021-03-02"),
    ("GOCI_CHL", "GOCI chlorophyll image", "2020-01-01", "2020-03-02", "high", "images/GOCI_CHL?date1=2020-01-01&date2=2020-03-02"),
    ("GOCI_TSS", "GOCI total suspended solids image", "2021-03-01", "2021-03-02", "high", "images/GOCI_TSS?date1=2021-03-01&date2=2021-03-02"),
    ("GOCI_TSS", "GOCI total suspended solids image", "2020-01-01", "2020-03-02", "high", "images/GOCI_TSS?date1=2020-01-01&date2=2020-03-02"),
    ("CWA", "Observation station information from the Central Meteorological Administration", "", "", "high", "obs/stations/CWA"),
    ("IHMT", "Observation station information of the Transportation Technology Research Center", "", "", "high", "obs/stations/IHMT"),
    ("WRA", "Observation station information from the WaterResources Agency", "", "", "high", "obs/stations/WRA"),
    ("NAMR", "Observation station information from National Academy of Marine Research", "", "", "high", "obs/stations/NAMR"),
    ("Vector_NAMR_FB_35A0003", "Monitoring data from observation stations", "2026-09-11", "2026-09-12", "high", "obs/Vector_NAMR_FB_35A0003/data?date1=2026-09-11&date2=2026-09-12"),
    ("EPA/MWQ", "Ministry of the Environment - Offshore Wind Farm Seawater Quality Station Information", "", "", "high", "obs/stations/EPA/MWQ"),
    ("GOCI", "GOCI satellite natural color image", "2021-03-01", "2021-03-02", "medium", "tiles/GOCI?date1=2021-03-01&date2=2021-03-02"),
    ("GOCI", "GOCI satellite natural color image", "2020-01-01", "2020-03-02", "medium", "tiles/GOCI?date1=2020-01-01&date2=2020-03-02"),
    ("OLNT_S3", "Sentinel-3 natural color image", "2021-03-01", "2021-03-02", "medium", "tiles/OLNT_S3?date1=2021-03-01&date2=2021-03-02"),
    ("OLNT_S3", "Sentinel-3 natural color image", "2020-01-01", "2020-03-02", "medium", "tiles/OLNT_S3?date1=2020-01-01&date2=2020-03-02"),
    ("SLNT_S3_SST", "Sentinel-3 sea surface temperature image", "2021-03-01", "2021-03-02", "medium", "images/SLNT_S3_SST?date1=2021-03-01&date2=2021-03-02"),
    ("SLNT_S3_SST", "Sentinel-3 sea surface temperature image", "2020-01-01", "2020-03-02", "medium", "images/SLNT_S3_SST?date1=2020-01-01&date2=2020-03-02"),
    ("GOCI_SSH", "GOCI sea surface height image", "2021-03-01", "2021-03-02", "medium", "images/GOCI_SSH?date1=2021-03-01&date2=2021-03-02"),
    ("GOCI_SSH", "GOCI sea surface height image", "2020-01-01", "2020-03-02", "medium", "images/GOCI_SSH?date1=2020-01-01&date2=2020-03-02"),
]


def summarize_payload(payload: object) -> dict[str, object]:
    if isinstance(payload, list):
        sample = payload[0] if payload else {}
        return {"record_count": len(payload), "sample_keys": sorted(sample.keys())[:12] if isinstance(sample, dict) else []}
    if isinstance(payload, dict):
        count = None
        for key in ("features", "data", "records", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                count = len(value)
                break
        return {"record_count": count, "sample_keys": sorted(payload.keys())[:12]}
    return {"record_count": None, "sample_keys": []}


def probe_nodass_apis(project_root: Path) -> dict[str, object]:
    base_url = "https://nodass.namr.gov.tw/noapi/namr/v1/"
    results = []
    for code, name, date1, date2, priority, path in NODASS_PROBE_URLS:
        url = base_url + path
        result: dict[str, object] = {
            "code": code,
            "name": name,
            "date1": date1,
            "date2": date2,
            "priority": "高" if priority == "high" else "中",
            "url": url,
        }
        try:
            request = Request(url, headers={"Accept": "application/json"})
            with urlopen(request, timeout=30) as response:
                raw = response.read(2_000_000)
                text = raw.decode("utf-8-sig", errors="replace")
                result["http_status"] = response.status
                result["content_type"] = response.headers.get("Content-Type", "")
                result["bytes_sampled"] = len(raw)
                try:
                    payload = json.loads(text)
                    result.update(summarize_payload(payload))
                    result["status"] = "可讀取"
                except json.JSONDecodeError:
                    result["record_count"] = None
                    result["sample_keys"] = []
                    result["status"] = "可讀取但非 JSON"
        except HTTPError as exc:
            result.update({"http_status": exc.code, "status": f"HTTP {exc.code}", "record_count": None, "sample_keys": []})
        except (URLError, TimeoutError) as exc:
            result.update({"http_status": None, "status": str(exc), "record_count": None, "sample_keys": []})
        results.append(result)

    summary = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "NODASS noapi/namr/v1",
        "total": len(results),
        "readable": len([row for row in results if row.get("status") in ("可讀取", "可讀取但非 JSON")]),
        "results": results,
    }
    output_dir = project_root / "data" / "external"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "nodass_api_probe.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
