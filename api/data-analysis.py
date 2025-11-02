from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 导入嵌入的数据
try:
    from lottery_data import LOTTERY_DATA
except ImportError:
    LOTTERY_DATA = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not LOTTERY_DATA:
                raise Exception("数据未加载")
            
            # 统计分析
            total_draws = len(LOTTERY_DATA)
            
            # 前区号码频率统计
            front_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 6):
                    num = record[f'front_{i}']
                    front_freq[num] = front_freq.get(num, 0) + 1
            
            # 后区号码频率统计
            back_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 3):
                    num = record[f'back_{i}']
                    back_freq[num] = back_freq.get(num, 0) + 1
            
            # 排序获取热门号码
            hot_front = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
            hot_back = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 最新日期
            last_update = LOTTERY_DATA[0]['date'] if LOTTERY_DATA else 'N/A'
            
            response = {
                'status': 'success',
                'analysis': {
                    'data_overview': {
                        'total_draws': total_draws,
                        'analysis_period': f'{LOTTERY_DATA[-1]["period"]} 至 {LOTTERY_DATA[0]["period"]}',
                        'last_update': last_update
                    },
                    'front_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_front[:5]],
                        'hot_numbers': [x[0] for x in hot_front[:10]],
                        'frequency_data': dict(hot_front[:10])
                    },
                    'back_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_back[:2]],
                        'hot_numbers': [x[0] for x in hot_back[:5]],
                        'frequency_data': dict(hot_back[:5])
                    }
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
