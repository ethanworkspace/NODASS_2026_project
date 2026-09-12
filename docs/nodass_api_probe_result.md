# NODASS API 探測結果

探測來源：使用者提供的 NODASS `noapi/namr/v1` 端點清單。

## 本次結論

- 共探測 26 個端點。
- 23 個端點可讀取。
- `EPA/MWQ` 測站端點目前回傳 `HTTP 403`，需確認是否要登入或申請權限。
- `GOCI_SSH` 兩個日期區間目前回傳 `HTTP 404`，需向 NODASS 確認正確代碼或資料是否已下架。
- 衛星影像類端點可回傳 `AccessImageURL`、`AccessLegendURL`、`DateTime` 與空間邊界欄位，可作為異常事件 ±72 小時影像佐證。

## 已可優先納入系統的端點

| 類型 | API 代碼 | 用途 |
| --- | --- | --- |
| 葉綠素影像 | `OLNT_S3_CHL`、`Sentinel2_CHL`、`GOCI_CHL` | 葉綠素 a 異常、優養化、藻華與空間擴散判讀 |
| 懸浮物影像 | `OLNT_S3_TSM`、`Sentinel2_TSM`、`GOCI_TSS` | 懸浮固體異常、河口泥沙羽流與港區擾動判讀 |
| 自然色圖磚 | `GOCI`、`OLNT_S3` | 事件當日影像背景與雲遮判讀 |
| 海溫影像 | `SLNT_S3_SST` | 海溫、水團邊界與生態壓力判讀 |
| 觀測站 metadata | `CWA`、`IHMT`、`WRA`、`NAMR` | 建立風、流、潮、浪測站資料表 |
| 觀測值資料 | `Vector_NAMR_FB_35A0003/data` | 測試即時/歷史觀測資料格式 |

## 需要向 NODASS 申請或確認的 API 名稱

| API 名稱 | 代碼 | 原因 |
| --- | --- | --- |
| Ministry of the Environment - Offshore Wind Farm Seawater Quality Station Information | `EPA/MWQ` | 目前回傳 403，需確認權限 |
| GOCI sea surface height image | `GOCI_SSH` | 目前回傳 404，需確認正確代碼或替代資料 |
| Monitoring data from observation stations | `OBS_DATA` | 要大量查測站歷史值時，建議確認使用限制與授權 |
| Sentinel/GOCI image products | `OLNT_S3_CHL`、`OLNT_S3_TSM`、`Sentinel2_CHL`、`Sentinel2_TSM`、`GOCI_CHL`、`GOCI_TSS` | 若要批次抓取事件窗影像，建議確認流量限制與資料授權 |
