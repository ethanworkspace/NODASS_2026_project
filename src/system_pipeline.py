import csv
import json
from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt, degrees
from pathlib import Path
from statistics import mean, median


WATER_ROOT = Path("歷史品管、即時海氣象水文觀測資料") / "海保署"
METOCEAN_ROOT = Path("歷史品管、即時海氣象水文觀測資料")
METOCEAN_AGENCIES = ("CWA", "IHMT", "NAMR", "WRA")

POLLUTANT_GROUPS = {
    "chlorophyll": ["chlorophyll_a"],
    "nutrients": [
        "ammonia_nitrogen",
        "nitrate_nitrogen",
        "orthophosphate",
        "nitrite_nitrogen",
        "silicate",
    ],
    "suspended_solids": ["suspended_solid"],
    "heavy_metals": ["cadmium", "chromium", "copper", "zinc", "lead", "mercury"],
}

WATER_COLUMNS = {
    "測站編號": "station_id",
    "時間": "observed_at",
    "氣溫": "air_temperature",
    "鹽度": "salinity",
    "水溫": "water_temperature",
    "酸鹼值": "ph",
    "懸浮固體": "suspended_solid",
    "溶氧(電極法)": "dissolved_oxygen",
    "溶氧飽和度": "dissolved_oxygen_saturation",
    "葉綠素a": "chlorophyll_a",
    "氨氮": "ammonia_nitrogen",
    "硝酸鹽氮": "nitrate_nitrogen",
    "正磷酸鹽": "orthophosphate",
    "亞硝酸鹽氮": "nitrite_nitrogen",
    "矽酸鹽": "silicate",
    "鎘": "cadmium",
    "鉻": "chromium",
    "銅": "copper",
    "鋅": "zinc",
    "鉛": "lead",
    "汞": "mercury",
}

MET_COLUMNS = {
    "測站編號": "station_id",
    "時間": "observed_at",
    "風速": "wind_speed",
    "風向": "wind_direction",
    "流速": "current_speed",
    "流向": "current_direction",
    "潮高": "tide_height",
    "中心經度": "lon",
    "中心緯度": "lat",
}

SOURCE_RULES = [
    ("污水", "wastewater_treatment", ["ammonia_nitrogen", "orthophosphate", "nitrate_nitrogen"]),
    ("工業", "industrial", ["cadmium", "chromium", "copper", "zinc", "lead", "mercury"]),
    ("六輕", "industrial", ["cadmium", "chromium", "copper", "zinc", "lead", "mercury"]),
    ("火力", "industrial", ["copper", "zinc", "lead", "suspended_solid"]),
    ("發電", "industrial", ["copper", "zinc", "lead", "suspended_solid"]),
    ("港", "harbor", ["suspended_solid", "copper", "zinc", "lead"]),
    ("漁港", "harbor", ["suspended_solid", "ammonia_nitrogen", "orthophosphate"]),
    ("溪口", "river", ["suspended_solid", "ammonia_nitrogen", "nitrate_nitrogen", "orthophosphate"]),
    ("河口", "river", ["suspended_solid", "ammonia_nitrogen", "nitrate_nitrogen", "orthophosphate"]),
]

