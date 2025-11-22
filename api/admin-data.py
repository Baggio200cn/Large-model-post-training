"""管理API - 数据CRUD操作"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import os

# 管理密码（从环境变量读取，默认值仅用于开发）
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'lottery2024')

try:
    from _db import get_all_lottery_data, add_lottery_data, delete_lottery_data, update_lottery_data
    USE_DATABASE = True
except:
    USE_DATABASE = False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            # 验证密码
            password = request_data.get('password', '')
            if password != ADMIN_PASSWORD:
                raise Exception('密码错误')
            
            if not USE_DATABASE:
                raise Exception('数据库未配置，无法使用管理功能')
            
            action = request_data.get('action', '')
            
            # 执行操作
            if action == 'list':
                data = get_all_lottery_data()
                result = {'success': True, 'data': data, 'count': len(data)}
            elif action == 'add':
                result = add_lottery_data(
                    period=request_data['period'],
                    date=request_data['date'],
                    front_zone=request_data['front_zone'],
                    back_zone=request_data['back_zone']
                )
            elif action == 'delete':
                result = delete_lottery_data(request_data['period'])
            elif action == 'update':
                result = update_lottery_data(
                    period=request_data['period'],
                    date=request_data['date'],
                    front_zone=request_data['front_zone'],
                    back_zone=request_data['back_zone']
                )
            else:
                result = {'success': False, 'message': '未知操作'}
            
            response = {
                'status': 'success' if result.get('success') else 'error',
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e), 'timestamp': datetime.now().isoformat()}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        self.do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

---

# 📄 文件7：`public/admin.html`

**（由于篇幅限制，我已经在上一条回复中提供了完整代码）**

---

## ✅ 部署检查清单

### 第1步：上传所有文件
```
✓ api/_lottery_data.py
✓ api/_ml_features.py  
✓ api/_ml_predictor.py
✓ api/predict.py
✓ api/_db.py
✓ api/admin-data.py
✓ public/admin.html
```

### 第2步：更新requirements.txt
```
requests==2.31.0
python-dateutil==2.8.2
pymongo==4.6.1
```

### 第3步：配置Vercel环境变量

**在Vercel Dashboard：**
1. Settings → Environment Variables
2. 添加：`MONGODB_URI` = `你的MongoDB连接字符串`
3. 添加：`ADMIN_PASSWORD` = `你的管理密码`

### 第4步：测试
```
1. 访问主页 - 点击"生成ML预测"
2. 访问 /admin.html - 输入密码登录
3. 添加一条测试数据
4. 再次测试预测功能
