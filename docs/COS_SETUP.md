# 腾讯云COS配置指南

## 为什么需要配置COS？

配置腾讯云COS后，您可以：
1. ✅ 自动将新增数据上传到云端存储
2. ✅ 自动上传训练好的ML模型
3. ✅ 实现数据的云端备份和同步
4. ✅ 多设备共享数据和模型

**不配置COS也能正常使用**，只是数据和模型仅保存在本地。

---

## 快速配置

### 1. 获取腾讯云密钥

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **访问管理** → **访问密钥** → **API密钥管理**
3. 创建密钥，获取：
   - `SecretId`
   - `SecretKey`

### 2. 创建COS存储桶

1. 进入 [COS控制台](https://console.cloud.tencent.com/cos5)
2. 创建存储桶：
   - 名称：例如 `lottery-data-1234567890`
   - 地域：例如 `广州(ap-guangzhou)`
   - 访问权限：`私有读写`

### 3. 设置环境变量

#### 方法1：在终端设置（临时）

```bash
export TENCENT_SECRET_ID=your_secret_id_here
export TENCENT_SECRET_KEY=your_secret_key_here
export TENCENT_COS_BUCKET=lottery-data-1234567890
export TENCENT_COS_REGION=ap-guangzhou
```

#### 方法2：在 `.env` 文件中设置（推荐）

创建项目根目录下的 `.env` 文件：

```env
# 腾讯云COS配置
TENCENT_SECRET_ID=your_secret_id_here
TENCENT_SECRET_KEY=your_secret_key_here
TENCENT_COS_BUCKET=lottery-data-1234567890
TENCENT_COS_REGION=ap-guangzhou
```

#### 方法3：在 Vercel 中设置（生产环境）

1. 进入 Vercel 项目设置
2. Environment Variables
3. 添加以上4个环境变量

---

## 验证配置

### 测试COS连接

```bash
cd Large-model-post-training
python scripts/upload_to_cos.py
```

**成功输出示例**：
```
✅ 彩票数据上传成功！
   COS路径: data/lottery_history.json
   数据量: 300 期
```

**失败输出示例**：
```
❌ 配置错误: 请设置TENCENT_SECRET_ID环境变量
```

---

## 配置后的效果

### 自动化流程

配置COS后，每次在后台添加数据时：

```
1. 用户添加数据
    ↓
2. 保存到本地 /tmp/user_lottery_data.json
    ↓
3. ✅ 自动更新 _lottery_data.py
    ↓
4. ✅ 自动上传到COS: data/lottery_history.json
    ↓
5. ✅ 触发模型训练
    ↓
6. ✅ 训练完成后上传模型到COS: models/*.pkl
```

### 后台管理界面提示

**配置COS前**：
```
成功添加期号 26010 的数据
✅ 本地同步成功（COS未配置）
✅ 模型训练已启动（后台运行）
```

**配置COS后**：
```
成功添加期号 26010 的数据
✅ 数据同步完成（本地✅ + COS✅）
✅ 模型训练已启动（后台运行）
```

---

## 常见问题

### Q1: 为什么显示"COS未配置"？

**答**：环境变量未设置。请按照上述步骤设置4个环境变量。

### Q2: 上传失败怎么办？

**可能原因**：
1. SecretId/SecretKey 错误
2. 存储桶名称或地域错误
3. 网络问题
4. 权限不足

**解决方法**：
```bash
# 检查环境变量
env | grep TENCENT

# 测试上传
python scripts/upload_to_cos.py
```

### Q3: 不配置COS影响使用吗？

**答**：不影响！系统会自动降级到本地模式：
- 数据保存在 `/tmp/user_lottery_data.json`
- 模型保存在 `data/models/`
- 预测功能正常使用

### Q4: 如何检查COS中的数据？

1. 登录 [COS控制台](https://console.cloud.tencent.com/cos5)
2. 进入您的存储桶
3. 查看文件：
   - `data/lottery_history.json` - 历史数据
   - `models/*.pkl` - Random Forest/XGBoost模型
   - `models/*.h5` - LSTM/Transformer模型

---

## 安全建议

### ⚠️ 保护您的密钥

1. **不要**将 `.env` 文件提交到Git
   ```bash
   # .gitignore
   .env
   ```

2. **不要**在代码中硬编码密钥

3. **定期轮换**密钥（每3-6个月）

4. **最小权限原则**：
   - 仅授予COS读写权限
   - 不要使用主账号密钥

---

## COS费用说明

### 存储费用

- **免费额度**：50GB/月（新用户6个月）
- **实际使用**：约 1-10MB（数据+模型）
- **月费用**：几乎免费

### 流量费用

- **内网流量**：免费
- **外网下载**：0.5元/GB
- **实际场景**：每月上传/下载 < 100MB，成本 < 0.1元

### 总结

**正常使用几乎免费**，无需担心费用问题。

---

## 进阶配置

### 启用版本控制

1. 进入COS控制台
2. 选择存储桶 → 数据管理 → 版本控制
3. 开启版本控制
4. 好处：可恢复历史版本

### 设置生命周期

自动删除旧版本模型：

1. 数据管理 → 生命周期
2. 添加规则：30天后删除旧版本
3. 节省存储空间

### 启用跨域访问（CORS）

如果前端需要直接访问COS：

```json
{
  "AllowedOrigins": ["*"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "ExposeHeaders": [],
  "MaxAgeSeconds": 3600
}
```

---

## 总结

✅ **推荐配置COS**，获得完整的自动化体验
⚠️ **不配置也能用**，只是数据仅保存在本地
📝 **配置简单**，只需4个环境变量

**立即开始配置** → [腾讯云控制台](https://console.cloud.tencent.com/)
