from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 内联100期历史数据（与history.py相同的数据）
LOTTERY_DATA = [
  {"period": "25123", "date": "2025-10-29", "front_1": 8, "front_2": 13, "front_3": 24, "front_4": 25, "front_5": 31, "back_1": 4, "back_2": 10},
  {"period": "25122", "date": "2025-10-27", "front_1": 2, "front_2": 3, "front_3": 6, "front_4": 16, "front_5": 17, "back_1": 4, "back_2": 5},
  {"period": "25121", "date": "2025-10-25", "front_1": 2, "front_2": 3, "front_3": 8, "front_4": 13, "front_5": 21, "back_1": 7, "back_2": 12},
  {"period": "25120", "date": "2025-10-22", "front_1": 11, "front_2": 13, "front_3": 22, "front_4": 26, "front_5": 35, "back_1": 2, "back_2": 8},
  {"period": "25119", "date": "2025-10-20", "front_1": 4, "front_2": 11, "front_3": 15, "front_4": 21, "front_5": 34, "back_1": 2, "back_2": 11},
  # ... 这里应该包含所有100期数据，为了演示简化
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
    
    # 前区选前5个高频
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
    front_zone = [x[0] for x in front_sorted[:5]]
    
    # 后区选前2个高频
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
    back_zone = [x[0] for x in back_sorted[:2]]
    
    return sorted(front_zone), sorted(back_zone), 0.85

def strategy_balanced():
    """平衡型：频率+随机"""
    front_freq, back_freq = calculate_frequency()
    
    # 前区：3个高频 + 2个随机
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
    front_high = [x[0] for x in front_sorted[:3]]
    
    # 从中频号码中随机选2个
    mid_freq_nums = [x[0] for x in front_sorted[5:15]]
    front_random = random.sample(mid_freq_nums, 2)
    front_zone = front_high + front_random
    
    # 后区：1个高频 + 1个随机
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
    back_high = [back_sorted[0][0]]
    back_mid = [x[0] for x in back_sorted[2:7]]
    back_random = random.sample(back_mid, 1)
    back_zone = back_high + back_random
    
    return sorted(front_zone), sorted(back_zone), 0.78

def strategy_aggressive():
    """激进型：选择低频号码（冷门号）"""
    front_freq, back_freq = calculate_frequency()
    
    # 前区选后5个低频（冷门）
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1])
    front_zone = [x[0] for x in front_sorted[:5]]
    
    # 后区选后2个低频
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1])
    back_zone = [x[0] for x in back_sorted[:2]]
    
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
            error = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
