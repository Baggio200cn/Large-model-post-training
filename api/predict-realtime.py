"""
实时预测API
直接从彩票API获取最新数据，实时计算预测
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
from collections import Counter


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
            # 1. 实时获取最新数据
            history_data = self._fetch_latest_data()
            
            if not history_data:
                self._send_error_response(503, '数据获取失败', '无法从API获取数据')
                return
            
            # 2. 实时计算频率
            red_freq, blue_freq = self._calculate_frequency(history_data)
            
            # 3. 生成预测
            predictions = self._generate_prediction(red_freq, blue_freq)
            
            # 4. 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'data': predictions,
                'disclaimer': '⚠️ 本预测仅供学习参考，不构成购彩建议。',
                'realtime': True,
                'data_source': 'Live API'
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, '服务器内部错误', str(e))
    
    def _fetch_latest_data(self):
        """从API获取最新数据"""
        try:
            url = 'https://www.mxnzp.com/api/lottery/common/latest?code=dlt&size=50'
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get('code') != 1:
                return None
            
            # 解析数据
            history = []
            for item in data.get('data', []):
                try:
                    # 解析开奖号码
                    numbers = item.get('openCode', '').split(',')
                    if len(numbers) >= 7:
                        history.append({
                            'period': item.get('expect', ''),
                            'date': item.get('openTime', ''),
                            'red_balls': [int(n) for n in numbers[:5]],
                            'blue_balls': [int(n) for n in numbers[5:7]]
                        })
                except (ValueError, AttributeError):
                    continue
            
            return history
            
        except Exception as e:
            print(f"数据获取错误: {e}")
            return None
    
    def _calculate_frequency(self, history_data):
        """计算号码频率"""
        red_counter = Counter()
        blue_counter = Counter()
        
        for record in history_data:
            red_counter.update(record['red_balls'])
            blue_counter.update(record['blue_balls'])
        
        # 计算概率
        total_draws = len(history_data)
        
        red_freq = {
            num: count / (total_draws * 5)
            for num, count in red_counter.items()
        }
        
        blue_freq = {
            num: count / (total_draws * 2)
            for num, count in blue_counter.items()
        }
        
        return red_freq, blue_freq
    
    def _generate_prediction(self, red_freq, blue_freq):
        """生成预测结果"""
        from datetime import datetime
        
        # 排序并取Top N
        red_sorted = sorted(red_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        blue_sorted = sorted(blue_freq.items(), key=lambda x: x[1], reverse=True)[:6]
        
        def get_reason(prob, ball_type):
            if ball_type == 'red':
                if prob > 0.025:
                    return "高频热号"
                elif prob > 0.02:
                    return "中频温号"
                else:
                    return "低频冷号"
            else:
                if prob > 0.1:
                    return "高频热号"
                elif prob > 0.08:
                    return "中频温号"
                else:
                    return "低频冷号"
        
        return {
            'red': [
                {
                    'number': int(n),
                    'probability': round(float(p), 4),
                    'reason': get_reason(p, 'red')
                }
                for n, p in red_sorted
            ],
            'blue': [
                {
                    'number': int(n),
                    'probability': round(float(p), 4),
                    'reason': get_reason(p, 'blue')
                }
                for n, p in blue_sorted
            ],
            'model_info': {
                'window_size': 50,
                'trained_at': datetime.now().isoformat(),
                'method': '实时频率分析'
            }
        }
    
    def _send_error_response(self, code, error, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': error,
            'message': message
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))