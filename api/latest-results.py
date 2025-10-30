"""
AI彩票分析实验室 - 最新结果API
版本: 2.0 - 返回实时时间戳
功能：
- 返回当前时间作为训练时间
- 可以扩展为返回最新一期的开奖结果
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import os


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
            # 尝试从数据文件获取更新时间
            update_time = self._get_data_update_time()
            
            if not update_time:
                # 使用当前时间
                update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            response = {
                'status': 'success',
                'updated_at': update_time,
                'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self._send_success_response(response)
            
        except Exception as e:
            print(f"Error in latest-results.py: {e}")
            # 即使出错也返回当前时间
            response = {
                'status': 'success',
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self._send_success_response(response)
    
    def _get_data_update_time(self):
        """尝试从数据文件获取更新时间"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'history.json'),
                '/var/task/data/raw/history.json',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 尝试从数据中获取更新时间
                    if isinstance(data, dict):
                        if 'updated_at_formatted' in data:
                            return data['updated_at_formatted']
                        elif 'updated_at' in data:
                            return data['updated_at']
            
            return None
            
        except Exception as e:
            print(f"Failed to get update time: {e}")
            return None
    
    def _send_success_response(self, data):
        """发送成功响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