NODASS_API_REQUIREMENTS = [
    {
        "name": "GOCI satellite natural color image",
        "class_code": "GOCI",
        "kind": "Map Tile API",
        "priority": "中",
        "use_case": "事件當日海面影像背景，輔助判讀泥沙、雲遮與沿岸羽流位置。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/tiles/GOCI",
    },
    {
        "name": "Sentinel-3 natural color image",
        "class_code": "OLNT_S3",
        "kind": "Map Tile API",
        "priority": "中",
        "use_case": "補足 2017 年後自然色影像，作為事件視覺佐證。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/tiles/OLNT_S3",
    },
    {
        "name": "Sentinel-3 chlorophyll image",
        "class_code": "OLNT_S3_CHL",
        "kind": "KML image",
        "priority": "高",
        "use_case": "直接支援葉綠素 a 異常偵測與空間擴散範圍比對。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/OLNT_S3_CHL",
    },
    {
        "name": "Sentinel-3 total suspended materials image",
        "class_code": "OLNT_S3_TSM",
        "kind": "KML image",
        "priority": "高",
        "use_case": "直接支援懸浮固體異常與河口泥沙羽流判讀。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/OLNT_S3_TSM",
    },
    {
        "name": "Sentinel-2 chlorophyll image",
        "class_code": "Sentinel2_CHL",
        "kind": "KML image",
        "priority": "高",
        "use_case": "高解析度近岸葉綠素 a 影像，用於測站周邊空間一致性。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/Sentinel2_CHL",
    },
    {
        "name": "Sentinel-2 total suspended materials image",
        "class_code": "Sentinel2_TSM",
        "kind": "KML image",
        "priority": "高",
        "use_case": "高解析度近岸懸浮物影像，用於河口、港區與工業外海事件。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/Sentinel2_TSM",
    },
    {
        "name": "Sentinel-3 sea surface temperature image",
        "class_code": "SLNT_S3_SST",
        "kind": "KML image",
        "priority": "中",
        "use_case": "補足海溫壓力與水團邊界，輔助葉綠素與生態壓力判讀。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/SLNT_S3_SST",
    },
    {
        "name": "GOCI chlorophyll image",
        "class_code": "GOCI_CHL",
        "kind": "KML image",
        "priority": "高",
        "use_case": "高時間頻率葉綠素 a 歷史影像，用於 72 小時事件窗比對。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/GOCI_CHL",
    },
    {
        "name": "GOCI total suspended solids image",
        "class_code": "GOCI_TSS",
        "kind": "KML image",
        "priority": "高",
        "use_case": "高時間頻率懸浮固體歷史影像，用於污染羽流追蹤。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/GOCI_TSS",
    },
    {
        "name": "CMEMS sea surface height image",
        "class_code": "CMEMS_SSH",
        "kind": "KML image",
        "priority": "中",
        "use_case": "潮汐與海面高度背景，輔助傳輸方向與可達性評估。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/GOCI_SSH",
    },
    {
        "name": "Observation station information from the Central Meteorological Administration",
        "class_code": "CWA",
        "kind": "text/station data",
        "priority": "高",
        "use_case": "建立中央氣象署浮標、潮位、海氣象測站 metadata。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/CWA",
    },
    {
        "name": "Observation station information of the Transportation Technology Research Center",
        "class_code": "IHMT",
        "kind": "text/station data",
        "priority": "高",
        "use_case": "建立港研中心港區浮標與潮位站，支援港區來源追蹤。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/IHMT",
    },
    {
        "name": "Observation station information from the WaterResources Agency",
        "class_code": "WRA",
        "kind": "text/station data",
        "priority": "高",
        "use_case": "建立水利署潮位/河口相關測站，補強上游與潮位條件。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/WRA",
    },
    {
        "name": "Observation station information from National Academy of Marine Research",
        "class_code": "NAMR",
        "kind": "text/station data",
        "priority": "高",
        "use_case": "建立國海院浮標測站，補足近岸風浪流觀測。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/NAMR",
    },
    {
        "name": "Monitoring data from observation stations",
        "class_code": "OBS_DATA",
        "kind": "text/parameter value",
        "priority": "高",
        "use_case": "取得風速、風向、浪高、流速、流向、潮位與海溫，直接服務 72 小時時空一致性。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/{station_id}/data",
    },
    {
        "name": "Aquaculture Research Institute - Sea Temperature Satellite Cloud Image Files",
        "class_code": "TFRIN_SST",
        "kind": "PNG image",
        "priority": "中",
        "use_case": "補水試所海溫影像，輔助養殖區與生態壓力判讀。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/images/TFRIN_SST",
    },
    {
        "name": "Ministry of the Environment - Offshore Wind Farm Seabed Station Information",
        "class_code": "EPA/SM",
        "kind": "text/station data",
        "priority": "中",
        "use_case": "補離岸風場海床站位，支援工程活動與生態壓力評估。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/EPA/SM",
    },
    {
        "name": "Ministry of the Environment - Offshore Wind Farm Seawater Quality Station Information",
        "class_code": "EPA/MWQ",
        "kind": "text/station data",
        "priority": "高",
        "use_case": "補環境部離岸風場海水水質測站，納入水質異常背景。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/EPA/MWQ",
    },
    {
        "name": "Aquaculture Research Institute - Water Quality Station Information",
        "class_code": "TFRIN/MWQ",
        "kind": "text/station data",
        "priority": "中",
        "use_case": "補水試所水質採集點，支援養殖區與近岸水質比對。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/obs/stations/TFRIN/MWQ",
    },
    {
        "name": "Ocean Affairs Council - Taiwan National Park Marine Conservation Area",
        "class_code": "OCA/NPMPA",
        "kind": "Vector Data",
        "priority": "中",
        "use_case": "建立海洋保護區敏感受體圖層，排序污染風險與告警優先序。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/list/vector/OCA/NPMPA",
    },
    {
        "name": "Ministry of the Environment - Offshore Wind Farm Ecological Survey",
        "class_code": "EPA_ORGANISM",
        "kind": "Vector Data",
        "priority": "中",
        "use_case": "補離岸風場生態調查，作為生態壓力與受體敏感度資料。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/list/organism/project/EPA",
    },
    {
        "name": "Ocean Affairs Council - Outlying Islands Coast Photo Collection",
        "class_code": "VNCPO",
        "kind": "Vector Data",
        "priority": "低",
        "use_case": "作為海岸型態與事件報告輔助素材，非模型核心資料。",
        "endpoint": "https://nodass.namr.gov.tw/noapi/namr/v1/query/VNCPO",
    },
]

