
# Large Model Post-Training Project

## 🎯 项目简介
本项目旨在构建一个基于大模型后训练的实验场，测试环境为中国大乐透有奖竞猜。通过整合多种模型的预测能力与灵修图片的随机性扰动，最终实现对下一期中奖号码的预测。

## 🏗️ 架构说明（2026-01更新）

本项目采用**前后端分离**架构：

### 前端
- 静态HTML/CSS/JavaScript页面
- 部署在Vercel/GitHub Pages
- 通过API动态获取数据

### 后端存储（腾讯云COS）
- **历史数据**：302期大乐透开奖数据（✅ 已上传）
- **ML模型**：4个机器学习模型文件
  - Random Forest（随机森林）
  - XGBoost
  - LSTM（长短期记忆网络）
  - Transformer

### API层
- FastAPI后端API
- 从腾讯云COS动态加载数据和模型
- 内置1小时缓存机制，减少COS请求

### 架构优势
✅ 数据和代码分离，便于独立更新
✅ 大文件存储在云端，不占用Git仓库空间
✅ 支持模型热更新，无需重新部署
✅ 高速CDN加速，提升访问速度

> 📖 **完整配置指南**：查看 [TENCENT_COS_SETUP.md](./TENCENT_COS_SETUP.md)

## 🚀 部署状态

- ✅ 腾讯云COS配置完成
- ✅ 302期历史数据已上传
- ✅ Vercel环境变量已配置
- 🔄 准备重新部署

## 项目目标
1. **数据分析与处理**：收集并清洗中国大乐透历史中奖数据。
2. **多模型训练与预测**：基于大模型（LSTM、Transformer等）训练历史数据，预测下一期中奖号码的概率值。
3. **灵修图片扰动模块**：引入灵修图片作为不确定性因素，调整预测权重。
4. **集成预测模块**：采用Stacking方法汇总各模块预测结果，并根据自学习算法调整权重。
5. **自动化推文生成**：输出详细的预测分析推文，采用中文Markdown格式。

## 文件结构
```
project/
├── data/
│   ├── raw_data/               # 原始数据
│   ├── processed_data/         # 处理后的数据
├── models/
│   ├── lstm_model.py           # LSTM模型代码
│   ├── transformer_model.py    # Transformer模型代码
│   ├── xgboost_model.py        # XGBoost模型代码
│   ├── rf_model.py             # Random Forest代码
├── spiritual/
│   ├── perturbation.py         # 灵修图片扰动模块代码
├── ensemble/
│   ├── stacking.py             # Stacking集成模型代码
├── utils/
│   ├── data_processing.py      # 数据处理工具
│   ├── markdown_generator.py   # Markdown推文生成工具
├── tests/
│   ├── test_models.py          # 各模型测试代码
├── main.py                     # 主程序入口
├── README.md                   # 项目说明文档
```

## 技术栈
- Python：数据分析与模型训练。
- HTML/CSS：项目网页设计与展示。
- GitHub Pages：项目托管与发布。

## 快速开始
1. 克隆仓库：
   ```bash
   git clone https://github.com/Baggio200cn/Large-model-post-training
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行项目：
   ```bash
   python main.py
   ```

## 贡献指南
欢迎所有对本项目感兴趣的开发者提交问题或贡献代码。请通过GitHub的`Issues`或`Pull Requests`功能进行协作。

## 许可
本项目遵循 [MIT License](LICENSE) 开源许可。
