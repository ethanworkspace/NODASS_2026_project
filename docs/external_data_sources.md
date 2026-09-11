# 外部資料補齊清單

本系統第一版已用現有海保署測站名稱與座標建立「初版候選來源」，並把下列官方資料來源登錄到 `data/external/external_data_catalog.csv`。後續若取得 API 金鑰、批次下載檔或正式清冊，可直接匯入並覆蓋初版候選來源。

## 已登錄資料來源

| 資料 | 提供機關 | 補齊用途 | 狀態 |
| --- | --- | --- | --- |
| 雨量觀測站-雨量資料 | 交通部中央氣象署 | 補足異常事件前後 72 小時降雨條件 | 已串接，需設定 `CWA_API_KEY` |
| 水污染源許可及申報資料 EMS_S_03 | 環境部 | 校正污水廠、工業放流口、排放污染物與排放量 | 已串接，需設定 `MOENV_API_KEY` |
| 即時水位資料與流域基本資料 | 經濟部水利署 | 補足河川水位、流量與逕流支持度 | 待申請水利署 `WRA_API_KEY` |
| 中央氣象署海象資料 | 交通部中央氣象署 | 補足潮位、海流、浮標與海象觀測 | 待會員登入/下載權限 |
| NODASS 國家海洋資料庫 | 國家海洋研究院 | 補足 HYCOM、ROMS、POM、風場、波浪、葉綠素與 AIS | 待登入或資料申請 |

## 需自行申請或登入的入口

| 來源 | 網址 | 備註 |
| --- | --- | --- |
| 中央氣象署開放資料授權碼 | https://opendata.cwa.gov.tw/user/authkey | 已可接入雨量 API |
| 中央氣象署 OpenAPI 文件 | https://opendata.cwa.gov.tw/dist/opendata-swagger.html | 查詢資料集代碼與參數 |
| 中央氣象署海象資料介面 | https://ocean.cwa.gov.tw/V2/data_interface/datasets | 需會員登入後下載更多資料 |
| 水利署 FHY API | https://fhy.wra.gov.tw/Api | FHY 端點需水利署自己的 API key |
| 水利署 OpenAPI 文件 | https://opendata.wra.gov.tw/api/v2/openapi.get | 水利署開放資料 OAS |
| 環境部 EMS_S_03 API | https://data.moenv.gov.tw/api/v2/EMS_S_03 | 已可用 `MOENV_API_KEY` 接入 |
| 環境統計查詢網 | https://statis.moenv.gov.tw/epanet/index.html | 查詢長期環境統計 |
| OCA 海洋保育資料 | https://www.oca.gov.tw/ch/home.jsp?id=318&parentpath=0,294,315 | 海域水質與保育相關資料 |
| 河川基本資料 | https://data.gov.tw/dataset/167895 | 可直接下載或串接 |
| NODASS 資料平台 | https://nodass.namr.gov.tw/data | 需確認下載/API 權限 |
| 國家海洋研究院研究成果 | https://www.namr.gov.tw/ch/home.jsp?id=50&parentpath=0,7&mcustomize=research_list.jsp | 可補模型、觀測與研究資料來源 |

## 第一版補齊策略

- 河口來源：從現有海保署測站名稱中辨識「溪口」「河口」並沿用其座標。
- 港區來源：從現有海保署測站名稱中辨識「港」「漁港」並沿用其座標。
- 工業來源：從現有海保署測站名稱中辨識「工業」「六輕」「火力」「發電」並沿用其座標。
- 污水來源：從現有海保署測站名稱中辨識「污水」並沿用其座標。

## 使用限制

- 初版候選來源是可運算的來源近似點，不等同於正式放流口清冊。
- 正式上線前，應以環境部水污染源資料、污水處理廠清冊與事業廢水許可資料校正來源座標。
- 因果推論需要歷史事件、排放量、降雨與河川流量共同支撐；目前初版僅做時空一致性與規則式來源排序。
