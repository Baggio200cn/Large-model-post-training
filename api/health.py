# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """健康检查端点 - 检查 COS 数据源"""

        # 检测腾讯云COS配置
        cos_configured = all([
            os.getenv('TENCENT_SECRET_ID'),
            os.getenv('TENCENT_SECRET_KEY'),
            os.getenv('TENCENT_COS_BUCKET'),
            os.getenv('TENCENT_COS_REGION')
        ])

        # 尝试导入 COS 数据加载器
        cos_available = False
        total_periods = 0
        data_source = 'none'
        error_message = None

        if cos_configured:
            try:
                from utils._cos_data_loader import get_lottery_data, get_cache_status
                data = get_lottery_data()
                if data and isinstance(data, list):
                    cos_available = True
                    total_periods = len(data)
                    data_source = 'tencent_cos'
            except Exception as e:
                error_message = str(e)

        if not cos_available:
            # 使用本地备份数据
            try:
                from utils._lottery_data import lottery_data
                total_periods = len(lottery_data)
                data_source = 'local_backup'
            except:
                total_periods = 0
                data_source = 'none'

        result = {
            'status': 'healthy',
            'version': '3.0.0',
            'cos_available': cos_available,
            'cos_configured': cos_configured,
            'total_periods': total_periods,
            'data_source': data_source,
            'endpoints': [
                '/api/health',
                '/api/test-cos',
                '/api/latest-results',
                '/api/admin-data',
                '/api/predict'
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
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
