"""
AI彩票分析实验室 - 历史数据API
版本: 5.0 - 彻底修复日期计算问题
功能：严格遵循周一、三、六的开奖规律
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import random


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
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            limit = int(query_params.get('limit', ['10'])[0])
            limit = min(max(limit, 1), 50)
            
            # 尝试加载真实数据
            history_data = self._load_real_data()
            
            if not history_data or len(history_data) == 0:
                # 生成准确的2025年数据
                history_data = self._generate_accurate_2025_data(limit)
                data_source = 'accurate_simulation'
            else:
                data_source = 'real_file'
            
            recent_data = history_data[:limit]
            
            response = {
                'history': recent_data,
                'total': len(history_data),
                'returned': len(recent_data),
                'data_source': data_source,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self._send_success_response(response)
            
        except Exception as e:
            print(f"Error in history.py: {e}")
            mock_data = self._generate_accurate_2025_data(10)
            response = {
                'history': mock_data,
                'total': len(mock_data),
                'returned': len(mock_data),
                'data_source': 'error_fallback'
            }
            self._send_success_response(response)
    
    def _load_real_data(self):
        """尝试加载真实数据文件"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'history.json'),
                '/var/task/data/raw/history.json',
                os.path.join(current_dir, 'history.json'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
            
            return None
            
        except Exception as e:
            print(f"Failed to load real data: {e}")
            return None
    
    def _generate_accurate_2025_data(self, count):
        """
        生成准确的2025年数据
        严格按照周一、三、六的开奖规律
        """
        print(f"Generating {count} accurate 2025 records...")
        
        data = []
        
        # 2025年10月31日是周五
        # 我们需要找到最近的开奖日
        today = datetime(2025, 10, 31)
        
        # 生成最近的开奖日列表
        draw_dates = self._generate_draw_dates(today, count)
        
        base_period = 25126  # 假设10月29日（周三）是25126期
        
        for i, draw_date in enumerate(draw_dates):
            period = base_period - i
            
            # 使用期号作为随机种子
            random.seed(period + 54321)
            
            red_balls = sorted(random.sample(range(1, 36), 5))
            blue_balls = sorted(random.sample(range(1, 13), 2))
            
            data.append({
                'period': str(period),
                'date': draw_date.strftime('%Y-%m-%d'),
                'red_balls': red_balls,
                'blue_balls': blue_balls
            })
        
        # 验证生成的日期
        if len(data) > 0:
            print(f"Generated dates: {data[0]['date']} (期号{data[0]['period']}) to {data[-1]['date']} (期号{data[-1]['period']})")
            print(f"First date weekday: {draw_dates[0].strftime('%A')}")
            print(f"Last date weekday: {draw_dates[-1].strftime('%A')}")
        
        return data
    
    def _generate_draw_dates(self, from_date, count):
        """
        从指定日期往前生成count个开奖日
        确保都是周一、三、六
        """
        draw_dates = []
        current = from_date
        
        # 首先找到最近的（过去的）开奖日
        while len(draw_dates) < count:
            weekday = current.weekday()  # 0=周一, 1=周二, ..., 6=周日
            
            # 如果是开奖日（周一0、周三2、周六5）
            if weekday in [0, 2, 5]:
                # 确保时间已过（如果是今天，需要已过21:25）
                if current.date() < from_date.date() or \
                   (current.date() == from_date.date() and current.hour >= 21):
                    draw_dates.append(current.replace(hour=21, minute=25, second=0, microsecond=0))
                    
                    # 往前推到上一个开奖日
                    if weekday == 0:  # 周一 -> 上周六（往前2天）
                        current = current - timedelta(days=2)
                    elif weekday == 2:  # 周三 -> 周一（往前2天）
                        current = current - timedelta(days=2)
                    elif weekday == 5:  # 周六 -> 周三（往前3天）
                        current = current - timedelta(days=3)
                else:
                    # 如果是今天但时间未到，往前推
                    current = current - timedelta(days=1)
            else:
                # 不是开奖日，往前推一天
                current = current - timedelta(days=1)
        
        return draw_dates
    
    def _send_success_response(self, data):
        """发送成功响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
```

---

## 📅 验证修复后的日期

修复后应该显示：
```
期号     日期           星期
25126   2025-10-29    周三 ✅
25125   2025-10-27    周一 ✅  
25124   2025-10-25    周六 ✅
25123   2025-10-22    周三 ✅
25122   2025-10-20    周一 ✅
25121   2025-10-18    周六 ✅
25120   2025-10-15    周三 ✅
25119   2025-10-13    周一 ✅
25118   2025-10-11    周六 ✅
25117   2025-10-08    周三 ✅
