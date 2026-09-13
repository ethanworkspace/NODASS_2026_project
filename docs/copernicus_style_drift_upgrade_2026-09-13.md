# Copernicus 類粒子漂流與汙染影響頁更新報告

更新日期：2026-09-13

## 本次更新重點

本次依 Copernicus Marine 這類海洋格網資料服務的概念，將擴散預測軌跡從單純方向線，升級為可接海洋資料場的粒子漂流模型架構。

## 已完成內容

### 1. 擴散軌跡改為多因子推估

新版漂流方向與距離會結合：

- 海洋流向
- 海洋流速
- 風向
- 風速
- 波浪 Stokes drift 預留項

目前資料中已有海流方向、海流速度與風向。風速欄位尚未正式接入，因此前端會清楚標示為「待接入，展示預設」，不會當成實測資料。

### 2. 粒子漂流顯示

- 地圖持續顯示漂流粒子動畫。
- 粒子沿合成漂流向量移動。
- 粒子加入橫向展寬，模擬汙染水團擴散。
- 圖層可單獨開關。

### 3. 海流與風向顯示

- 地圖新增海流向量。
- 地圖新增風向向量。
- 擴散預測頁顯示海流方向、海流速度、風向、風速與風速來源。

### 4. 刪除系統說明頁

已將原本的「系統說明」頁移除，改為「汙染影響」頁。

汙染影響頁包含：

- 汙染擴散可能造成的影響
- 目前風險受體
- 擴散模型輸入
- 建議接入的海洋資料服務
- 論文可復現功能
- API 優先清單

## 建議接入資料來源

| 資料來源 | 用途 | 網址 |
| --- | --- | --- |
| Copernicus Marine 全球海洋物理預報 | hourly sea water velocity、surface currents、粒子所在位置的 u/v 海流 | https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description |
| Copernicus Marine 全球波浪預報 | wave direction、wave period、Stokes drift、表層漂移 | https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description |
| 中央氣象署開放資料 | 台灣周邊風向、風速、潮位與海象觀測 | https://opendata.cwa.gov.tw/ |
| NODASS | CHL、TSM、SST、觀測站與影像佐證 | https://nodass.namr.gov.tw/data |

## 模型公式概念

目前前端以向量方式合成漂流：

```text
drift_vector = ocean_current_vector + wind_leeway_vector + stokes_drift_vector
```

其中：

- `ocean_current_vector` 由海流方向與海流速度換算。
- `wind_leeway_vector` 由風向與風速換算，目前使用風速 3% 作為表層漂移係數。
- `stokes_drift_vector` 為波浪漂移預留項，未來可由 Copernicus wave 產品取得。

## 目前限制

- 目前仍是前端初版粒子模型，尚未真正下載 Copernicus NetCDF / Zarr 格網資料。
- 風速欄位尚未接入，暫以展示預設值呈現並明確標示。
- 需申請 Copernicus Marine 帳號或服務憑證後，才能做正式資料下載。
- 正式版本應在後端以時間與座標查詢格網 u/v 流速，再逐步推進粒子。

## 下一階段建議

1. 申請 Copernicus Marine 帳號。
2. 在後端加入 `copernicusmarine` Python 套件。
3. 下載台灣周邊海域 hourly currents 與 wave/Stokes drift。
4. 將粒子從前端動畫升級為後端產生 GeoJSON 軌跡。
5. 在地圖加入粒子濃度熱區與抵達時間。
