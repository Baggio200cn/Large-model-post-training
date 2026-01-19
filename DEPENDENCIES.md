# 项目依赖说明

## 📦 依赖文件结构

本项目使用分离的依赖管理策略：

### `requirements.txt` - 生产环境（Vercel）

**用途**：Vercel 部署时使用的轻量级依赖

**包含**：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `requests` - HTTP 请求
- `cos-python-sdk-v5` - 腾讯云 COS SDK
- `python-multipart` - 文件上传处理
- `beautifulsoup4` - HTML 解析
- `jinja2` - 模板引擎

**大小**：约 20-30 MB

**说明**：
- ✅ 只包含 API 运行必需的库
- ✅ 不包含 ML 训练库（TensorFlow、scikit-learn等）
- ✅ 符合 Vercel 300MB 限制

---

### `requirements-dev.txt` - 开发环境（本地）

**用途**：本地开发、模型训练、数据处理

**包含**：
- 所有生产环境的依赖
- `tensorflow` - 深度学习框架
- `scikit-learn` - 传统机器学习
- `xgboost` - 梯度提升模型
- `pandas` - 数据处理
- `numpy` - 数值计算

**大小**：约 500-800 MB

**说明**：
- ✅ 包含完整的开发和训练工具
- ✅ 用于本地模型训练
- ❌ 不用于 Vercel 部署（太大）

---

## 🚀 使用方法

### Vercel 部署（自动）
Vercel 会自动使用 `requirements.txt`，无需配置。

### 本地开发
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 或者分别安装
pip install -r requirements.txt          # 基础依赖
pip install -r requirements-dev.txt      # 开发依赖
```

### 本地训练模型
```bash
# 1. 安装完整依赖
pip install -r requirements-dev.txt

# 2. 准备训练数据
python scripts/prepare_training_data.py

# 3. 训练模型
python scripts/train_models.py

# 4. 上传到腾讯云
python scripts/upload_to_cos.py
```

---

## 📊 依赖大小对比

| 依赖文件 | 用途 | 大小 | Vercel 兼容 |
|---------|------|------|------------|
| requirements.txt | 生产API | ~30 MB | ✅ 是 |
| requirements-dev.txt | 开发训练 | ~800 MB | ❌ 否 |

---

## ⚠️ 重要说明

### 为什么分离依赖？

1. **Vercel 限制**：部署包不能超过 300MB
2. **实际需求**：API 只需要读取数据，不需要运行模型
3. **性能优化**：减少部署时间和冷启动时间

### 模型在哪里？

- ❌ 不在 Vercel 上
- ✅ 在腾讯云 COS 上
- ✅ API 通过 COS SDK 访问

### 如果需要在 Vercel 上运行模型？

不推荐，因为：
1. Serverless 环境不适合运行大型 ML 模型
2. 部署包大小限制
3. 冷启动时间过长

如果确实需要，考虑：
1. 使用 Vercel Edge Functions
2. 或者部署到其他平台（如 AWS Lambda、Google Cloud Run）
3. 或者使用模型服务化（如 TensorFlow Serving）

---

## 🔄 更新依赖

### 更新生产依赖
```bash
# 编辑 requirements.txt
vim requirements.txt

# 测试
pip install -r requirements.txt

# 提交
git add requirements.txt
git commit -m "chore: update production dependencies"
git push
```

### 更新开发依赖
```bash
# 编辑 requirements-dev.txt
vim requirements-dev.txt

# 测试
pip install -r requirements-dev.txt

# 提交
git add requirements-dev.txt
git commit -m "chore: update development dependencies"
git push
```

---

## 📝 版本历史

- **2026-01-19**: 分离生产和开发依赖
  - 创建 `requirements.txt`（轻量版）
  - 创建 `requirements-dev.txt`（完整版）
  - 解决 Vercel 300MB 限制问题
