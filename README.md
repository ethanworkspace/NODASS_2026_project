# 台灣海岸汙染監測系統

本專案重新製作為「台灣海岸汙染監測系統」，用於監測台灣海岸是否發生水質汙染事件；若判定發生汙染，系統會依事件日前後 72 小時內的海氣象條件，預測汙染可能擴散到哪裡。系統以透明可檢核的規則式模型作為初版核心，並保留後續升級為貝氏網路、因果推論、時序分類與粒子漂流模型的工程架構。

展示網站：

https://nodass-coastal-source-tracing-ai.workspace-787619.chatgpt.site

GitHub：

https://github.com/ethanworkspace/NODASS_2026_project

## 目前功能

### 1. 汙染事件監測

- 偵測葉綠素 a、營養鹽、懸浮固體與重金屬異常。
- 使用中位數與 MAD/IQR 穩健尺度建立初版異常分數。
- 事件表會列出測站、時間、汙染物、實測值、基準值與異常分數。

### 2. 72 小時時空一致性

- 每個汙染事件自動建立事件日前後 72 小時事件窗。
- 只使用事件窗內的海氣象、水文與影像查詢條件。
- 擴散預測使用順流、下風與可達距離做判斷。
- 事件窗外資料不納入模型判斷，避免用不同水文條件混合解釋同一汙染事件。

### 3. 汙染擴散預測

- 依主導流向、主導風向與平均流速建立 72 小時擴散軌跡。
- 軌跡以 12 小時為間距輸出，包含經緯度、方向與距離。
- 系統會比對沿岸參考點，列出可能受影響區域與風險等級。
- 目前模型為初版方向性預測，不等同正式海洋數值模式。

### 4. 互動式地圖

- 前端接入 Leaflet 地圖模組。
- 預設底圖使用 OpenStreetMap，無需 API key。
- 地圖可平移、縮放、開關圖層，並點選事件點、擴散軌跡與可能受影響區域查看細節。
- 若外部地圖模組暫時無法載入，系統會回到內建台灣海岸示意圖，避免畫面空白。
- 第一屏即顯示汙染狀態、72 小時預測距離、受影響區域與地圖，不再需要先閱讀說明頁。

### 5. NODASS 影像佐證

- 依汙染物群組推薦 NODASS 影像或圖磚端點。
- 葉綠素事件優先查看 `GOCI_CHL`、`OLNT_S3_CHL`、`Sentinel2_CHL`。
- 懸浮固體與重金屬事件優先查看 `GOCI_TSS`、`OLNT_S3_TSM`、`Sentinel2_TSM`。
- 影像查詢時間窗固定為事件日前後 72 小時。
- 系統不自動補齊缺漏資料；缺資料會整理在文件或報告中。

### 6. 採樣建議

- 先建議異常測站複測，確認汙染是否仍存在。
- 再沿預測擴散方向與高風險關注點布設採樣斷面。
- 採樣建議會列出點位名稱、理由、緯度與經度。
- 採樣點可在互動式地圖上查看。

### 7. 論文方法復現

已放入系統中的可復現功能包含：

- 多測站時空異常偵測：對應汙染事件偵測與事件窗。
- 水動力汙染傳輸概念：對應 72 小時順流擴散軌跡。
- Bayesian/MCMC 汙染推估概念：目前以透明分數與風險節點展示，後續可升級為後驗機率。
- 主動採樣策略：對應汙染測站複測與擴散方向斷面採樣。
- 衛星 CHL/TSM/SST 佐證：對應 NODASS 事件窗影像 API 入口。

## 專案結構

```text
NODASS project/
  configs/                     設定檔
  dashboard/                   React 互動前端原始頁與資料
  data/
    external/                  外部資料暫存，不上傳 GitHub
    processed/                 系統處理後資料，不上傳 GitHub
  dist/                        線上展示用靜態網站
  docs/                        中文說明文件與更新匯報
  models/                      模型設定與未來模型輸出
  reports/                     系統執行摘要
  src/                         Python 資料管線與 CLI
  tests/                       測試資料夾
```

