# 腾讯云COS集成配置指南

## 📋 架构说明

本项目采用**前后端分离**架构：

- **前端**：静态HTML/CSS/JavaScript页面（部署在Vercel）
- **后端数据存储**：腾讯云对象存储（COS）
  - 500期历史开奖数据
  - 4个机器学习模型文件
- **API**：从腾讯云COS动态加载数据和模型

### 优势

✅ 数据和模型分离，便于更新
✅ 不需要重新部署即可更新数据
✅ 降低Vercel存储压力
✅ 支持大文件存储（模型文件）
✅ 高速CDN加速访问

---

## 🚀 第一步：创建腾讯云COS存储桶

### 1. 登录腾讯云控制台

访问：https://console.cloud.tencent.com/cam

### 2. 创建COS存储桶

1. 进入 **对象存储 COS** 控制台
2. 点击 **创建存储桶**
3. 配置参数：
   - **名称**：`lottery-ml-data`（自定义）
   - **所属地域**：选择最近的地域（如：广州）
   - **访问权限**：私有读写（推荐）
   - **其他**：保持默认

### 3. 获取访问密钥

1. 进入 **访问管理 CAM** → **访问密钥**
2. 点击 **新建密钥**
3. 保存 **SecretId** 和 **SecretKey**（后续需要）

---

## 🔧 第二步：本地环境配置

### 1. 安装依赖

```bash
pip install cos-python-sdk-v5
```

### 2. 配置环境变量

创建 `.env` 文件（或在Vercel中配置）：

```bash
# 腾讯云COS配置
TENCENT_SECRET_ID=你的SecretId
TENCENT_SECRET_KEY=你的SecretKey
TENCENT_COS_BUCKET=lottery-ml-data  # 你的存储桶名称
TENCENT_COS_REGION=ap-guangzhou     # 你的区域
```

### 3. 区域代码对照表

| 地域 | Region |
|------|--------|
| 广州 | ap-guangzhou |
| 上海 | ap-shanghai |
| 北京 | ap-beijing |
| 成都 | ap-chengdu |
| 香港 | ap-hongkong |

---

## 📤 第三步：上传数据和模型

### 1. 准备训练数据

```bash
python scripts/prepare_training_data.py
```

输出：`data/training/` 目录下的训练数据文件

### 2. 训练机器学习模型

```bash
python scripts/train_models.py
```

这将训练4个模型：
- Random Forest（随机森林）
- XGBoost
- LSTM（长短期记忆网络）
- Transformer

输出：`data/models/` 目录下的模型文件

### 3. 上传到腾讯云COS

```bash
# 设置环境变量（如果还没有）
export TENCENT_SECRET_ID=你的SecretId
export TENCENT_SECRET_KEY=你的SecretKey
export TENCENT_COS_BUCKET=lottery-ml-data
export TENCENT_COS_REGION=ap-guangzhou

# 运行上传脚本
python scripts/upload_to_cos.py
```

上传内容：
- ✅ `data/lottery_history.json` - 500期历史数据
- ✅ `models/random_forest_front.pkl` - 随机森林模型
- ✅ `models/xgboost_front.pkl` - XGBoost模型
- ✅ `models/lstm_front.h5` - LSTM模型
- ✅ `models/transformer_front.h5` - Transformer模型
- ✅ `models/models_info.json` - 模型元数据

### 4. 验证上传

```bash
# 测试从COS加载数据
python -c "from api._cos_data_loader import get_lottery_data; print(f'加载了 {len(get_lottery_data())} 期数据')"
```

---

## 🌐 第四步：Vercel部署配置

### 1. 在Vercel中添加环境变量

进入你的Vercel项目 → Settings → Environment Variables

添加：
```
TENCENT_SECRET_ID = 你的SecretId
TENCENT_SECRET_KEY = 你的SecretKey
TENCENT_COS_BUCKET = lottery-ml-data
TENCENT_COS_REGION = ap-guangzhou
```

### 2. 重新部署

```bash
git add .
git commit -m "feat: 集成腾讯云COS存储"
git push origin main
```

Vercel会自动重新部署。

---

## 🔄 第五步：更新数据流程

当需要更新彩票数据或重新训练模型时：

### 1. 更新历史数据

编辑 `api/_lottery_data.py`，添加新的开奖数据

### 2. 重新训练模型

```bash
python scripts/prepare_training_data.py
python scripts/train_models.py
```

### 3. 重新上传到COS

```bash
python scripts/upload_to_cos.py
```

### 4. 清除缓存

API会自动缓存数据1小时，如需立即更新：

```bash
# 在API中调用
from api._cos_data_loader import clear_cache
clear_cache()
```

或者等待1小时后缓存自动过期。

---

## 📊 COS文件结构

```
你的存储桶/
├── data/
│   └── lottery_history.json          # 500期历史数据
├── models/
│   ├── random_forest_front.pkl       # 随机森林模型
│   ├── xgboost_front.pkl             # XGBoost模型
│   ├── lstm_front.h5                 # LSTM模型
│   ├── transformer_front.h5          # Transformer模型
│   └── models_info.json              # 模型元数据
└── training/
    ├── training_data.pkl             # 训练数据
    └── metadata.json                 # 数据元数据
```

---

## 🛡️ 安全建议

1. **永远不要**将 SecretId 和 SecretKey 提交到Git仓库
2. 使用环境变量或密钥管理服务
3. 定期更换访问密钥
4. 设置COS访问权限为"私有读写"
5. 启用COS访问日志监控异常访问

---

## ❓ 常见问题

### Q1: 上传失败怎么办？

检查：
- 网络连接是否正常
- SecretId 和 SecretKey 是否正确
- 存储桶名称和区域是否匹配
- 是否有COS写入权限

### Q2: API加载数据失败？

- 首先会尝试从COS加载
- 如果失败，自动回退到本地数据
- 检查环境变量是否在Vercel中正确配置

### Q3: 模型文件太大怎么办？

- COS支持最大5GB单个文件
- 使用分块上传（已内置）
- 考虑模型压缩或量化

### Q4: 如何节省COS成本？

- 使用CDN加速（可选）
- 启用数据缓存（已内置1小时缓存）
- 定期清理旧数据
- 使用归档存储（不常用数据）

---

## 📝 API使用示例

### 在API中加载数据

```python
from api._cos_data_loader import get_lottery_data, load_model_from_cos

# 加载彩票数据（自动缓存）
data = get_lottery_data()
print(f"加载了 {len(data)} 期数据")

# 加载模型（自动缓存）
rf_model = load_model_from_cos('random_forest_front')

# 强制刷新缓存
data = get_lottery_data(force_refresh=True)
```

### 查看缓存状态

```python
from api._cos_data_loader import get_cache_status

status = get_cache_status()
print(status)
```

---

## 📞 技术支持

- 腾讯云COS文档：https://cloud.tencent.com/document/product/436
- Python SDK文档：https://cloud.tencent.com/document/product/436/12269

---

## ✅ 完成检查清单

- [ ] 创建腾讯云账号
- [ ] 创建COS存储桶
- [ ] 获取访问密钥
- [ ] 本地配置环境变量
- [ ] 训练机器学习模型
- [ ] 上传数据和模型到COS
- [ ] 在Vercel配置环境变量
- [ ] 部署并测试API
- [ ] 验证数据加载正常

恭喜！🎉 你已经成功集成腾讯云COS存储！
