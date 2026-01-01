# 🚀 大乐透AI预测系统 - 部署指南

## ✅ 当前状态

- **数据量：** 83期真实历史数据
- **期号范围：** 25047 - 25129
- **更新日期：** 2024-11-14
- **部署平台：** Vercel

---

## 📊 系统功能

### API端点

1. **健康检查**
```
   GET /api/health.py
```

2. **最新开奖**
```
   GET /api/latest-results.py
   返回：最新一期开奖数据
```

3. **数据分析**
```
   GET /api/data-analysis.py
   返回：热号、冷号、频率统计
```

4. **AI预测**
```
   POST /api/predict.py
   返回：基于历史数据的预测结果
```

5. **灵修因子**
```
   GET /api/spiritual.py
   返回：灵修扰动因子
```

6. **生成推文**
```
   POST /api/generate-tweet.py
   返回：格式化的预测分析报告
```

---

## 🔄 数据更新流程

### 每周更新步骤

1. **获取最新开奖数据**
   - 截图官网开奖信息
   - 上传给Claude识别

2. **更新数据文件**
   - Claude生成新的 `lottery_historical_data.py`
   - 复制到 `api/` 目录

3. **提交到GitHub**
```bash
   git add api/lottery_historical_data.py
   git commit -m "Update: Add period XXXXX"
   git push
```

4. **自动部署**
   - Vercel自动检测更新
   - 2-3分钟完成部署
   - 系统自动使用新数据

### 数据格式
```python
{
    "period": "25129",
    "draw_date": "2025-11-12",
    "front_zone": [3, 9, 14, 28, 35],
    "back_zone": [2, 4]
}
```

---

## 🎯 验证部署

### 测试API
```bash
# 测试健康检查
curl https://your-project.vercel.app/api/health.py

# 测试最新数据
curl https://your-project.vercel.app/api/latest-results.py

# 测试预测
curl -X POST https://your-project.vercel.app/api/predict.py
```

### 期望结果

- ✅ 返回状态码 200
- ✅ JSON格式正确
- ✅ 包含真实数据
- ✅ 最新期号为 25129

---

## 📝 注意事项

1. **数据文件位置**
   - 必须在 `api/lottery_historical_data.py`
   - 不要放在其他目录

2. **文件格式**
   - 确保Python语法正确
   - 保持数据格式统一

3. **更新频率**
   - 建议每周开奖后更新
   - 保持数据新鲜度

4. **备份建议**
   - Git自动保存历史版本
   - 可随时回滚

---

## 🛠️ 故障排查

### 问题1：API返回404

**原因：** URL缺少 `.py` 扩展名

**解决：**
```
❌ /api/health
✅ /api/health.py
```

### 问题2：数据不是最新

**原因：** 缓存未更新

**解决：**
1. 清除浏览器缓存
2. 等待2-3分钟
3. 强制刷新页面

### 问题3：导入错误

**原因：** 文件路径问题

**解决：**
- 确认 `lottery_historical_data.py` 在 `api/` 目录
- 检查文件名拼写

---

## 📞 技术支持

遇到问题请检查：

1. Vercel部署日志
2. 浏览器控制台
3. API响应内容
4. 文件路径和命名

---

**最后更新：** 2024-11-14  
**数据版本：** v1.0 (83期)
