# NODASS 海岸生態壓力與污染傳輸來源追蹤 AI

本專案用於分析海岸水質異常，並結合水質、海氣象、水文、污染源、衛星影像與離岸風電海域水質資料，推估可能的污染傳輸來源區。系統第一版採用透明可檢核的規則式模型，並預留貝氏網路、因果推論與粒子漂流模擬的升級結構。

## 目前功能

### 1. 水質異常偵測

- 偵測葉綠素 a、營養鹽、懸浮固體與重金屬異常。
- 使用中位數與 MAD/IQR 穩健尺度建立初版異常分數。
- 產出異常事件表，包含測站、時間、污染物、實測值、基準值與異常分數。

### 2. 72 小時時空一致性

- 每個異常事件自動建立事件日前後 72 小時時間窗。
- 僅使用事件窗內的海氣象資料。
- 來源候選必須符合至少一項條件才會進入排序：
  - 72 小時內依平均流速可達。
  - 位於上風方向。
  - 位於上游流向可達方向。

### 3. 污染來源排序

- 來源類型包含河川輸入、港區活動、工業來源、污水處理與環境部正式放流口。
- 排序分數整合距離、流向、風向、污染物吻合度與 72 小時可達性。
- 產出每個異常事件前 5 名候選來源與信心等級。

### 4. 外部資料串接

- 中央氣象署雨量 API：已可讀取並解析雨量站。
- 環境部 EMS_S_03：已可讀取水污染源許可及申報資料，並轉成正式放流口候選來源。
- NODASS noapi 端點：已建立探測工具，記錄端點狀態、資料筆數與回傳欄位。
- 離岸風電海域水質壓縮檔：已匯入摘要，作為 EPA/MWQ 端點無權限時的離線佐證。

### 5. React 互動式前端

前端位於 `dashboard/index.html` 與 `dist/index.html`，目前包含：

- 總覽
- 異常事件
- 來源追蹤
- 時空一致性
- 影像佐證
- 漂流反推
- 貝氏機率
- 採樣建議
- 模型評估
- NODASS 探測
- 離岸風電水質

系統中不再放置「資料補齊」頁；待申請資料會整理在文件中匯報。

### 6. 可連接互動地圖

- 來源追蹤頁已接入 Leaflet 地圖模組。
- 預設底圖使用 OpenStreetMap，無需 API key。
- 地圖會顯示異常測站、候選污染來源與來源至事件測站的傳輸連線。
- 可平移、縮放、開關圖層，並點選地圖點位查看事件、來源、距離、信心與 72 小時可達性。
- 地圖會嘗試依事件窗載入 NODASS `GOCI` 與 `OLNT_S3` 圖磚，使用格式為 `AccessURL/{z}/{y}/{x}.jpg`。
- 若外部 CDN 或底圖暫時無法載入，系統會回到內建台灣周邊示意地圖。

### 7. 影像佐證

- 依事件污染群組自動推薦 NODASS 影像端點。
- 葉綠素事件優先推薦 `GOCI_CHL`、`OLNT_S3_CHL`、`Sentinel2_CHL`。
- 懸浮固體與重金屬事件優先推薦 `GOCI_TSS`、`OLNT_S3_TSM`、`Sentinel2_TSM`。
- 影像查詢時間窗固定為事件日前後 72 小時，符合時空一致性原則。
- `GOCI` 與 `OLNT_S3` 圖磚已接入來源追蹤地圖的疊圖選單。
- `GOCI_SSH` 已列入待確認端點，目前測試為 `HTTP 404`。
- Google Earth Engine 已列為後續 Sentinel-2/3 自動取像與水色處理平台，正式使用需要 Google Cloud 專案與授權。

### 8. 72 小時反向漂流

- 使用事件窗平均流速與主導流向，建立反向 72 小時漂流軌跡雛形。
- 在來源追蹤地圖與「漂流反推」頁顯示反推路徑。
- 目前是簡化向量模型；正式 OpenDrift/OceanParcels 版本需接入格網海流資料。

### 9. 貝氏來源機率

- 將目前來源分數、污染物吻合、上游流向、上風方向與來源類型轉成後驗機率樣式。
- 顯示最高後驗來源、候選來源相對機率與先驗權重。
- 目前是透明可檢核的貝氏雛形；正式 Bayesian Network/MCMC 需歷史事件與排放資料校正。

### 10. 採樣建議

- 依最高順位候選來源與異常測站位置，自動產生下一採樣點。
- 採樣點包含異常測站複測點，以及來源到事件測站之間的斷面點。
- 採樣建議頁會列出每個點位的經緯度、目的與判讀理由。
- 採樣點已可在互動地圖上顯示。

### 11. 論文方法復現

已把文獻中的方法轉成系統可用功能：

- 多測站時空貝氏異常偵測：已復現為 72 小時事件窗與多測站一致性架構。
- 水動力 + Bayesian/MCMC 污染源反推：已復現為流速、方向、距離與污染物吻合度來源排序。
- 主動式污染源追蹤 Agent：已復現為異常後自動列出來源與下一步資料需求。
- 衛星葉綠素/懸浮物影像比對：已復現為 NODASS CHL/TSM/SST API 探測與事件窗影像準備。
- 主動採樣策略：已復現為異常測站複測與候選來源傳輸斷面採樣點推薦。
- 粒子漂流模型：已復現為 72 小時反向漂流雛形，等待格網海流資料後升級為 OpenDrift/OceanParcels。
- Bayesian/MCMC 來源反推：已復現為來源後驗機率面板，等待歷史事件與排放量資料後校正。

## 專案結構

