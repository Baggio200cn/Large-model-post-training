"""
历史数据API - 日期修复版
版本: 3.1 - 确保周一、三、六的正确性
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta


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
            # 解析查询参数
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            limit = int(query_params.get('limit', ['10'])[0])
            limit = min(max(limit, 1), 50)
            
            # 尝试读取真实数据
            history_data = self._load_real_data()
            
            if not history_data:
                history_data = self._generate_realistic_mock_data(limit)
                data_source = 'mock'
            else:
                data_source = 'file'
            
            recent_data = history_data[:limit]
            
            self._send_success_response({
                'history': recent_data,
                'total': len(history_data),
                'returned': len(recent_data),
                'data_source': data_source
            })
            
        except Exception as e:
            mock_data = self._generate_realistic_mock_data(10)
            self._send_success_response({
                'history': mock_data,
                'total': len(mock_data),
                'returned': len(mock_data),
                'data_source': 'mock'
            })
    
    def _load_real_data(self):
        """尝试加载真实数据"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'history.json'),
                '/var/task/data/raw/history.json',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        all_data = json.load(f)
                    
                    if isinstance(all_data, dict):
                        return all_data.get('data', [])
                    else:
                        return all_data
            
            return None
        except:
            return None
    
    def _generate_realistic_mock_data(self, count):
        """生成符合真实规律的模拟数据（周一、三、六）"""
        import random
        
        # 2025年10月30日是周四
        # 最近的开奖日应该是10月28日（周二）不对
        # 让我重新算：2025-10-30是周四
        # 最近的开奖日应该是10-28（周二）？不对，10-28不是开奖日
        # 10-27是周一 ✓
        # 10-26是周日
        # 10-25是周六 ✓
        
        # 定义2025年10月的开奖日（实际日期）
        # 周一、三、六开奖
        known_dates = [
            '2025-10-27',  # 周一
            '2025-10-25',  # 周六
            '2025-10-23',  # 周四？错了，应该是周三 - 让我重新计算
        ]
        
        # 让我用更可靠的方法：从今天往前推
        today = datetime(2025, 10, 30)  # 周四
        
        draw_dates = []
        current_date = today
        
        # 生成count个开奖日期
        while len(draw_dates) < count:
            # 往前找开奖日（周一=0, 周三=2, 周六=5）
            weekday = current_date.weekday()
            
            if weekday in [0, 2, 5]:  # 周一、三、六
                draw_dates.append(current_date)
                # 找下一个开奖日
                if weekday == 0:  # 周一 -> 上周六
                    current_date = current_date - timedelta(days=2)
                elif weekday == 2:  # 周三 -> 周一
                    current_date = current_date - timedelta(days=2)
                elif weekday == 5:  # 周六 -> 周三
                    current_date = current_date - timedelta(days=3)
            else:
                # 如果不是开奖日，往前推一天
                current_date = current_date - timedelta(days=1)
        
        # 生成数据
        mock_data = []
        for i, draw_date in enumerate(draw_dates):
            period = 25126 - i
            
            # 生成随机号码
            random.seed(period)
            red_balls = sorted(random.sample(range(1, 36), 5))
            blue_balls = sorted(random.sample(range(1, 13), 2))
            
            mock_data.append({
                'period': str(period),
                'date': draw_date.strftime('%Y-%m-%d'),
                'red_balls': red_balls,
                'blue_balls': blue_balls
            })
        
        return mock_data
    
    def _send_success_response(self, data):
        """发送成功响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
