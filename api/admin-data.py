# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 用户添加的数据存储路径
USER_DATA_FILE = '/tmp/user_lottery_data.json'


def load_user_data():
    """加载用户添加的数据"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_user_data(data):
    """保存用户添加的数据"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def get_combined_lottery_data():
    """获取合并后的彩票数据（用户数据 + 固定数据）"""
    from utils._lottery_data import lottery_data
    user_data = load_user_data()
    # 用户数据在前，固定数据在后
    return user_data + lottery_data


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """获取管理数据状态"""
        try:
            # 使用合并后的数据（用户数据 + 固定数据）
            combined_data = get_combined_lottery_data()

            kv_available = False
            data_source = 'local_backup'
            latest_period = '--'
            total_periods = 0

            if combined_data and len(combined_data) > 0:
                total_periods = len(combined_data)
                latest = combined_data[0]
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
                period = params.get('period', '').strip()
                date = params.get('date', '').strip()
                front = params.get('front', [])
                back = params.get('back', [])

                # 验证数据
                if not period:
                    result = {'status': 'error', 'message': '期号不能为空'}
                elif not isinstance(front, list) or len(front) != 5:
                    result = {'status': 'error', 'message': '前区需要5个号码'}
                elif not isinstance(back, list) or len(back) != 2:
                    result = {'status': 'error', 'message': '后区需要2个号码'}
                else:
                    # 检查期号是否已存在
                    combined_data = get_combined_lottery_data()
                    existing = any(item.get('period') == period for item in combined_data)

                    if existing:
                        result = {'status': 'error', 'message': f'期号 {period} 已存在'}
                    else:
                        # 加载用户数据
                        user_data = load_user_data()

                        # 创建新记录
                        new_record = {
                            'period': period,
                            'date': date if date else datetime.now().strftime('%Y-%m-%d'),
                            'front_zone': front,
                            'back_zone': back,
                            'user_added': True,
                            'added_at': datetime.now().isoformat()
                        }

                        # 添加到列表开头（最新的在前面）
                        user_data.insert(0, new_record)

                        # 保存
                        if save_user_data(user_data):
                            result = {
                                'status': 'success',
                                'message': f'成功添加期号 {period} 的数据'
                            }
                        else:
                            result = {
                                'status': 'error',
                                'message': '保存数据失败'
                            }
            elif action == 'get_history':
                # 获取历史记录（使用合并后的数据）
                combined_data = get_combined_lottery_data()
                limit = params.get('limit', 20)
                history = []
                for item in combined_data[:limit]:
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
