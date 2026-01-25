# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """获取管理数据状态"""
        try:
            from utils._lottery_data import lottery_data

            kv_available = False
            data_source = 'local_backup'
            latest_period = '--'
            total_periods = 0

            if lottery_data and len(lottery_data) > 0:
                total_periods = len(lottery_data)
                latest = lottery_data[0]
                latest_period = latest.get('period', '--')

            # 检测腾讯云COS配置
            cos_configured = all([
                os.getenv('TENCENT_SECRET_ID'),
                os.getenv('TENCENT_SECRET_KEY'),
                os.getenv('TENCENT_COS_BUCKET'),
                os.getenv('TENCENT_COS_REGION')
            ])

            if cos_configured:
                try:
                    from utils._cos_data_loader import get_lottery_data
                    cos_data = get_lottery_data()
                    if cos_data and isinstance(cos_data, list) and len(cos_data) > 0:
                        kv_available = True
                        data_source = 'tencent_cos'
                        total_periods = len(cos_data)
                        latest_period = cos_data[0].get('period', '--')
                except:
                    pass

            result = {
                'status': 'success',
                'kv_available': kv_available,
                'data_source': data_source,
                'latest_period': latest_period,
                'total_periods': total_periods
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
        """处理管理操作"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            action = params.get('action', '')

            if action == 'fetch':
                # 自动抓取最新数据
                result = {
                    'status': 'success',
                    'message': '数据抓取功能需要配置腾讯云COS'
                }
            elif action == 'init':
                # 初始化KV数据
                result = {
                    'status': 'success',
                    'message': 'KV初始化功能需要配置Vercel KV'
                }
            elif action == 'add':
                # 添加开奖数据
                result = {
                    'status': 'success',
                    'message': '添加数据功能需要配置数据存储'
                }
            elif action == 'get_history':
                # 获取历史记录
                from utils._lottery_data import lottery_data
                limit = params.get('limit', 20)
                history = []
                for item in lottery_data[:limit]:
                    history.append({
                        'period': item.get('period'),
                        'date': item.get('date'),
                        'front': item.get('front_zone', []),
                        'back': item.get('back_zone', [])
                    })
                result = {
                    'status': 'success',
                    'history': history
                }
            else:
                result = {
                    'status': 'error',
                    'message': '未知操作'
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