```text
NODASS project/
  configs/                     設定檔
  dashboard/                   React 互動前端原始頁與資料
  data/
    external/                  外部資料暫存，不上傳 GitHub
    processed/                 系統處理後資料，不上傳 GitHub
  dist/                        線上展示用靜態網站
  docs/                        中文說明文件與匯報
  models/                      模型設定與未來模型輸出
  reports/                     系統執行摘要
  src/                         Python 資料管線與 CLI
  tests/                       測試資料夾
```

## 主要輸出

| 檔案 | 說明 |
| --- | --- |
| `dashboard/system_data.json` | React 前端使用的完整系統資料 |
| `dist/data/system_data.json` | 線上展示使用的資料檔 |
| `data/processed/anomaly_events.csv` | 異常事件 |
| `data/processed/event_time_windows.csv` | 72 小時事件窗 |
| `data/processed/source_candidates.csv` | 候選污染來源 |
| `data/processed/source_ranking_results.csv` | 來源排序結果 |
| `reports/system_run_summary.json` | 每次執行摘要 |
| `docs/update_report_2026-09-12.md` | 本次更新匯報 |
| `docs/feature_upgrade_report_2026-09-12.md` | 推薦功能升級匯報 |
| `docs/advanced_feature_report_2026-09-13.md` | NODASS 圖磚、漂流反推與貝氏機率升級匯報 |

## 安裝需求

本專案目前以 Python 標準函式庫與靜態 React CDN 為主，不需要大型安裝流程。

### 必要套件

- Python 3.11 以上
- Git
- 可開啟網頁的瀏覽器

### 前端使用

目前前端使用 CDN 版 React：

- React 18
- ReactDOM 18
- Babel Standalone
- Leaflet 1.9.4
- OpenStreetMap tile service

因此不需要 `npm install`。若未來要改成正式 Vite/Next.js 專案，可再新增 `package.json`、`vite`、`typescript` 與測試工具。

### Python 套件

目前核心流程使用標準函式庫：

- `csv`
- `json`
- `datetime`
- `pathlib`
- `statistics`
- `urllib`
- `zipfile`/系統解壓工具

目前不必安裝 pandas、numpy 或 scikit-learn。若要升級模型，建議新增：

```bash
pip install pandas numpy scikit-learn pgmpy networkx geopandas shapely pyproj
```

若要做粒子漂流模擬，建議評估：

```bash
pip install opendrift parcels netCDF4 xarray
```

## API 授權碼設定

授權碼請只放在本機環境變數或 `.env`，不要寫進前端或 GitHub。

| 環境變數 | 用途 | 申請網址 |
| --- | --- | --- |
| `CWA_API_KEY` | 中央氣象署雨量、海氣象與海象資料 | https://opendata.cwa.gov.tw/user/authkey |
| `MOENV_API_KEY` | 環境部水污染源許可及申報資料 EMS_S_03 | https://data.moenv.gov.tw/api/v2/EMS_S_03 |
| `WRA_API_KEY` | 水利署 FHY 河川、流域、水位與流量 API | https://fhy.wra.gov.tw/Api |

目前已驗證中央氣象署與環境部 API 可讀取；水利署 FHY 端點需要水利署自己的 API key，不能使用中央氣象署授權碼。

## 地圖模組與可改接 API

目前系統使用 Leaflet + OpenStreetMap，這是免金鑰的公開底圖組合，適合初版展示與研究原型。若後續要做正式營運或需要更穩定的服務等級，可替換 `dashboard/index.html` 內的 `mapProvider` 設定。

| 地圖來源 | 是否需要 API key | 用途 |
| --- | --- | --- |
| OpenStreetMap | 否 | 初版互動底圖、縮放、平移與點位呈現 |
| Mapbox | 是 | 商用底圖、衛星底圖、客製化樣式 |
| Google Maps Platform | 是 | 商用地圖、地理編碼與高流量服務 |
| 國土測繪中心圖資服務 | 依服務條款與流量而定 | 台灣官方底圖、地籍/通用電子地圖 |
| NODASS 影像/圖磚 | 依端點權限而定 | 衛星 CHL、TSM、SST 事件窗影像疊圖 |
| Google Earth Engine | 是 | Sentinel-2/3 自動取像、雲遮遮罩與水色指標處理 |

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

目前已探測 26 個 NODASS 端點，其中 23 個可讀取。

- 可讀取：`OLNT_S3_CHL`、`OLNT_S3_TSM`、`Sentinel2_CHL`、`Sentinel2_TSM`、`GOCI_CHL`、`GOCI_TSS`、`GOCI`、`OLNT_S3`、`SLNT_S3_SST`、`CWA`、`IHMT`、`WRA`、`NAMR`
- 需確認權限：`EPA/MWQ`，目前回傳 `HTTP 403`
- 需確認代碼或資料狀態：`GOCI_SSH`，目前回傳 `HTTP 404`
- 圖磚格式已確認：`GOCI` 與 `OLNT_S3` 回傳的 `AccessURL` 可使用 `AccessURL/{z}/{y}/{x}.jpg` 疊加到 Leaflet。

## 目前限制

- 初版來源排序仍是透明規則分數，尚未改成正式後驗機率。
- 尚未接入格網海流模型，粒子漂流模擬仍是下一階段功能。
- 離岸風電水質資料已做摘要，尚未完全轉成逐站時間序列分析。
- `EPA/MWQ` 端點需要確認權限，暫以使用者提供的壓縮檔補足背景資料。

## 線上展示

展示網站：

https://nodass-coastal-source-tracing-ai.workspace-787619.chatgpt.site

GitHub：

https://github.com/ethanworkspace/NODASS_2026_project