METHOD_EVALUATION = [
    {
        "method": "多測站時空貝氏異常偵測",
        "reference": "Contamination Event Detection Method Using Multi-Stations Temporal-Spatial Information Based on Bayesian Network",
        "score": 86,
        "current_support": "目前已具備異常事件、鄰近測站、72 小時事件窗與方向可達條件。",
        "reproduced_feature": "新增模型評估頁與升級節點，將單站異常擴充為多測站時空一致性框架。",
        "next_step": "建立 Bayesian Network 節點：事件、上游測站、上風測站、流向、潮位、污染物群組。",
    },
    {
        "method": "水動力 + Bayesian/MCMC 污染源反推",
        "reference": "Identification of pollution sources in rivers using a hydrodynamic diffusion wave model and improved Bayesian-MCMC algorithm",
        "score": 78,
        "current_support": "目前以平均流速、方向角與 72 小時可達距離做規則式近似。",
        "reproduced_feature": "新增漂流模擬升級欄位，標記哪些 NODASS 流場 API 可支援粒子追蹤。",
        "next_step": "接入格網流場後，將候選來源分數改為後驗機率與不確定區間。",
    },
    {
        "method": "主動式污染源追蹤 Agent",
        "reference": "Active Tracking of Marine Pollution Sources: An Uncertainty-Aware Categorical Bayesian Framework for USVs",
        "score": 72,
        "current_support": "目前 Agent 已能偵測異常後自動列出候選來源與資料缺口。",
        "reproduced_feature": "新增資料需求優先序，能指出下一個最該申請的 API 或資料層。",
        "next_step": "加入不確定度與下一站建議，讓 Agent 推薦下一個採樣/查詢點。",
    },
    {
        "method": "衛星葉綠素與懸浮物影像比對",
        "reference": "NODASS Sentinel/GOCI satellite derived products and coastal chlorophyll studies",
        "score": 90,
        "current_support": "NODASS API 已提供 Sentinel-2/3 與 GOCI 葉綠素、懸浮物影像。",
        "reproduced_feature": "新增 NODASS API 申請清單，將 CHL、TSM、SST、SSH 標為可補強模型的資料。",
        "next_step": "依事件日期抓取 ±72 小時影像，計算測站周邊影像像素異常。",
    },
]


def parse_time(value: str) -> datetime | None:
    value = (value or "").strip().strip('"')
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def parse_float(value: str) -> float | None:
    try:
        value = (value or "").strip()
        if value == "":
            return None
        return float(value)
    except ValueError:
        return None


def read_lonlat(folder: Path) -> tuple[float | None, float | None]:
    path = folder / "LonLat.csv"
    if not path.exists():
        return None, None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return None, None
    return parse_float(rows[0].get("CenterLongitude", "")), parse_float(rows[0].get("CenterLatitude", ""))


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius = 6371.0
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return radius * 2 * atan2(sqrt(a), sqrt(1 - a))


