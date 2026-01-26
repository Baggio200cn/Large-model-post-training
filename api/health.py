# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """健康检查端点 - 检查系统状态和数据源"""

        # 检测 Vercel KV 配置
        kv_available = bool(os.getenv('KV_REST_API_URL') and os.getenv('KV_REST_API_TOKEN'))

        # 尝试加载数据
        total_periods = 0
        data_source = 'none'
        error_message = None

        try:
            # 尝试导入本地数据
            from utils._lottery_data import lottery_data
            total_periods = len(lottery_data)
            data_source = 'local_backup'
        except Exception as e:
            error_message = str(e)
            total_periods = 0
            data_source = 'none'

        result = {
            'status': 'healthy',
            'version': '3.1.0',
            'kv_available': kv_available,
            'total_periods': total_periods,
            'data_source': data_source,
            'endpoints': [
                '/api/health',
                '/api/latest-results',
                '/api/predict',
                '/api/data-analysis',
                '/api/spiritual',
                '/api/fusion-weights',
                '/api/generate-tweet',
                '/api/admin-data',
                '/api/ai-knowledge'
            ]
        }

        if error_message:
            result['error'] = error_message

        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
