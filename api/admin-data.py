from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from _db import get_all_lottery_data, add_lottery_data, delete_lottery_data, update_lottery_data

# 简单的密码保护（后续可以改进）
ADMIN_PASSWORD = "lottery2024"  # 建议从环境变量读取

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取请求
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
            
            action = request_data.get('action', '')
            
            # 执行操作
            if action == 'list':
                # 获取所有数据
                data = get_all_lottery_data()
                result = {'success': True, 'data': data, 'count': len(data)}
            
            elif action == 'add':
                # 添加数据
                result = add_lottery_data(
                    period=request_data['period'],
                    date=request_data['date'],
                    front_zone=request_data['front_zone'],
                    back_zone=request_data['back_zone']
                )
            
            elif action == 'delete':
                # 删除数据
                result = delete_lottery_data(request_data['period'])
            
            elif action == 'update':
                # 更新数据
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
        # GET请求返回所有数据（需要密码参数）
        self.do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
