"""
测试腾讯云COS数据加载
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        try:
            # 尝试加载COS数据加载器
            try:
                from _cos_data_loader import get_lottery_data, get_cache_status
                cos_available = True
            except Exception as e:
                cos_available = False
                cos_error = str(e)

            # 检查环境变量
            env_vars = {
                'TENCENT_SECRET_ID': os.getenv('TENCENT_SECRET_ID', None),
                'TENCENT_SECRET_KEY': os.getenv('TENCENT_SECRET_KEY', None),
                'TENCENT_COS_BUCKET': os.getenv('TENCENT_COS_BUCKET', None),
                'TENCENT_COS_REGION': os.getenv('TENCENT_COS_REGION', None)
            }

            env_status = {}
            for key, value in env_vars.items():
                if value:
                    # 只显示前4个字符，保护敏感信息
                    env_status[key] = f"{value[:4]}...（已设置）"
                else:
                    env_status[key] = "❌ 未设置"

            response = {
                'status': 'success',
                'message': '腾讯云COS连接测试',
                'cos_loader_available': cos_available,
                'environment_variables': env_status,
            }

            # 如果COS可用，尝试加载数据
            if cos_available:
                try:
                    data = get_lottery_data()
                    cache_status = get_cache_status()

                    response['data_test'] = {
                        'success': True,
                        'total_records': len(data),
                        'latest_period': data[0]['period'] if data else None,
                        'cache_status': cache_status
                    }
                except Exception as e:
                    response['data_test'] = {
                        'success': False,
                        'error': str(e)
                    }
            else:
                response['cos_error'] = cos_error

            # 返回JSON响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))

        except Exception as e:
            # 错误响应
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'status': 'error',
                'error': str(e)
            }

            self.wfile.write(json.dumps(error_response, ensure_ascii=False, indent=2).encode('utf-8'))
