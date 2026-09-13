# 2026-09-13 進階功能升級匯報

## 本次實作目標

本次依需求開始製作前一輪建議功能，重點放在三個可立即落地的方向：

1. NODASS 衛星圖磚疊加。
2. 72 小時反向漂流雛形。
3. 貝氏污染來源機率面板。

## 已完成功能

| 功能 | 完成內容 | 對應論文/專案概念 |
| --- | --- | --- |
| NODASS 圖磚疊加 | 來源追蹤地圖會依事件日前後 72 小時自動嘗試載入 `GOCI` 與 `OLNT_S3` 圖磚。 | 衛星水色影像輔助污染來源判讀 |
| 72 小時反向漂流 | 新增「漂流反推」頁，使用事件窗平均流速與主導流向反推污染到達前 72 小時可能路徑。 | OpenDrift/OceanParcels 類粒子漂流概念雛形 |
| 貝氏來源機率 | 新增「貝氏機率」頁，將來源排序分數轉為後驗機率樣式。 | Bayesian/MCMC 污染源反推概念雛形 |
| 來源追蹤整合 | 來源追蹤地圖新增 NODASS 圖磚選單與 72 小時反向漂流圖層。 | 多證據來源追蹤決策介面 |
| API 狀態匯報 | 將 `GOCI_SSH` 與 Google Earth Engine 列入影像佐證頁。 | 後續海面高度與 Sentinel 自動取像需求 |

## NODASS 端點測試結果

| 端點 | 狀態 | 備註 |
| --- | --- | --- |
| `images/GOCI_SSH?date1=2021-03-01&date2=2021-03-02` | `HTTP 404` | 需確認代碼是否更名或資料是否下架。 |
| `images/GOCI_SSH?date1=2020-01-01&date2=2020-03-02` | `HTTP 404` | 需確認是否有其他 SSH/海面高度端點。 |
| `tiles/GOCI?date1=2021-03-01&date2=2021-03-02` | `HTTP 200` | 可取得 `AccessURL`。 |
| `tiles/GOCI?date1=2020-01-01&date2=2020-03-02` | `HTTP 200` | 可取得 `AccessURL`。 |
| `tiles/OLNT_S3?date1=2021-03-01&date2=2021-03-02` | `HTTP 200` | 可取得 `AccessURL`。 |
| `tiles/OLNT_S3?date1=2020-01-01&date2=2020-03-02` | `HTTP 200` | 可取得 `AccessURL`。 |
| `https://earthengine.googleapis.com` | 根網址 `HTTP 404` | 正式使用需透過 Google Cloud 啟用 Earth Engine API 並帶授權呼叫。 |

## 圖磚格式確認

NODASS `tiles/GOCI` 與 `tiles/OLNT_S3` 回傳的 `AccessURL` 不是一般 `z/x/y.png` 格式。實測可用格式為：

```text
AccessURL/{z}/{y}/{x}.jpg
```

系統已依此格式接入 Leaflet 圖層。

## 目前限制

| 項目 | 限制 | 下一步 |
| --- | --- | --- |
| NODASS 圖磚 | 目前由瀏覽器端嘗試讀取公開端點，若 CORS 或端點當期無影像，會只顯示 OpenStreetMap。 | 建議建立後端代理或定期快取圖磚 metadata。 |
| 反向漂流 | 目前使用單一平均流速與主導流向，尚非真正粒子模式。 | 接入 HYCOM、ROMS、Copernicus Marine 或台灣本地格網海流後，升級 OpenDrift/OceanParcels。 |
| 貝氏機率 | 目前是來源分數正規化與來源類型先驗，尚未訓練條件機率表。 | 取得歷史污染事件、排放量、稽查紀錄後建立正式 Bayesian Network/MCMC。 |
| GOCI_SSH | 端點目前為 404。 | 向 NODASS/NAMR 確認 SSH 代碼、資料狀態或替代海面高度/潮位資料。 |
| Earth Engine | 尚未申請/授權。 | 建立 Google Cloud 專案，啟用 Earth Engine API，設定服務帳號或 OAuth。 |

## 後續建議

1. 將 NODASS 圖磚 metadata 寫入後端快取，避免每次前端即時查詢。
2. 取得格網海流資料後，改用 OpenDrift 或 OceanParcels 進行真正粒子追蹤。
3. 建立歷史污染事件資料表，校正貝氏來源機率。
4. 申請 Google Earth Engine，用於 Sentinel-2/3 自動取像、雲遮遮罩與水色指標計算。
5. 確認 `GOCI_SSH` 是否改名，或改用中央氣象署/海洋資料庫潮位與海面高度資料。

