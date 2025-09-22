from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 获取环境信息用于诊断
        response = {
            'status': 'success',
            'message': 'Simple test API is working',
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'python_version': 'Available',
                'vercel_runtime': 'Working',
                'has_api_key': 'api_key' in os.environ,
                'environment_vars_count': len(os.environ)
            },
            'test_data': {
                'random_number': 42,
                'test_array': [1, 2, 3, 4, 5],
                'nested_object': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
