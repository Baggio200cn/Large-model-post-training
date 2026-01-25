# 🔍 获取并更新Vercel实际域名

## 问题
当前文档中使用的都是占位符URL（如 `https://your-domain.vercel.app`），无法直接测试API。

## 解决方案

### 步骤1：获取实际Vercel域名

有以下3种方法：

#### 方法A：通过Vercel Dashboard（最简单）
1. 访问 https://vercel.com/dashboard
2. 登录您的账户
3. 找到项目 `Large-model-post-training`
4. 在项目页面顶部可以看到域名，例如：
   - `large-model-post-training.vercel.app` 或
   - `large-model-post-training-abc123xyz.vercel.app`

#### 方法B：通过最近的部署日志
1. 在Vercel Dashboard中进入项目
2. 点击 "Deployments" 标签
3. 查看最新的部署记录
4. 点击部署记录，可以看到 "Visit" 按钮旁边的域名

#### 方法C：通过Git部署输出
如果您最近推送过代码，Vercel的部署通知中会包含域名链接。

---

### 步骤2：更新文档中的占位符

#### 自动更新（推荐）

```bash
# 1. 编辑 .vercel-domain 文件，填入您的实际域名
nano .vercel-domain
# 将 VERCEL_DOMAIN=your-actual-domain.vercel.app
# 改为 VERCEL_DOMAIN=large-model-post-training-abc123.vercel.app

# 2. 运行更新脚本
./update-domain.sh

# 3. 提交更改
git add DEPLOYMENT.md docs/AUTO_TRAINING.md
git commit -m "docs: 更新Vercel域名为实际地址"
git push
```

#### 手动更新

如果您不想使用脚本，可以手动编辑以下文件：

1. **DEPLOYMENT.md**
   - 将 `your-project.vercel.app` 替换为实际域名
   - 将 `your-domain.vercel.app` 替换为实际域名

2. **docs/AUTO_TRAINING.md**
   - 将 `your-domain.com` 替换为实际域名

---

### 步骤3：测试API

更新域名后，您可以使用以下命令测试API（假设域名为 `large-model-post-training.vercel.app`）：

```bash
# 测试健康检查
curl https://large-model-post-training.vercel.app/api/health.py

# 测试最新开奖数据
curl https://large-model-post-training.vercel.app/api/latest-results.py

# 测试数据分析
curl https://large-model-post-training.vercel.app/api/data-analysis.py

# 测试AI预测
curl -X POST https://large-model-post-training.vercel.app/api/predict.py

# 测试训练状态
curl -X POST https://large-model-post-training.vercel.app/api/admin-data \
  -H "Content-Type: application/json" \
  -d '{"action": "training_status"}'
```

---

## 常见域名格式

Vercel项目的默认域名通常遵循以下格式之一：

1. **简单格式**：`<项目名>.vercel.app`
   - 示例：`large-model-post-training.vercel.app`

2. **带用户名格式**：`<项目名>-<用户名>.vercel.app`
   - 示例：`large-model-post-training-baggio200cn.vercel.app`

3. **带随机字符格式**：`<项目名>-<随机字符>.vercel.app`
   - 示例：`large-model-post-training-9xk2m.vercel.app`

---

## 快速检查

如果您忘记了域名，可以尝试以下常见组合：

```bash
# 尝试简单格式
curl https://large-model-post-training.vercel.app/api/health.py

# 如果上面不行，登录Vercel Dashboard查看确切域名
```

---

## 故障排除

### 问题：域名无法访问
- **检查1**：确认项目已成功部署（在Vercel Dashboard查看部署状态）
- **检查2**：确认URL中包含 `.py` 扩展名（例如：`/api/health.py`）
- **检查3**：检查浏览器控制台是否有CORS错误

### 问题：API返回404
- **原因**：缺少 `.py` 扩展名
- **解决**：确保URL格式为 `/api/<文件名>.py`

---

## 附录：项目API端点清单

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health.py` | GET | 健康检查 |
| `/api/test.py` | GET | 测试API |
| `/api/latest-results.py` | GET | 获取最新开奖结果 |
| `/api/data-analysis.py` | GET | 数据分析（热号、冷号） |
| `/api/predict.py` | POST | AI预测 |
| `/api/spiritual.py` | GET | 灵修因子 |
| `/api/generate-tweet.py` | POST | 生成推文 |
| `/api/admin-data` | POST | 管理数据（添加/查询） |

---

**更新时间**：2026-01-25
**问题反馈**：请提交Issue或联系开发团队