def bearing_degrees(source_lon: float, source_lat: float, target_lon: float, target_lat: float) -> float:
    lon1 = radians(source_lon)
    lon2 = radians(target_lon)
    lat1 = radians(source_lat)
    lat2 = radians(target_lat)
    delta_lon = lon2 - lon1
    x = sin(delta_lon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(delta_lon)
    return (degrees(atan2(x, y)) + 360) % 360


def angle_diff(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs((a - b + 180) % 360 - 180)


def direction_score(diff: float | None, tolerance: float = 75.0) -> float:
    if diff is None or diff > tolerance:
        return 0.0
    return round(1 - diff / tolerance, 4)


def circular_mean(values: list[float]) -> float | None:
    if not values:
        return None
    x = sum(cos(radians(v)) for v in values)
    y = sum(sin(radians(v)) for v in values)
    return (degrees(atan2(y, x)) + 360) % 360


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def pollutant_group(pollutant: str) -> str:
    for group, names in POLLUTANT_GROUPS.items():
        if pollutant in names:
            return group
    return "other"


def source_type_for_name(name: str) -> tuple[str, list[str]]:
    for keyword, source_type, expected in SOURCE_RULES:
        if keyword in name:
            return source_type, expected
    return "coastal_station", ["suspended_solid", "chlorophyll_a"]


def collect_stations(data_root: Path) -> list[dict[str, object]]:
    stations: list[dict[str, object]] = []
    water_root = data_root / WATER_ROOT
    for folder in sorted(p for p in water_root.iterdir() if p.is_dir()):
        lon, lat = read_lonlat(folder)
        stations.append(
            {
                "station_id": folder.name,
                "station_name": folder.name,
                "source_agency": "海保署",
                "station_type": "water_quality",
                "lon": lon,
                "lat": lat,
            }
        )
    for agency in METOCEAN_AGENCIES:
        agency_root = data_root / METOCEAN_ROOT / agency
        if not agency_root.exists():
            continue
        for folder in sorted(p for p in agency_root.iterdir() if p.is_dir()):
            lon, lat = read_lonlat(folder)
            stations.append(
                {
                    "station_id": f"{agency}_{folder.name}",
                    "station_name": folder.name,
                    "source_agency": agency,
                    "station_type": "metocean",
                    "lon": lon,
                    "lat": lat,
                }
            )
    return stations


def collect_source_candidates(water_stations: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for station in water_stations:
        name = str(station["station_name"])
        source_type, expected = source_type_for_name(name)
        if source_type == "coastal_station":
            continue
        candidates.append(
            {
                "source_id": f"SRC_{len(candidates) + 1:04d}",
                "source_name": name,
                "source_type": source_type,
                "lon": station["lon"],
                "lat": station["lat"],
                "known_pollutants": ";".join(expected),
                "data_basis": "由現有海保署測站名稱與座標建立的初版候選來源，需用官方污染源清冊校正",
            }
        )
    return candidates


def expected_pollutants_from_emi_items(items: set[str]) -> list[str]:
    mapping = [
        ("懸浮", "suspended_solid"),
        ("葉綠素", "chlorophyll_a"),
        ("氨氮", "ammonia_nitrogen"),
        ("硝酸", "nitrate_nitrogen"),
        ("亞硝酸", "nitrite_nitrogen"),
        ("磷", "orthophosphate"),
        ("鎘", "cadmium"),
        ("鉻", "chromium"),
        ("銅", "copper"),
        ("鋅", "zinc"),
        ("鉛", "lead"),
        ("汞", "mercury"),
    ]
    text = " ".join(items)
    matched = [target for keyword, target in mapping if keyword in text]
    return matched or ["ammonia_nitrogen", "orthophosphate", "suspended_solid"]


def read_moenv_discharge_sources(project_root: Path, start_index: int) -> list[dict[str, object]]:
    path = project_root / "data" / "external" / "moenv_ems_s_03.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        records = data.get("records") or data.get("result") or []
    elif isinstance(data, list):
        records = data
    else:
        records = []

    grouped: dict[str, dict[str, object]] = {}
    pollutant_items: dict[str, set[str]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        lon = parse_float(str(record.get("longitude", "")))
        lat = parse_float(str(record.get("latitude", "")))
        if lon is None or lat is None:
            continue
        key = f"{record.get('ems_no', '')}_{record.get('let', '')}_{lon:.6f}_{lat:.6f}"
        pollutant_items.setdefault(key, set()).add(str(record.get("emi_item", "")))
        if key in grouped:
            continue
        grouped[key] = {
            "source_name": f"{record.get('fac_name', '未命名事業')} {record.get('let', '')}".strip(),
            "source_type": "official_discharge",
            "lon": lon,
            "lat": lat,
            "official_id": record.get("ems_no", ""),
            "discharge_no": record.get("let", ""),
            "recipient_water": record.get("let_watertype", ""),
            "permit_no": record.get("per_no", ""),
            "permitted_water": record.get("per_water", ""),
            "data_basis": "環境部水污染源許可及申報資料 EMS_S_03 API",
        }

    sources: list[dict[str, object]] = []
    for offset, (key, source) in enumerate(grouped.items(), start=start_index):
        source["source_id"] = f"SRC_{offset:04d}"
        source["known_pollutants"] = ";".join(expected_pollutants_from_emi_items(pollutant_items.get(key, set())))
        sources.append(source)
    return sources


def read_fetch_status(project_root: Path) -> dict[str, object]:
    path = project_root / "data" / "external" / "fetch_status.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_rainfall_latest(project_root: Path) -> list[dict[str, object]]:
    path = project_root / "data" / "external" / "cwa_rainfall_latest.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    stations = data.get("cwaopendata", {}).get("dataset", {}).get("Station", [])
    rows: list[dict[str, object]] = []
    for station in stations:
        coords = station.get("GeoInfo", {}).get("Coordinates", [])
        wgs84 = next((item for item in coords if item.get("CoordinateName") == "WGS84"), None)
        if not wgs84:
            continue
        rain = station.get("RainfallElement", {})
        observed_raw = station.get("ObsTime", {}).get("DateTime", "")
        observed_at = parse_time(observed_raw.replace("T", " ").split("+")[0])
        rows.append(
            {
                "rain_station_id": station.get("StationId"),
                "rain_station_name": station.get("StationName"),
                "observed_at": observed_at,
                "lon": parse_float(wgs84.get("StationLongitude", "")),
                "lat": parse_float(wgs84.get("StationLatitude", "")),
                "county": station.get("GeoInfo", {}).get("CountyName"),
                "town": station.get("GeoInfo", {}).get("TownName"),
                "rain_1h": parse_float(rain.get("Past1hr", {}).get("Precipitation", "")),
                "rain_3h": parse_float(rain.get("Past3hr", {}).get("Precipitation", "")),
                "rain_6h": parse_float(rain.get("Past6hr", {}).get("Precipitation", "")),
                "rain_12h": parse_float(rain.get("Past12hr", {}).get("Precipitation", "")),
                "rain_24h": parse_float(rain.get("Past24hr", {}).get("Precipitation", "")),
            }
        )
    return rows


def nearest_rainfall_station(
    event: dict[str, object], rainfall_rows: list[dict[str, object]]
) -> dict[str, object] | None:
    event_lon = event.get("lon")
    event_lat = event.get("lat")
    if not isinstance(event_lon, float) or not isinstance(event_lat, float):
        return None
    nearest = None
    nearest_distance = 999999.0
    for row in rainfall_rows:
        lon = row.get("lon")
        lat = row.get("lat")
        if not isinstance(lon, float) or not isinstance(lat, float):
            continue
        distance = haversine_km(lon, lat, event_lon, event_lat)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest = dict(row)
            nearest["distance_km"] = round(distance, 3)
    return nearest


def read_water_quality(data_root: Path) -> list[dict[str, object]]:
    observations: list[dict[str, object]] = []
    for data_file in sorted((data_root / WATER_ROOT).glob("*/*.csv")):
        if data_file.name.lower() == "lonlat.csv":
            continue
        station_name = data_file.parent.name
        lon, lat = read_lonlat(data_file.parent)
        with data_file.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if len(rows) < 4:
            continue
        header = rows[0]
        mapped = [WATER_COLUMNS.get(col, col) for col in header]
        for raw in rows[3:]:
            if len(raw) != len(mapped):
                continue
            row = dict(zip(mapped, raw))
            observed_at = parse_time(row.get("observed_at", ""))
            if observed_at is None:
                continue
            item: dict[str, object] = {
                "station_id": row.get("station_id") or station_name,
                "station_name": station_name,
                "observed_at": observed_at,
                "lon": lon,
                "lat": lat,
            }
            for field in [name for names in POLLUTANT_GROUPS.values() for name in names]:
                item[field] = parse_float(row.get(field, ""))
            observations.append(item)
    return observations


def detect_anomaly_events(observations: list[dict[str, object]], limit: int = 30) -> list[dict[str, object]]:
    values_by_pollutant: dict[str, list[float]] = {}
    for obs in observations:
        for pollutant in [name for names in POLLUTANT_GROUPS.values() for name in names]:
            value = obs.get(pollutant)
            if isinstance(value, float):
                values_by_pollutant.setdefault(pollutant, []).append(value)

    baselines: dict[str, tuple[float, float, float]] = {}
    for pollutant, values in values_by_pollutant.items():
        if len(values) < 8:
            continue
        base = median(values)
        deviations = [abs(v - base) for v in values]
        mad_scale = median(deviations) * 1.4826
        iqr_scale = (percentile(values, 0.75) - percentile(values, 0.25)) / 1.349
        scale = max(mad_scale, iqr_scale, abs(base) * 0.1, 0.01)
        high_gate = percentile(values, 0.9)
        baselines[pollutant] = (base, scale, high_gate)

    events: list[dict[str, object]] = []
    for obs in observations:
        for pollutant, (base, scale, high_gate) in baselines.items():
            value = obs.get(pollutant)
            if not isinstance(value, float):
                continue
            score = (value - base) / scale
            if score < 3.5 or value < high_gate:
                continue
            events.append(
                {
                    "event_id": f"EVT_{len(events) + 1:04d}",
                    "station_id": obs["station_id"],
                    "station_name": obs["station_name"],
                    "detected_at": obs["observed_at"],
                    "pollutant_group": pollutant_group(pollutant),
                    "pollutant_name": pollutant,
                        "observed_value": value,
                        "baseline_value": round(base, 4),
                    "anomaly_score": round(score, 4),
                    "anomaly_method": "全域中位數_MAD",
                    "lon": obs["lon"],
                    "lat": obs["lat"],
                }
            )
    events.sort(key=lambda item: float(item["anomaly_score"]), reverse=True)
    return events[:limit]


def nearest_metocean_stations(
    event: dict[str, object], met_stations: list[dict[str, object]], limit: int = 6
) -> list[dict[str, object]]:
    event_lon = event.get("lon")
    event_lat = event.get("lat")
    if not isinstance(event_lon, float) or not isinstance(event_lat, float):
        return []
    with_distance = []
    for station in met_stations:
        lon = station.get("lon")
        lat = station.get("lat")
        if not isinstance(lon, float) or not isinstance(lat, float):
            continue
        distance = haversine_km(lon, lat, event_lon, event_lat)
        copy = dict(station)
        copy["distance_km"] = distance
        with_distance.append(copy)
    return sorted(with_distance, key=lambda item: float(item["distance_km"]))[:limit]


def met_folder(data_root: Path, station: dict[str, object]) -> Path:
    return data_root / METOCEAN_ROOT / str(station["source_agency"]) / str(station["station_name"])


def summarize_metocean_window(
    data_root: Path,
    event: dict[str, object],
    met_stations: list[dict[str, object]],
    rainfall_rows: list[dict[str, object]],
) -> dict[str, object]:
    event_time = event["detected_at"]
    assert isinstance(event_time, datetime)
    start = event_time - timedelta(hours=72)
    end = event_time + timedelta(hours=72)
    wind_dirs: list[float] = []
    current_dirs: list[float] = []
    current_speeds: list[float] = []
    tide_values: list[float] = []
    rows = 0
    used_station_names: list[str] = []

    for station in met_stations:
        folder = met_folder(data_root, station)
        files = list(folder.glob(f"qc/{event_time.year}.csv")) + list(
            folder.glob(f"realtime/{event_time.year}.csv")
        )
        station_rows = 0
        for path in files:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                source_rows = list(reader)
            if len(source_rows) < 4:
                continue
            header = [MET_COLUMNS.get(col, col) for col in source_rows[0]]
            for raw in source_rows[3:]:
                if len(raw) != len(header):
                    continue
                row = dict(zip(header, raw))
                observed_at = parse_time(row.get("observed_at", ""))
                if observed_at is None or observed_at < start or observed_at > end:
                    continue
                station_rows += 1
                rows += 1
                for key, target in (
                    ("wind_direction", wind_dirs),
                    ("current_direction", current_dirs),
                    ("current_speed", current_speeds),
                    ("tide_height", tide_values),
                ):
                    value = parse_float(row.get(key, ""))
                    if value is not None:
                        target.append(value)
        if station_rows:
            used_station_names.append(str(station["station_name"]))

    tide_range = None
    if tide_values:
        tide_range = round(max(tide_values) - min(tide_values), 4)
    nearest_rain = nearest_rainfall_station(event, rainfall_rows)
    rain_status = "未接入雨量資料"
    rain_station = None
    rain_distance = None
    rain_24h = None
    if nearest_rain:
        rain_station = nearest_rain.get("rain_station_name")
        rain_distance = nearest_rain.get("distance_km")
        rain_24h = nearest_rain.get("rain_24h")
        rain_time = nearest_rain.get("observed_at")
        if isinstance(rain_time, datetime) and start <= rain_time <= end:
            rain_status = "雨量時間落在 72 小時事件窗內"
        else:
            rain_status = "已接入即時雨量，但時間不屬於此歷史事件窗"
    return {
        "window_start": start,
        "window_end": end,
        "meteo_rows": rows,
        "used_metocean_stations": ";".join(used_station_names),
        "dominant_wind_direction": circular_mean(wind_dirs),
        "dominant_current_direction": circular_mean(current_dirs),
        "mean_current_speed": mean(current_speeds) if current_speeds else None,
        "tide_range": tide_range,
        "nearest_rain_station": rain_station,
        "rain_station_distance_km": rain_distance,
        "rain_24h": rain_24h,
        "rain_status": rain_status,
    }


def rank_sources(
    event: dict[str, object], window: dict[str, object], candidates: list[dict[str, object]]
) -> list[dict[str, object]]:
    event_lon = event.get("lon")
    event_lat = event.get("lat")
    if not isinstance(event_lon, float) or not isinstance(event_lat, float):
        return []
    ranked: list[dict[str, object]] = []
    for source in candidates:
        lon = source.get("lon")
        lat = source.get("lat")
        if not isinstance(lon, float) or not isinstance(lat, float):
            continue
        distance = haversine_km(lon, lat, event_lon, event_lat)
        source_to_event = bearing_degrees(lon, lat, event_lon, event_lat)
        event_to_source = bearing_degrees(event_lon, event_lat, lon, lat)
        wind_dir = window.get("dominant_wind_direction")
        current_dir = window.get("dominant_current_direction")
        upwind_score = direction_score(angle_diff(event_to_source, wind_dir))
        current_score = direction_score(angle_diff(source_to_event, current_dir))
        speed = window.get("mean_current_speed")
        travel_km = float(speed) * 259.2 if isinstance(speed, float) else 0.0
        reachable = distance <= max(travel_km, 3.0)
        expected = str(source.get("known_pollutants", "")).split(";")
        pollutant_match = 1.0 if event["pollutant_name"] in expected else 0.25
        distance_score = max(0.0, 1 - distance / 60.0)

        # 時空一致性：不符合 72 小時可達且沒有上風/上游流向支持者排除。
        if not reachable and upwind_score == 0 and current_score == 0:
            continue
        score = (
            distance_score * 0.25
            + upwind_score * 0.2
            + current_score * 0.25
            + pollutant_match * 0.2
            + (1.0 if reachable else 0.0) * 0.1
        )
        ranked.append(
            {
                "event_id": event["event_id"],
                "source_id": source["source_id"],
                "source_name": source["source_name"],
                "source_type": source["source_type"],
                "distance_km": round(distance, 3),
                "bearing_to_event": round(source_to_event, 1),
                "reachable_within_72h": reachable,
                "upwind_score": round(upwind_score, 4),
                "upstream_current_score": round(current_score, 4),
                "pollutant_match_score": pollutant_match,
                "source_score": round(score, 4),
                "confidence_level": "高" if score >= 0.7 else "中" if score >= 0.45 else "低",
                "explanation": "通過 72 小時時空一致性篩選",
            }
        )
    return sorted(ranked, key=lambda item: float(item["source_score"]), reverse=True)[:5]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            safe = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    safe[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    safe[key] = value
            writer.writerow(safe)


def write_external_catalog(project_root: Path) -> None:
    rows = [
        {
            "資料集": "雨量觀測站-雨量資料",
            "提供機關": "交通部中央氣象署",
            "用途": "補足異常事件前後 72 小時降雨條件",
            "網址": "https://opendata.cwa.gov.tw/user/authkey",
            "狀態": "已串接，需設定 CWA_API_KEY",
        },
        {
            "資料集": "水污染源許可及申報資料 EMS_S_03",
            "提供機關": "環境部",
            "用途": "校正事業放流口、排放污染物、排放量與承受水體",
            "網址": "https://data.moenv.gov.tw/api/v2/EMS_S_03",
            "狀態": "已串接，需設定 MOENV_API_KEY",
        },
        {
            "資料集": "FHY 河川與流域資料",
            "提供機關": "經濟部水利署",
            "用途": "補足河川水位與逕流支持度",
            "網址": "https://fhy.wra.gov.tw/Api",
            "狀態": "待申請 WRA_API_KEY",
        },
        {
            "資料集": "中央氣象署海象資料",
            "提供機關": "交通部中央氣象署",
            "用途": "補足浮標、潮位、風浪流觀測",
            "網址": "https://ocean.cwa.gov.tw/V2/data_interface/datasets",
            "狀態": "待會員登入或下載權限",
        },
        {
            "資料集": "NODASS 國家海洋資料庫",
            "提供機關": "國家海洋研究院",
            "用途": "補足海流、風場、波浪、海溫、鹽度、葉綠素與 AIS",
            "網址": "https://nodass.namr.gov.tw/data",
            "狀態": "待登入或資料申請",
        },
    ]
    write_csv(
        project_root / "data" / "external" / "external_data_catalog.csv",
        rows,
        ["資料集", "提供機關", "用途", "網址", "狀態"],
    )


def build_dashboard(
    project_root: Path,
    events: list[dict[str, object]],
    rankings: list[dict[str, object]],
    sources: list[dict[str, object]],
    windows: list[dict[str, object]],
    rainfall_rows: list[dict[str, object]],
) -> None:
    top_event = events[0] if events else {}
    top_rankings = [r for r in rankings if r.get("event_id") == top_event.get("event_id")][:5]
    rows_html = "\n".join(
        "<tr>"
        f"<td>{event['event_id']}</td><td>{event['station_name']}</td>"
        f"<td>{event['detected_at'].strftime('%Y-%m-%d %H:%M')}</td>"
        f"<td>{event['pollutant_name']}</td><td>{event['observed_value']}</td>"
        f"<td>{event['anomaly_score']}</td>"
        "</tr>"
        for event in events[:10]
    )
    ranking_html = "\n".join(
        "<tr>"
        f"<td>{row['source_name']}</td><td>{row['source_type']}</td>"
        f"<td>{row['distance_km']}</td><td>{'是' if row['reachable_within_72h'] else '否'}</td>"
        f"<td>{row['source_score']}</td><td>{row['confidence_level']}</td>"
        "</tr>"
        for row in top_rankings
    )
    window_by_event = {row["event_id"]: row for row in windows}
    top_window = window_by_event.get(top_event.get("event_id"), {})
    top_wind = top_window.get("dominant_wind_direction")
    top_current = top_window.get("dominant_current_direction")
    top_speed = top_window.get("mean_current_speed")
    payload = {
        "events": [
            {k: (v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v) for k, v in e.items()}
            for e in events
        ],
        "rankings": rankings,
        "windows": [
            {k: (v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v) for k, v in w.items()}
            for w in windows
        ],
        "sources": sources,
        "rainfall_station_count": len(rainfall_rows),
        "official_discharge_source_count": len(
            [source for source in sources if source.get("source_type") == "official_discharge"]
        ),
        "external_status": read_fetch_status(project_root),
        "method_evaluation": METHOD_EVALUATION,
        "nodass_api_requirements": NODASS_API_REQUIREMENTS,
    }
    (project_root / "dashboard" / "system_data.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return
    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NODASS 初版系統</title>
  <style>
    body {{ margin:0; font-family:"Microsoft JhengHei", "Noto Sans TC", Arial, sans-serif; background:#f5f7f8; color:#1a252b; }}
    .layout {{ display:grid; grid-template-columns:250px 1fr; min-height:100vh; }}
    aside {{ background:#10363d; color:white; padding:24px 18px; }}
    .brand {{ font-size:20px; font-weight:800; line-height:1.35; margin-bottom:24px; }}
    nav div {{ padding:10px 12px; border-radius:8px; margin-bottom:8px; color:#d8ebed; }}
    nav .active {{ background:#1f545d; color:white; }}
    main {{ padding:26px; }}
    h1 {{ margin:0 0 8px; font-size:28px; }}
    h2 {{ font-size:19px; margin:0 0 14px; }}
    .muted {{ color:#61727a; line-height:1.6; }}
    .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:20px 0; }}
    .card, section {{ background:white; border:1px solid #d8e1e5; border-radius:8px; padding:16px; }}
    .value {{ font-size:28px; font-weight:800; }}
    .label {{ color:#61727a; font-size:14px; margin-bottom:8px; }}
    .grid {{ display:grid; grid-template-columns:1.25fr .9fr; gap:18px; align-items:start; }}
    .full {{ grid-column:1 / -1; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th, td {{ border-bottom:1px solid #d8e1e5; padding:10px 8px; text-align:right; white-space:nowrap; }}
    th:first-child, td:first-child {{ text-align:left; }}
    th {{ color:#61727a; background:#f8fafb; }}
    .badge {{ display:inline-block; padding:4px 9px; border-radius:999px; background:#006d77; color:white; font-size:12px; }}
    .warn {{ background:#fff6e4; border:1px solid #ead39b; padding:12px; border-radius:8px; color:#6d4d08; margin-top:14px; }}
    @media (max-width:960px) {{ .layout,.grid,.stats {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <div class="brand">NODASS<br>污染來源追蹤 AI</div>
      <nav>
        <div class="active">總覽</div>
        <div>異常事件</div>
        <div>來源追蹤</div>
        <div>時空一致性</div>
        <div>資料補齊</div>
      </nav>
    </aside>
    <main>
      <h1>初版系統執行結果</h1>
      <p class="muted">系統已完成水質異常偵測、候選來源建立、72 小時海氣象事件窗分析與時空一致性來源篩選。</p>
      <div class="stats">
        <div class="card"><div class="label">異常事件</div><div class="value">{len(events)}</div></div>
        <div class="card"><div class="label">候選來源</div><div class="value">{len(sources)}</div></div>
        <div class="card"><div class="label">來源排序結果</div><div class="value">{len(rankings)}</div></div>
        <div class="card"><div class="label">時空窗</div><div class="value">±72h</div></div>
      </div>
      <div class="grid">
        <section>
          <h2>前 10 筆異常事件</h2>
          <table>
            <thead><tr><th>事件</th><th>測站</th><th>時間</th><th>污染物</th><th>實測值</th><th>異常分數</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </section>
        <section>
          <h2>最高異常事件來源排序</h2>
          <p class="muted">事件：{top_event.get('event_id', '無')}，測站：{top_event.get('station_name', '無')}</p>
          <table>
            <thead><tr><th>候選來源</th><th>類型</th><th>距離 km</th><th>72h 可達</th><th>分數</th><th>信心</th></tr></thead>
            <tbody>{ranking_html}</tbody>
          </table>
          <div class="warn">時空一致性規則：僅保留事件前後 72 小時內，符合上風、上游流向或流速距離可達條件的候選來源。</div>
        </section>
        <section class="full">
          <h2>最高異常事件的 72 小時事件窗</h2>
          <table>
            <thead><tr><th>事件窗開始</th><th>事件窗結束</th><th>海氣象筆數</th><th>主導風向</th><th>主導流向</th><th>平均流速</th><th>潮差</th><th>最近雨量站</th><th>雨量狀態</th></tr></thead>
            <tbody><tr>
              <td>{top_window.get('window_start', '')}</td>
              <td>{top_window.get('window_end', '')}</td>
              <td>{top_window.get('meteo_rows', '')}</td>
              <td>{round(top_wind, 1) if isinstance(top_wind, float) else ''}</td>
              <td>{round(top_current, 1) if isinstance(top_current, float) else ''}</td>
              <td>{round(top_speed, 3) if isinstance(top_speed, float) else ''}</td>
              <td>{top_window.get('tide_range', '')}</td>
              <td>{top_window.get('nearest_rain_station', '')}</td>
              <td>{top_window.get('rain_status', '')}</td>
            </tr></tbody>
          </table>
        </section>
        <section class="full">
          <h2>外部資料串接狀態</h2>
          <table>
            <thead><tr><th>資料</th><th>狀態</th><th>系統用途</th></tr></thead>
            <tbody>
              <tr><td>中央氣象署雨量資料</td><td><span class="badge">已下載並解析 {len(rainfall_rows)} 站</span></td><td>配對最近雨量站，檢查是否落在 72 小時事件窗</td></tr>
              <tr><td>水利署水位與河川站況</td><td><span class="badge">官方服務暫時不可用</span></td><td>後續補足河川水位、流量與逕流支持度</td></tr>
              <tr><td>環境部水污染源許可及申報資料</td><td><span class="badge">待授權或匯入檔</span></td><td>校正正式放流口、排放污染物與排放量</td></tr>
            </tbody>
          </table>
        </section>
      </div>
    </main>
  </div>
</body>
</html>
"""
    dashboard_path = project_root / "dashboard" / "index.html"
    dashboard_path.write_text(html, encoding="utf-8")


def run_initial_system(data_root: Path, project_root: Path) -> dict[str, int]:
    processed = project_root / "data" / "processed"
    reports = project_root / "reports"
    stations = collect_stations(data_root)
    water_stations = [s for s in stations if s["station_type"] == "water_quality"]
    met_stations = [s for s in stations if s["station_type"] == "metocean"]
    sources = collect_source_candidates(water_stations)
    sources.extend(read_moenv_discharge_sources(project_root, len(sources) + 1))
    rainfall_rows = read_rainfall_latest(project_root)
    observations = read_water_quality(data_root)
    events = detect_anomaly_events(observations)

    windows: list[dict[str, object]] = []
    rankings: list[dict[str, object]] = []
    for event in events:
        nearest = nearest_metocean_stations(event, met_stations)
        window = summarize_metocean_window(data_root, event, nearest, rainfall_rows)
        window["event_id"] = event["event_id"]
        windows.append(window)
        rankings.extend(rank_sources(event, window, sources))

    write_csv(
        processed / "stations.csv",
        stations,
        ["station_id", "station_name", "source_agency", "station_type", "lon", "lat"],
    )
    write_csv(
        processed / "source_candidates.csv",
        sources,
        [
            "source_id",
            "source_name",
            "source_type",
            "lon",
            "lat",
            "known_pollutants",
            "data_basis",
            "official_id",
            "discharge_no",
            "recipient_water",
            "permit_no",
            "permitted_water",
        ],
    )
    write_csv(
        processed / "anomaly_events.csv",
        events,
        [
            "event_id",
            "station_id",
            "station_name",
            "detected_at",
            "pollutant_group",
            "pollutant_name",
            "observed_value",
            "baseline_value",
            "anomaly_score",
            "anomaly_method",
            "lon",
            "lat",
        ],
    )
    write_csv(
        processed / "event_time_windows.csv",
        windows,
        [
            "event_id",
            "window_start",
            "window_end",
            "meteo_rows",
            "used_metocean_stations",
            "dominant_wind_direction",
            "dominant_current_direction",
            "mean_current_speed",
            "tide_range",
            "nearest_rain_station",
            "rain_station_distance_km",
            "rain_24h",
            "rain_status",
        ],
    )
    write_csv(
        processed / "rainfall_latest.csv",
        rainfall_rows,
        [
            "rain_station_id",
            "rain_station_name",
            "observed_at",
            "lon",
            "lat",
            "county",
            "town",
            "rain_1h",
            "rain_3h",
            "rain_6h",
            "rain_12h",
            "rain_24h",
        ],
    )
    write_csv(
        processed / "source_ranking_results.csv",
        rankings,
        [
            "event_id",
            "source_id",
            "source_name",
            "source_type",
            "distance_km",
            "bearing_to_event",
            "reachable_within_72h",
            "upwind_score",
            "upstream_current_score",
            "pollutant_match_score",
            "source_score",
            "confidence_level",
            "explanation",
        ],
    )
    write_external_catalog(project_root)
    build_dashboard(project_root, events, rankings, sources, windows, rainfall_rows)
    summary = {
        "stations": len(stations),
        "sources": len(sources),
        "observations": len(observations),
        "events": len(events),
        "windows": len(windows),
        "rankings": len(rankings),
        "rainfall_stations": len(rainfall_rows),
    }
    (reports / "system_run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary
