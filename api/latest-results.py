from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 设置响应头
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 读取历史数据文件
            data_file = 'data/raw/history.json'
            
            if not os.path.exists(data_file):
                response = {
                    'status': 'error',
                    'message': '数据文件不存在'
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取数据
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 获取更新时间
            updated_at = data.get('updated_at_formatted', data.get('updated_at', ''))
            
            # 如果没有格式化时间，尝试格式化ISO时间
            if not updated_at or 'T' in updated_at:
                try:
                    iso_time = data.get('updated_at', '')
                    if iso_time:
                        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
                        updated_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 获取最新10期数据
            lottery_data = data.get('data', [])[:10]
            
            # 构建响应
            response = {
                'status': 'success',
                'updated_at': updated_at,
                'latest_results': lottery_data,
                'total_count': len(lottery_data)
            }
            
            # 返回JSON
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
```

5. 提交：`Add latest-results.py for timestamp API`

---

## 第3步：验证部署

### 3.1 等待Vercel自动部署

- GitHub提交后，Vercel会自动检测
- 通常需要 **1-2分钟**
- 可以在Vercel控制台查看部署状态

### 3.2 测试网站

1. 访问您的网站：
```
   https://large-model-post-training-xxx.vercel.app
```

2. **强制刷新** (清除缓存):
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **检查时间显示：**
   - 打开浏览器开发者工具（F12）
   - 查看 Console 标签
   - 应该看到：`⏰ 时间戳更新: 2025-10-30 XX:XX:XX`

### 3.3 验证清单

检查以下内容：

- [ ] 页面加载时显示"AI模型分析中..."
- [ ] 预测结果正常显示（红球+蓝球）
- [ ] **模型信息区域显示动态时间**（不是固定的10月23日）
- [ ] 历史记录正常加载
- [ ] Console没有红色错误信息

---

## 🔍 故障排查

### 问题1: 时间还是显示旧的固定时间

**解决方案：**
1. 清除浏览器缓存（Ctrl + Shift + Delete）
2. 检查 `/api/latest-results.py` 是否正确返回数据
3. 在浏览器访问：`https://你的域名/api/latest-results.py`
4. 应该看到包含 `updated_at` 字段的JSON

### 问题2: Console显示API错误

**检查：**
1. 网络标签（Network）查看API请求状态
2. 如果是404：确认API文件路径正确
3. 如果是500：检查Python代码语法

### 问题3: 页面空白或加载失败

**检查：**
1. F12打开Console查看错误信息
2. 确认 `main.js` 没有语法错误
3. 确认所有文件都已提交到GitHub

---

## 📊 预期效果对比

### ❌ 修改前
```
训练时间: 2025/10/23 14:13:28  （固定的）
```

### ✅ 修改后
```
训练时间: 2025-10-30 15:45:32  （动态的，每次数据更新都会变）
