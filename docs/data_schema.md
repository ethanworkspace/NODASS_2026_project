# 資料架構

## stations

| 欄位 | 說明 |
| --- | --- |
| station_id | 穩定的測站編號 |
| station_name | 測站名稱 |
| source_agency | 資料來源，例如海保署、CWA、IHMT、NAMR、WRA 或外部資料 |
| station_type | 測站類型，例如水質、海氣象、生態、河口、污染源 |
| lon | 經度 |
| lat | 緯度 |
| region | 行政區或海岸區域 |
| coast_type | 海岸或生態系類型 |
| active_start | 最早觀測時間 |
| active_end | 最晚觀測時間 |

## water_quality_observations

| 欄位 | 說明 |
| --- | --- |
| observation_id | 唯一觀測資料編號 |
| station_id | 測站編號 |
| observed_at | UTC+8 觀測時間 |
| air_temperature | 氣溫，單位 C |
| salinity | 鹽度，單位 PSU |
| water_temperature | 水溫，單位 C |
| ph | 酸鹼值 |
| suspended_solid | 懸浮固體，單位 mg/L |
| dissolved_oxygen | 溶氧，單位 mg/L |
| dissolved_oxygen_saturation | 溶氧飽和度，單位百分比 |
| chlorophyll_a | 葉綠素 a，單位 ug/L |
| ammonia_nitrogen | 氨氮，單位 mg/L |
| nitrate_nitrogen | 硝酸鹽氮，單位 mg/L |
| orthophosphate | 正磷酸鹽，單位 mg/L |
| nitrite_nitrogen | 亞硝酸鹽氮，單位 mg/L |
| silicate | 矽酸鹽，單位 mg/L |
| cadmium | 鎘，單位 mg/L |
| chromium | 鉻，單位 mg/L |
| copper | 銅，單位 mg/L |
| zinc | 鋅，單位 mg/L |
| lead | 鉛，單位 mg/L |
| mercury | 汞，單位 mg/L |
| quality_flag | 資料品質旗標 |

## metocean_observations

| 欄位 | 說明 |
| --- | --- |
| observation_id | 唯一觀測資料編號 |
| station_id | 測站編號 |
| observed_at | UTC+8 觀測時間 |
| wind_gust_speed | 陣風風速，單位 m/s |
| wind_speed | 風速，單位 m/s |
| wind_direction | 風向，單位度 |
| air_pressure | 氣壓，單位 hPa |
| air_temperature | 氣溫，單位 C |
| sea_temperature | 海面溫度，單位 C |
| wave_height_significant | 示性波高，單位 m |
| wave_mean_period | 平均波浪週期，單位秒 |
| wave_main_direction | 波向，單位度 |
| wave_peak_period | 波浪尖峰週期，單位秒 |
| current_speed | 流速，單位 m/s |
| current_direction | 流向，單位度 |
| tide_height | 潮高，單位 m |
| lon | 經度 |
| lat | 緯度 |
| quality_flag | 資料品質旗標 |

## anomaly_events

| 欄位 | 說明 |
| --- | --- |
| event_id | 唯一異常事件編號 |
| station_id | 水質測站編號 |
| detected_at | 異常事件時間 |
| pollutant_group | 污染物群組，例如葉綠素、營養鹽、懸浮固體、重金屬 |
| pollutant_name | 污染物欄位名稱 |
| observed_value | 實測值 |
| baseline_value | 該站點基準值 |
| anomaly_score | 標準化異常分數 |
| anomaly_method | 異常偵測方法 |
| severity | 嚴重程度，例如低、中、高、重大 |
| status | 事件狀態，例如新事件、審核中、已確認、已排除 |

## source_ranking_results

| 欄位 | 說明 |
| --- | --- |
| result_id | 唯一排序結果編號 |
| event_id | 異常事件編號 |
| source_id | 候選來源編號 |
| distance_km | 來源到事件測站距離，單位公里 |
| bearing_to_event | 來源指向事件測站的方位角 |
| reachable_within_72h | 是否在 72 小時內可達 |
| upwind_score | 上風一致性分數 |
| upstream_current_score | 上游流向一致性分數 |
| pollutant_match_score | 污染物與來源類型吻合分數 |
| hydrology_score | 降雨與河川流量支持分數 |
| posterior_probability | 貝氏網路後驗機率 |
| confidence_level | 信心等級，例如低、中、高 |
| explanation | 可讀的推論說明 |
