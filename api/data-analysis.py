from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 内联100期历史数据（与history.py相同）
LOTTERY_DATA = [
  {"period": "25123", "date": "2025-10-29", "front_1": 8, "front_2": 13, "front_3": 24, "front_4": 25, "front_5": 31, "back_1": 4, "back_2": 10},
  {"period": "25122", "date": "2025-10-27", "front_1": 2, "front_2": 3, "front_3": 6, "front_4": 16, "front_5": 17, "back_1": 4, "back_2": 5},
  {"period": "25121", "date": "2025-10-25", "front_1": 2, "front_2": 3, "front_3": 8, "front_4": 13, "front_5": 21, "back_1": 7, "back_2": 12},
  {"period": "25120", "date": "2025-10-22", "front_1": 11, "front_2": 13, "front_3": 22, "front_4": 26, "front_5": 35, "back_1": 2, "back_2": 8},
  {"period": "25119", "date": "2025-10-20", "front_1": 4, "front_2": 11, "front_3": 15, "front_4": 21, "front_5": 34, "back_1": 2, "back_2": 11},
  {"period": "25118", "date": "2025-10-18", "front_1": 3, "front_2": 10, "front_3": 19, "front_4": 23, "front_5": 33, "back_1": 1, "back_2": 8},
  {"period": "25117", "date": "2025-10-15", "front_1": 5, "front_2": 7, "front_3": 18, "front_4": 28, "front_5": 35, "back_1": 5, "back_2": 9},
  {"period": "25116", "date": "2025-10-13", "front_1": 1, "front_2": 4, "front_3": 14, "front_4": 23, "front_5": 30, "back_1": 3, "back_2": 12},
  {"period": "25115", "date": "2025-10-11", "front_1": 6, "front_2": 12, "front_3": 16, "front_4": 27, "front_5": 34, "back_1": 2, "back_2": 7},
  {"period": "25114", "date": "2025-10-08", "front_1": 9, "front_2": 15, "front_3": 20, "front_4": 25, "front_5": 32, "back_1": 4, "back_2": 11}
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            total = len(LOTTERY_DATA)
            
            # 计算前区号码频率
            front_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 6):
                    num = record[f'front_{i}']
                    front_freq[num] = front_freq.get(num, 0) + 1
            
            # 计算后区号码频率
            back_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 3):
                    num = record[f'back_{i}']
                    back_freq[num] = back_freq.get(num, 0) + 1
            
            # 排序获取热门号码
            hot_front = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
            hot_back = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
            
            response = {
                'status': 'success',
                'analysis': {
                    'data_overview': {
                        'total_draws': total,
                        'analysis_period': f'{LOTTERY_DATA[-1]["period"]} 至 {LOTTERY_DATA[0]["period"]}',
                        'last_update': LOTTERY_DATA[0]['date']
                    },
                    'front_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_front[:5]],
                        'hot_numbers': [x[0] for x in hot_front[:10]],
                        'cold_numbers': [x[0] for x in hot_front[-5:]]
                    },
                    'back_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_back[:2]],
                        'hot_numbers': [x[0] for x in hot_back[:5]],
                        'cold_numbers': [x[0] for x in hot_back[-3:]]
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
            
            import traceback
            error_response = {
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
