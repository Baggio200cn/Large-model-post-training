"""
实时历史数据API
直接从彩票API获取最新历史记录
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
from urllib.parse import urlparse, parse_qs


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
            
            # 获取limit参数，默认10期
            limit = int(query_params.get('limit', ['10'])[0])
            limit = min(max(limit, 1), 50)
            
            # 从API获取数据
            history_data = self._fetch_history_data(limit)
            
            if not history_data:
                self._send_error_response(503, '数据获取失败', '无法从API获取数据')
                return
            
            # 返回成功结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'data': history_data,
                'total': len(history_data),
                'returned': len(history_data),
                'realtime': True
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, '服务器内部错误', str(e))
    
    def _fetch_history_data(self, limit):
        """从API获取历史数据"""
        try:
            url = f'https://www.mxnzp.com/api/lottery/common/latest?code=dlt&size={limit}'
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get('code') != 1:
                return None
            
            # 解析并格式化数据
            formatted_data = []
            for item in data.get('data', []):
                try:
                    # 解析开奖号码
                    numbers = item.get('openCode', '').split(',')
                    if len(numbers) >= 7:
                        red_balls = [int(n) for n in numbers[:5]]
                        blue_balls = [int(n) for n in numbers[5:7]]
                        
                        formatted_data.append({
                            'period': item.get('expect', ''),
                            'date': item.get('openTime', ''),
                            'red_balls': red_balls,
                            'blue_balls': blue_balls,
                            'display_code': self._format_display_code(red_balls, blue_balls)
                        })
                except (ValueError, AttributeError):
                    continue
            
            return formatted_data
            
        except Exception as e:
            print(f"数据获取错误: {e}")
            return None
    
    def _format_display_code(self, red_balls, blue_balls):
        """格式化显示号码"""
        red_str = ','.join([f'{n:02d}' for n in red_balls])
        blue_str = ','.join([f'{n:02d}' for n in blue_balls])
        return f"{red_str} + {blue_str}"
    
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