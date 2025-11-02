from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

try:
    from lottery_data import LOTTERY_DATA
except ImportError:
    LOTTERY_DATA = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not LOTTERY_DATA:
                raise Exception("数据未加载")
            
            # 获取最近10期
            recent_10 = LOTTERY_DATA[:10]
            
            # 格式化输出
            history = []
            for record in recent_10:
                history.append({
                    'period': record['period'],
                    'date': record['date'],
                    'front_zone': [
                        record['front_1'], record['front_2'],
                        record['front_3'], record['front_4'],
                        record['front_5']
                    ],
                    'back_zone': [record['back_1'], record['back_2']]
                })
            
            response = {
                'status': 'success',
                'history': history,
                'total': len(LOTTERY_DATA),
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
            
            error_response = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
