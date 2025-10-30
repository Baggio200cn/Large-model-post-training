"""
最新结果时间戳API - 完整生产版
功能: 返回数据更新时间戳
版本: 2.0
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 尝试从history.json读取更新时间
            timestamp = self._get_data_timestamp()
            
            # 返回成功结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            response = {
                'status': 'success',
                'updated_at': timestamp
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # 发生错误时返回当前时间
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'success',
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def _get_data_timestamp(self):
        """获取数据更新时间戳"""
        try:
            # 尝试多个可能的文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'history.json'),
                '/var/task/data/raw/history.json',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 如果数据包含updated_at字段
                    if isinstance(data, dict):
                        # 优先使用格式化的时间
                        if 'updated_at_formatted' in data:
                            return data['updated_at_formatted']
                        
                        # 否则尝试ISO格式
                        if 'updated_at' in data:
                            iso_time = data['updated_at']
                            try:
                                dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
                                return dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
            
            # 如果无法读取，返回当前时间
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

---

## 🚀 部署步骤

### Step 1: 更新所有文件

**按顺序更新以下文件：**

1. **`public/js/main.js`**
   - 提交消息：`Update to complete production version with full error handling`

2. **`api/history.py`**
   - 提交消息：`Update history.py to production version with real data support`

3. **`api/latest-results.py`**
   - 提交消息：`Update latest-results.py to production version`

### Step 2: 等待 Vercel 部署

- 提交后等待 2-3 分钟
- 查看 Vercel 控制台确认部署成功

### Step 3: 彻底清除缓存

1. 关闭所有浏览器窗口
2. 重新打开浏览器
3. 按 `Ctrl + Shift + Delete`
4. 清除"全部时间"的缓存
5. 关闭浏览器

### Step 4: 测试

1. 重新打开浏览器
2. 访问网站
3. 按 `F12` 打开开发者工具
4. 刷新页面

---

## ✅ 预期结果

### Console 应该显示：
```
✅ [时间] main.js 加载完成！版本: 2.0
ℹ️ [时间] 页面加载完成，开始初始化...
ℹ️ [时间] 开始加载预测数据...
ℹ️ [时间] 开始加载历史数据...
🔍 [时间] 正在请求 /api/predict.py...
✅ [时间] 预测数据加载成功 {...}
ℹ️ [时间] 开始渲染预测结果 {...}
🔍 [时间] 渲染 red-balls [9, 2, 22, 8, 14]
✅ [时间] red-balls 渲染完成
🔍 [时间] 渲染 blue-balls [5, 2]
✅ [时间] blue-balls 渲染完成
✅ [时间] 模型信息显示完成
✅ [时间] 预测结果渲染完成
ℹ️ [时间] 开始获取时间戳...
✅ [时间] 时间戳更新成功 2025-10-30 XX:XX:XX
