"""
历史数据API - 修复版（匹配前端格式）
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs


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
            # 解析查询参数
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            # 获取limit参数，默认10期
            limit = int(query_params.get('limit', ['10'])[0])
            limit = min(max(limit, 1), 50)  # 限制在1-50之间
            
            # 读取历史数据
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'raw', 'history.json'
            )
            
            if not os.path.exists(data_path):
                self._send_error_response(
                    404,
                    '数据文件未找到',
                    '请先运行数据采集脚本'
                )
                return
            
            # 加载数据
            with open(data_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            
            # 如果数据是字典格式（包含metadata），提取data字段
            if isinstance(all_data, dict):
                history_data = all_data.get('data', [])
            else:
                history_data = all_data
            
            # 取最近N期
            recent_data = history_data[:limit]
            
            # 返回成功结果 - 修改为前端期望的格式
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 返回前端期望的格式
            response = {
                'history': recent_data,  # 前端期望的字段名
                'total': len(history_data),
                'returned': len(recent_data)
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, '服务器内部错误', str(e))
    
    def _send_error_response(self, code, error, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': error,
            'message': message
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
```

---

## 📋 操作步骤

### Step 1: 更新 predict.py

1. 打开 GitHub：`https://github.com/Baggio200cn/Large-model-post-training/blob/main/api/predict.py`
2. 点击 ✏️ 编辑
3. 全选删除（Ctrl+A, Delete）
4. 粘贴上面的完整代码
5. 提交：`Fix predict.py response format to match frontend expectations`

### Step 2: 更新 history.py

1. 打开 GitHub：`https://github.com/Baggio200cn/Large-model-post-training/blob/main/api/history.py`
2. 点击 ✏️ 编辑
3. 全选删除
4. 粘贴上面的完整代码
5. 提交：`Fix history.py response format to match frontend expectations`

### Step 3: 等待 Vercel 自动部署

- 提交后等待 1-2 分钟
- Vercel 会自动检测并部署

### Step 4: 测试

1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 访问网站
3. 强制刷新（Ctrl+Shift+R）
4. 打开 F12 查看 Console

---

## ✅ 预期结果

修复后，您应该看到：
```
✅ main.js 加载完成！
🚀 页面加载完成，开始初始化...
📊 开始加载预测数据...
✅ 预测数据加载成功: {red_balls: [...], blue_balls: [...]}
📜 开始加载历史数据...
✅ 历史数据加载成功: {history: [...]}
🎨 开始渲染预测结果...
✅ 预测结果渲染完成
⏰ 时间戳更新: 2025-10-30 XX:XX:XX
✅ 时间显示已更新: 2025-10-30 XX:XX:XX
