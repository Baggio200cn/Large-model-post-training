# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import random
import hashlib
import os
import sys

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """获取灵修预测"""
        try:
            # 生成基于时间的随机种子
            import time
            seed = int(time.time())
            random.seed(seed)

            # 生成灵修预测号码
            front_zone = sorted(random.sample(range(1, 36), 5))
            back_zone = sorted(random.sample(range(1, 13), 2))

            # 生成能量分析
            intensity = round(random.uniform(0.6, 0.9), 2)

            result = {
                'status': 'success',
                'spiritual_prediction': {
                    'front_zone': front_zone,
                    'back_zone': back_zone
                },
                'energy_analysis': {
                    'intensity': intensity,
                    'energy_level': '中' if intensity < 0.75 else '高',
                    'cosmic_alignment': '良好'
                },
                'message': '灵修感应完成'
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_result = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        """处理带文本输入的灵修预测"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            text = params.get('text', '')

            # 使用文本生成哈希种子
            if text:
                seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            else:
                import time
                seed = int(time.time())

            random.seed(seed)

            # 生成灵修预测号码
            front_zone = sorted(random.sample(range(1, 36), 5))
            back_zone = sorted(random.sample(range(1, 13), 2))

            # 根据文本长度和内容生成能量强度
            intensity = round(0.6 + (len(text) % 30) / 100, 2)
            if intensity > 0.9:
                intensity = 0.9

            result = {
                'status': 'success',
                'spiritual_prediction': {
                    'front_zone': front_zone,
                    'back_zone': back_zone
                },
                'energy_analysis': {
                    'intensity': intensity,
                    'energy_level': '中' if intensity < 0.75 else '高',
                    'cosmic_alignment': '良好',
                    'text_analyzed': bool(text)
                },
                'message': '灵修感应完成'
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_result = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
