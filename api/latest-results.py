from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 导入历史数据
try:
    from .lottery_historical_data import get_latest_draw, get_historical_data
except ImportError:
    # 备用导入方式
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from lottery_historical_data import get_latest_draw, get_historical_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 获取最新一期数据
            latest = get_latest_draw()
            
            if not latest:
                raise Exception("没有可用的历史数据")
            
            # 构建响应
            response = {
                'status': 'success',
                'latest_results': {
                    'period': latest['period'],
                    'draw_date': latest['draw_date'],
                    'winning_numbers': {
                        'front_zone': latest['front_zone'],
                        'back_zone': latest['back_zone'],
                        'display': f"{' '.join([f'{n:02d}' for n in latest['front_zone']])} + {' '.join([f'{n:02d}' for n in latest['back_zone']])}"
                    }
                },
                'data_info': {
                    'total_periods': len(get_historical_data()),
                    'data_source': 'Real historical data'
                },
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
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
