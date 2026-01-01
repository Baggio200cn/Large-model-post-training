# API 文档

## 1. 机器学习/统计预测
- **路径**：`/api/ml_stats_predict`
- **方法**：POST
- **请求参数**：
  - `csv_path` (string, 可选)：数据文件路径，默认`data/processed_samlpe.csv`
  - `target_col` (string, 可选)：目标列名
- **返回**：
  - `ml_result`：机器学习模型结果
  - `stats_result`：统计建模结果
  - `timestamp`：时间戳

## 2. 模型融合预测
- **路径**：`/api/model_fusion`
- **方法**：POST
- **请求参数**：
  - `csv_path` (string, 可选)：数据文件路径
  - `target_col` (string, 可选)：目标列名
- **返回**：
  - `fusion_prediction`：融合预测结果
  - `rf_prediction`：随机森林预测
  - `ols_prediction`：OLS预测
  - `fusion_strategy`：融合策略说明
  - `timestamp`：时间戳

## 3. 数据分析报告
- **路径**：`/api/latest-results`
- **方法**：POST
- **请求参数**：
  - `csv_path` (string, 可选)：数据文件路径
  - `current_period` (string, 可选)
  - `last_period` (string, 可选)
- **返回**：
  - `report.content`：HTML分析表格
  - `report.format`：内容格式
  - `period`：期号
  - `generated_at`：生成时间
  - `timestamp`：时间戳
