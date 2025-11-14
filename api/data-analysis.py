from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 导入历史数据和统计函数
try:
    from .lottery_historical_data import (
        get_historical_data, 
        get_hot_and_cold_numbers,
        get_number_frequency,
        get_latest_draw
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from lottery_historical_data import (
        get_historical_data, 
        get_hot_and_cold_numbers,
        get_number_frequency,
        get_latest_draw
    )

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 获取历史数据
            all_data = get_historical_data()
            latest = get_latest_draw()
            
            # 获取热号和冷号
            front_hot_cold = get_hot_and_cold_numbers('front', 10)
            back_hot_cold = get_hot_and_cold_numbers('back', 5)
            
            # 获取号码频率
            front_freq = get_number_frequency('front')
            back_freq = get_number_frequency('back')
            
            # 构建响应
            response = {
                'status': 'success',
                'analysis': {
                    'data_overview': {
                        'total_draws': len(all_data),
                        'analysis_period': f"{all_data[-1]['draw_date']} 至 {all_data[0]['draw_date']}",
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'latest_period': latest['period']
                    },
                    'front_zone_analysis': {
                        'hot_numbers': front_hot_cold['hot'][:5],
                        'cold_numbers': front_hot_cold['cold'][:5],
                        'most_frequent': sorted(front_freq.items(), key=lambda x: x[1], reverse=True)[:5],
                        'frequency_data': front_freq
                    },
                    'back_zone_analysis': {
                        'hot_numbers': back_hot_cold['hot'][:3],
                        'cold_numbers': back_hot_cold['cold'][:3],
                        'most_frequent': sorted(back_freq.items(), key=lambda x: x[1], reverse=True)[:3],
                        'frequency_data': back_freq
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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
