# 2026-09-12 地圖模組升級匯報

## 本次升級目標

本次依需求將 NODASS 海岸污染來源追蹤 AI 的地圖從靜態示意圖升級為可連接底圖服務的互動式地圖，讓污染來源推估結果可以在真實地圖上檢視。

## 已完成內容

| 項目 | 完成內容 |
| --- | --- |
| 地圖模組 | 已接入 Leaflet 1.9.4。 |
| 預設底圖 | 使用 OpenStreetMap 公開圖磚，不需要 API key。 |
| 事件顯示 | 在地圖上標示異常測站，點選可查看事件編號、測站、污染物與異常分數。 |
| 來源顯示 | 在地圖上標示候選污染來源，點選可查看來源類型、距離、信心與 72 小時可達性。 |
| 傳輸連線 | 以線段連接候選來源與異常測站，前順位來源以較醒目的線寬顯示。 |
| 圖層控制 | 可開關異常測站、候選來源與傳輸連線圖層。 |
| 地圖備援 | 若外部地圖 CDN 或底圖無法載入，系統會自動回到內建台灣周邊示意地圖。 |

## 目前地圖資料來源

| 資料 | 系統欄位 | 用途 |
| --- | --- | --- |
| 異常事件 | `event.lat`、`event.lon` | 異常測站定位 |
| 來源候選 | `source.lat`、`source.lon` | 候選污染來源定位 |
| 來源排序 | `distance_km`、`confidence_level`、`reachable_within_72h` | 地圖彈窗與來源可信度判讀 |
| 事件窗 | `dominant_current_direction`、`dominant_wind_direction`、`mean_current_speed` | 來源追蹤判斷摘要 |

## 可申請或改接的地圖/API

| API 或模組 | 是否需要申請 | 建議用途 | 網址 |
| --- | --- | --- | --- |
| OpenStreetMap | 否 | 初版展示與研究原型底圖 | https://www.openstreetmap.org |
| Leaflet | 否 | 前端互動地圖模組 | https://leafletjs.com |
| Mapbox | 是 | 商用底圖、衛星底圖、客製化樣式與高流量服務 | https://www.mapbox.com |
| Google Maps Platform | 是 | 商用地圖、地理編碼、路徑與高穩定度服務 | https://mapsplatform.google.com |
| 國土測繪中心圖資服務 | 依服務條款與使用量而定 | 台灣官方底圖、通用電子地圖、地形圖 | https://maps.nlsc.gov.tw |
| NODASS 圖磚與影像端點 | 依端點權限而定 | CHL、TSM、TSS、SST 事件窗衛星影像疊圖 | https://nodass.namr.gov.tw/api-service |

## 下一階段可延伸功能

1. 將 NODASS `tiles/GOCI`、`tiles/OLNT_S3` 疊加到 Leaflet 作為衛星影像圖層。
2. 依異常事件日期自動取得前後 72 小時 CHL/TSM/SST 影像，並在地圖上切換。
3. 加入河川流量、水位與入海口圖層，強化上游來源判斷。
4. 接入格網海流資料後，將傳輸線升級為粒子漂流軌跡。
5. 若正式部署需要服務等級保證，可改用 Mapbox 或 Google Maps API key。

