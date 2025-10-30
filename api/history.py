"""
历史数据API - 完整生产版
功能: 优先读取真实数据，失败时提供模拟数据
版本: 2.0
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
            
            # 获取limit参数，默认10期
            limit = int(query_params.get('limit', ['10'])[0])
            limit = min(max(limit, 1), 50)  # 限制在1-50之间
            
            # 尝试读取真实数据
            history_data = self._load_real_data()
            
            # 如果读取失败，使用模拟数据
            if not history_data:
                history_data = self._generate_mock_data(limit)
                data_source = 'mock'
            else:
                data_source = 'file'
            
            # 取最近N期
            recent_data = history_data[:limit] if history_data else []
            
            # 返回成功结果
            self._send_success_response({
                'history': recent_data,
                'total': len(history_data) if history_data else 0,
                'returned': len(recent_data),
                'data_source': data_source
            })
            
        except Exception as e:
            # 发生任何错误时，返回模拟数据而不是崩溃
            mock_data = self._generate_mock_data(10)
            self._send_success_response({
                'history': mock_data,
                'total': len(mock_data),
                'returned': len(mock_data),
                'data_source': 'mock',
                'note': f'使用模拟数据（错误: {str(e)}）'
            })
    
    def _load_real_data(self):
        """尝试加载真实数据"""
        try:
            # 尝试多个可能的文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'history.json'),
                '/var/task/data/raw/history.json',
                os.path.join(current_dir, 'history.json'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        all_data = json.load(f)
                    
                    # 如果数据是字典格式（包含metadata），提取data字段
                    if isinstance(all_data, dict):
                        return all_data.get('data', [])
                    else:
                        return all_data
            
            return None
            
        except Exception as e:
            print(f"Error loading real data: {e}")
            return None
    
    def _generate_mock_data(self, count):
        """生成模拟数据"""
        mock_data = []
        base_date = datetime.now()
        
        for i in range(count):
            date = base_date - timedelta(days=i*3)
            period = f"25{100-i:03d}"
            
            mock_data.append({
                'period': period,
                'date': date.strftime('%Y-%m-%d'),
                'red_balls': [2, 7, 15, 23, 35],
                'blue_balls': [3, 8]
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
