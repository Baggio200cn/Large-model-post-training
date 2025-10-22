# 🎯 AI彩票分析实验室

> 用有趣的方式教授AI技术 - 探索随机性与模式识别的边界

## 📖 项目简介

这是一个教育性质的AI项目，通过大乐透数据分析展示完整的数据科学流程。

**重要声明：** 本项目仅用于技术学习和AI科普，不能提高彩票中奖率。彩票是完全随机的，请理性对待。

## ✨ 核心特色

- 🎓 **教育性**：完整的数据科学项目流程
- 🔬 **技术展示**：从数据采集到模型部署
- 💡 **创新点**：灵修因子系统（图像哈希 → 伪随机因子）
- 📝 **科普文章**：自动生成通俗易懂的AI知识文章
- 🚀 **全免费**：基于Vercel + GitHub，零成本运行

## 🏗️ 技术架构

```
前端: Vercel静态托管
API: Vercel Serverless Functions
数据: GitHub仓库
训练: GitHub Actions
模型: 轻量级ML（scikit-learn）
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone <your-repo-url>
cd lottery-ai-lab

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# 从 https://www.mxnzp.com 获取彩票API密钥
```

### 3. 采集数据

```bash
python scripts/collect_data.py
```

### 4. 训练模型

```bash
python scripts/train_simple_model.py
```

### 5. 本地运行

```bash
# 安装Vercel CLI
npm i -g vercel

# 本地开发
vercel dev
```

## 📁 项目结构

```
lottery-ai-lab/
├── api/                    # Vercel API函数
├── public/                 # 前端静态文件
├── src/                    # 核心业务逻辑
│   ├── data/              # 数据处理
│   ├── models/            # 模型定义
│   ├── spiritual/         # 灵修因子系统
│   └── utils/             # 工具函数
├── data/                  # 数据文件
├── scripts/               # 脚本工具
└── tests/                 # 测试文件
```

## 🎓 科普文章系列

1. AI能预测彩票吗？
2. 数据科学完整流程
3. 特征工程的艺术
4. 随机森林模型解密
5. 哈希函数的魔法
6. 贝叶斯定理入门
7. 数据可视化技巧
8. API设计最佳实践

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目仅用于AI技术学习和科普教育。彩票是完全随机的，任何预测方法都不能提高中奖概率。请理性购彩，不要沉迷。

---

**记住：AI是工具，不是魔法** 🎓
