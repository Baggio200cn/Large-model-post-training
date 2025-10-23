"""
历史数据API
返回最近N期的开奖记录
"""

from http.server import BaseHTTPRequestHandler
import json
import os
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
            limit = min(max(limit, 1), 50)  # 限制在1-50之间
            
            # 读取历史数据
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'raw', 'history.json'
            )
            
            if not os.path.exists(data_path):
                self._send_error_response(
                    404,
                    '数据文件未找到',
                    '请先运行数据采集脚本'
                )
                return
            
            # 加载数据
            with open(data_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            
            # 取最近N期
            recent_data = all_data[:limit]
            
            # 格式化数据
            formatted_data = []
            for item in recent_data:
                formatted_data.append({
                    'period': item['period'],
                    'date': item['date'],
                    'red_balls': item['red_balls'],
                    'blue_balls': item['blue_balls'],
                    'display_code': self._format_display_code(
                        item['red_balls'],
                        item['blue_balls']
                    )
                })
            
            # 返回成功结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'data': formatted_data,
                'total': len(all_data),
                'returned': len(formatted_data)
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, '服务器内部错误', str(e))
    
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