## 主要檔案

| 檔案 | 說明 |
| --- | --- |
| `dashboard/index.html` | React 互動前端原始檔 |
| `dashboard/system_data.json` | 前端開發用系統資料 |
| `dist/index.html` | 線上展示用前端檔 |
| `dist/data/system_data.json` | 線上展示用資料 |
| `data/processed/anomaly_events.csv` | 汙染異常事件 |
| `data/processed/event_time_windows.csv` | 72 小時事件窗 |
| `data/processed/source_candidates.csv` | 沿岸風險參考點 |
| `data/processed/source_ranking_results.csv` | 風險與一致性判斷 |
| `reports/system_run_summary.json` | 系統執行摘要 |
| `docs/` | 更新報告與資料需求文件 |

## 安裝需求

### 必要環境

- Python 3.11 以上
- Git
- 可開啟網頁的瀏覽器

### 前端套件

目前前端使用 CDN 版套件，不需要 `npm install`。

- React 18
- ReactDOM 18
- Babel Standalone
- Leaflet 1.9.4
- OpenStreetMap tile service

### Python 套件

目前核心資料流程以 Python 標準函式庫為主：

- `csv`
- `json`
- `datetime`
- `pathlib`
- `statistics`
- `urllib`
- `zipfile`

若後續要升級為正式分析模型，建議新增：

```bash
pip install pandas numpy scikit-learn pgmpy networkx geopandas shapely pyproj
```

若要升級粒子漂流或格網海流模擬，建議評估：

```bash
pip install opendrift parcels netCDF4 xarray
```

## API 授權碼

授權碼請只放在本機環境變數或 `.env`，不要寫進前端或 GitHub。

| 環境變數 | 用途 | 申請網址 |
| --- | --- | --- |
| `CWA_API_KEY` | 中央氣象署雨量、海氣象與海象資料 | https://opendata.cwa.gov.tw/user/authkey |
| `MOENV_API_KEY` | 環境部水汙染源許可及申報資料 | https://data.moenv.gov.tw/api/v2/EMS_S_03 |
| `WRA_API_KEY` | 水利署河川、流域、水位與流量 API | https://fhy.wra.gov.tw/Api |
| `GOOGLE_EARTH_ENGINE_KEY` | 未來接入 Earth Engine 衛星與格網影像 | https://earthengine.googleapis.com |

目前已驗證中央氣象署與環境部 API 可讀取；水利署 FHY 端點需要水利署自己的 API key，不能使用中央氣象署授權碼。

## 常用指令

### 更新外部資料

```bash
python -m src.cli fetch-external
```

### 探測 NODASS API

```bash
python -m src.cli probe-nodass
```

### 盤點原始資料

```bash
python -m src.cli audit --data-root "C:/高雄科技大學_找點樂子"
```

### 重跑完整系統

```bash
python -m src.cli run-system --data-root "C:/高雄科技大學_找點樂子"
```

### 本機預覽

```bash
cd dist
python -m http.server 8787
```

開啟：

```text
http://127.0.0.1:8787/index.html
```

## NODASS API 探測結果

目前已探測 26 個 NODASS 端點，其中多數可讀取。

- 可讀取：`OLNT_S3_CHL`、`OLNT_S3_TSM`、`Sentinel2_CHL`、`Sentinel2_TSM`、`GOCI_CHL`、`GOCI_TSS`、`GOCI`、`OLNT_S3`、`SLNT_S3_SST`、`CWA`、`IHMT`、`WRA`、`NAMR`
- 需確認權限：`EPA/MWQ`
- 需確認代碼或資料狀態：`GOCI_SSH`

## 目前限制

- 初版擴散預測使用事件窗平均流速與主導方向，尚未接入完整格網海流模型。
- 目前只預測方向性與可能影響區域，不輸出正式濃度場。
- 影像資料目前提供事件窗 API 入口，尚未把影像直接疊到地圖。
- 系統不自動補齊缺資料；需要補充的資料會以報告列出。
- `EPA/MWQ` 端點仍需確認權限。

