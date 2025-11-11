from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 内联历史数据（简化版，包含前10期）
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

def calculate_frequency():
    """计算号码频率"""
    front_freq = {}
    back_freq = {}
    
    for record in LOTTERY_DATA:
        for i in range(1, 6):
            num = record[f'front_{i}']
            front_freq[num] = front_freq.get(num, 0) + 1
        for i in range(1, 3):
            num = record[f'back_{i}']
            back_freq[num] = back_freq.get(num, 0) + 1
    
    return front_freq, back_freq

def strategy_conservative():
    """保守型：选择高频号码"""
    front_freq, back_freq = calculate_frequency()
    
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
    front_zone = [x[0] for x in front_sorted[:5]]
    
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
    back_zone = [x[0] for x in back_sorted[:2]]
    
    return sorted(front_zone), sorted(back_zone), 0.85

def strategy_balanced():
    """平衡型：频率+随机"""
    front_freq, back_freq = calculate_frequency()
    
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
    front_high = [x[0] for x in front_sorted[:3]]
    
    mid_freq_nums = [x[0] for x in front_sorted[5:15]] if len(front_sorted) > 15 else [x[0] for x in front_sorted[3:]]
    front_random = random.sample(mid_freq_nums, min(2, len(mid_freq_nums)))
    front_zone = front_high + front_random
    
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
    back_high = [back_sorted[0][0]] if back_sorted else [random.randint(1, 12)]
    back_mid = [x[0] for x in back_sorted[2:7]] if len(back_sorted) > 7 else [x[0] for x in back_sorted[1:]]
    back_random = random.sample(back_mid, min(1, len(back_mid))) if back_mid else [random.randint(1, 12)]
    back_zone = back_high + back_random
    
    return sorted(front_zone), sorted(back_zone), 0.78

def strategy_aggressive():
    """激进型：选择低频号码（冷门）"""
    front_freq, back_freq = calculate_frequency()
    
    # 获取所有可能的号码
    all_front = set(range(1, 36))
    all_back = set(range(1, 13))
    
    # 找出出现次数最少的号码
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1])
    front_zone = [x[0] for x in front_sorted[:5]]
    
    # 如果不足5个，从未出现的号码中随机选择
    if len(front_zone) < 5:
        appeared = set(front_freq.keys())
        not_appeared = list(all_front - appeared)
        front_zone.extend(random.sample(not_appeared, 5 - len(front_zone)))
    
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1])
    back_zone = [x[0] for x in back_sorted[:2]]
    
    if len(back_zone) < 2:
        appeared = set(back_freq.keys())
        not_appeared = list(all_back - appeared)
        back_zone.extend(random.sample(not_appeared, 2 - len(back_zone)))
    
    return sorted(front_zone), sorted(back_zone), 0.65

def strategy_random():
    """随机型：完全随机"""
    front_zone = sorted(random.sample(range(1, 36), 5))
    back_zone = sorted(random.sample(range(1, 13), 2))
    return front_zone, back_zone, 0.50

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取请求
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
            else:
                data = {}
            
            strategy = data.get('strategy', 'conservative')
            
            # 根据策略生成预测
            if strategy == 'conservative':
                front, back, conf = strategy_conservative()
                name = '保守型频率模型'
            elif strategy == 'balanced':
                front, back, conf = strategy_balanced()
                name = '平衡型频率+随机混合'
            elif strategy == 'aggressive':
                front, back, conf = strategy_aggressive()
                name = '激进型探索冷门'
            elif strategy == 'random':
                front, back, conf = strategy_random()
                name = '随机型完全随机探索'
            else:
                front, back, conf = strategy_conservative()
                name = '保守型频率模型'
            
            response = {
                'status': 'success',
                'prediction': {
                    'strategy': strategy,
                    'strategy_name': name,
                    'front_zone': front,
                    'back_zone': back,
                    'confidence': conf,
                    'based_on': len(LOTTERY_DATA)
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
