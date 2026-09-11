# NODASS 海岸生態壓力與污染來源追蹤 AI

本專案用於分析海岸水質異常，並結合海氣象、水文、生態與空間資料，推估可能的污染傳輸來源區。

## 專案目標

- 偵測葉綠素 a、營養鹽、懸浮固體與重金屬異常。
- 針對每個異常事件建立前後 72 小時事件窗。
- 依上風、上游流向、鄰近河口與可達時間篩選候選來源。
- 先用透明規則排序來源區，再逐步加入貝氏網路與因果推論。

## 第一版示範範圍

建議先以以下區域做 MVP：

- 高屏溪出海口
- 高雄港外海測站
- 二仁溪口

這些區域在現有資料中已有明確水質測站，且鄰近來源語意清楚，適合快速做出可展示的來源追蹤流程。

## 主要流程

1. 匯入原始水質、海氣象、生態與外部污染源資料。
2. 標準化測站資料、時間、單位與品管欄位。
3. 偵測水質異常事件。
4. 為每個事件擷取前後 72 小時資料窗。
5. 依風、流、潮與距離估算污染物可達性。
6. 排序候選污染來源區。
7. 產生事件報告與儀表板可用資料。

## 資料目錄

可將既有 NODASS 資料放入 `data/raw/`，或在 `configs/paths.yaml` 指定原始資料位置。

```text
data/
  raw/
  interim/
  processed/
  external/
```

## 執行方式

```bash
python -m src.cli fetch-external
python -m src.cli audit --data-root "C:/高雄科技大學_找點樂子"
python -m src.cli build-stations --data-root "C:/高雄科技大學_找點樂子"
python -m src.cli detect-anomalies --data-root "C:/高雄科技大學_找點樂子"
python -m src.cli run-system --data-root "C:/高雄科技大學_找點樂子"
```

## API 授權碼設定

授權碼請只放在本機環境變數或 `.env`，不要寫進前端或 GitHub。

| 環境變數 | 用途 | 申請網址 |
| --- | --- | --- |
| `CWA_API_KEY` | 中央氣象署雨量、海氣象與海象資料 | https://opendata.cwa.gov.tw/user/authkey |
| `MOENV_API_KEY` | 環境部水污染源許可及申報資料 EMS_S_03 | https://data.moenv.gov.tw/api/v2/EMS_S_03 |
| `WRA_API_KEY` | 水利署 FHY 河川、流域、水位與流量 API | https://fhy.wra.gov.tw/Api |

目前已驗證中央氣象署與環境部 API 可讀取；水利署 FHY 端點需要水利署自己的 API key，不能使用中央氣象署授權碼。

## 目前狀態

目前已完成初版 React 互動前端、資料契約、設定檔、資料管線、異常偵測、72 小時時空一致性篩選與來源排序結果輸出。
