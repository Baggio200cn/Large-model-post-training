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
        """处理带文本或图片输入的灵修预测"""
        try:
            import base64
            import time

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            text = params.get('text', '')
            image_data = params.get('image', '')

            image_analyzed = False
            seed = None

            # 优先使用图片生成种子
            if image_data:
                try:
                    # 移除data:image/...;base64,前缀
                    if ',' in image_data:
                        image_data = image_data.split(',', 1)[1]

                    # 解码图片数据
                    img_bytes = base64.b64decode(image_data)

                    # 使用图片数据的哈希作为种子
                    img_hash = hashlib.md5(img_bytes).hexdigest()
                    seed = int(img_hash[:8], 16)
                    image_analyzed = True
                except Exception as img_error:
                    # 图片处理失败，回退到文本或时间
                    pass

            # 如果没有图片或图片处理失败，使用文本生成种子
            if seed is None:
                if text:
                    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
                else:
                    seed = int(time.time())

            random.seed(seed)

            # 生成灵修预测号码
            front_zone = sorted(random.sample(range(1, 36), 5))
            back_zone = sorted(random.sample(range(1, 13), 2))

            # 根据输入类型和内容生成能量强度
            if image_analyzed:
                # 图片能量：基于哈希值生成更高的能量强度
                intensity = round(0.65 + (seed % 25) / 100, 2)
            elif text:
                # 文本能量：基于文本长度和内容
                intensity = round(0.6 + (len(text) % 30) / 100, 2)
            else:
                # 默认能量
                intensity = round(0.6 + random.random() * 0.2, 2)

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
                    'text_analyzed': bool(text),
                    'image_analyzed': image_analyzed
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
