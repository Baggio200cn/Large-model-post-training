"""
最简环境变量检查 - 不依赖任何外部库
"""
from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """检查环境变量是否设置"""

        # 检查所有环境变量
        env_check = {
            'TENCENT_SECRET_ID': os.getenv('TENCENT_SECRET_ID'),
            'TENCENT_SECRET_KEY': os.getenv('TENCENT_SECRET_KEY'),
            'TENCENT_COS_BUCKET': os.getenv('TENCENT_COS_BUCKET'),
            'TENCENT_COS_REGION': os.getenv('TENCENT_COS_REGION')
        }

        # 构建响应
        response = {
            'message': '环境变量检查',
            'environment': {}
        }

        for key, value in env_check.items():
            if value:
                # 只显示前4个字符
                response['environment'][key] = {
                    'set': True,
                    'preview': value[:4] + '...',
                    'length': len(value)
                }
            else:
                response['environment'][key] = {
                    'set': False,
                    'value': None
                }

        # 检查是否所有变量都设置了
        all_set = all(v for v in env_check.values())
        response['all_configured'] = all_set

        if all_set:
            response['status'] = 'OK - 所有环境变量已设置'
        else:
            missing = [k for k, v in env_check.items() if not v]
            response['status'] = f'ERROR - 缺少环境变量: {", ".join(missing)}'

        # 发送响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
