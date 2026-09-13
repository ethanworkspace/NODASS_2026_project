# 資料服務與可復現功能匯報（2026-09-13）

## 本次頁面調整

- 「汙染影響」頁已移除下列技術型區塊，避免一般使用者在操作系統時被資料申請與模型細節干擾：
  - 擴散模型輸入
  - 建議接入的海洋資料服務
  - 論文可復現功能
  - API 優先清單
- 上述內容改集中整理於本文件，作為專案維護、資料串接與後續研究復現的內部匯報。

## 已提供但不應公開寫入的授權資料

- 中央氣象署開放資料 API 授權碼已由使用者提供。
- 授權碼不得寫入 `dashboard/index.html`、`dist/index.html`、`README.md` 或任何會上傳 GitHub / 公開網站的檔案。
- 專案應只使用環境變數名稱保存設定需求：
  - `CWA_API_KEY`
  - `COPERNICUSMARINE_SERVICE_USERNAME`
  - `COPERNICUSMARINE_SERVICE_PASSWORD`

## Copernicus Marine 狀態

使用者已登入 Copernicus Marine，代表可進入下一階段資料接入規劃。正式串接仍建議在後端處理，不應把帳密或 token 放入前端。

建議優先資料：

| 資料服務 | 用途 | 連結 |
| --- | --- | --- |
| Copernicus Marine 全球海洋物理預報 | 取得海流 u/v、流速與流向，作為粒子漂流主驅動 | https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description |
| Copernicus Marine 全球波浪預報 | 取得波浪場、Stokes drift 或表層漂移補正 | https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description |
| Copernicus Marine Sea Ice L4 NRT | 台灣近岸污染監測不是優先資料，但可保留為全球產品格式參考 | https://data.marine.copernicus.eu/product/SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001/services |

## 中央氣象署資料接入規劃

目前系統前端已有風向與預設風速顯示。下一階段應由後端使用 `CWA_API_KEY` 讀取風場、潮位或海象資料，整理後輸出給前端。

建議用途：

| 資料 | 用途 |
| --- | --- |
| 風向 | 汙染表層漂移方向補正 |
| 風速 | 估算 wind leeway，取代目前展示預設值 |
| 潮位 | 判斷漲退潮與沿岸擴散風險 |
| 海象觀測 | 驗證波浪、海況與漂流不確定性 |

## 擴散模型輸入

前端目前使用下列合成概念：

```text
drift_vector = ocean_current_vector + wind_leeway_vector + stokes_drift_vector
```

欄位需求：

| 欄位 | 說明 |
| --- | --- |
| ocean_current_u / ocean_current_v | 海流東西與南北分量 |
| ocean_current_speed | 海流速度 |
| ocean_current_direction | 海流方向 |
| wind_speed | 風速 |
| wind_direction | 風向 |
| stokes_drift_u / stokes_drift_v | 波浪造成的表層 Stokes drift |
| timestamp | 時間，需落在事件日前後 72 小時窗內 |
| lat / lon | 粒子所在位置或格網中心 |

## 論文可復現功能

| 功能 | 系統對應 | 後續補強 |
| --- | --- | --- |
| 多測站時空貝氏異常偵測 | 已具備事件窗、鄰近站點與異常分數 | 加入正式 Bayesian Network 節點與條件機率表 |
| 水動力 + Bayesian/MCMC 來源反推 | 已具備候選來源、擴散軌跡與可達性判斷 | 後端加入 MCMC 取樣與污染源 posterior 排序 |
| 主動式污染源追蹤 Agent | 已能列出候選來源與資料缺口 | 加入巡測路徑規劃與不確定性更新 |
| 衛星 CHL / TSM 影像比對 | 已列入 NODASS 影像 API 與事件窗 | 加入影像下載、雲遮/缺值標記與空間重疊分析 |

## API 優先清單

| API / 資料 | 優先度 | 用途 |
| --- | --- | --- |
| CWA_API_KEY | 高 | 風速、風向、潮位、海象觀測 |
| Copernicus Marine Physics | 高 | 海流 u/v 與格網流速 |
| Copernicus Marine Waves | 高 | 波浪、Stokes drift、表層漂移補正 |
| NODASS GOCI / Sentinel CHL | 高 | 葉綠素 a 異常與藻華判讀 |
| NODASS GOCI / Sentinel TSM / TSS | 高 | 懸浮固體、泥沙羽流與污染水團判讀 |
| NODASS OBS Stations | 高 | 觀測站 metadata 與近岸現地資料 |
| WRA_API_KEY | 中 | 河川水位、流量與河口輸入條件 |
| MOENV_API_KEY | 中 | 污染源許可、放流水與排放背景 |

## 後續工程建議

1. 將 CWA 與 Copernicus Marine 的帳密/API key 放入後端環境變數。
2. 新增後端排程：每日下載台灣周邊海流、風場與波浪資料。
3. 將格網資料轉成事件窗查詢格式，避免前端直接處理大型 NetCDF/Zarr。
4. 前端維持只讀取整理後的 JSON，並顯示資料來源、更新時間與缺值狀態。
