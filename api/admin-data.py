# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入共享数据加载模块
from utils._data_loader import load_user_data, save_user_data, get_combined_lottery_data

# 导入数据同步和训练触发模块
try:
    from utils._data_sync import sync_new_data
    from utils._training_trigger import trigger_training, get_training_status
    SYNC_AVAILABLE = True
except Exception as e:
    print(f"⚠️  数据同步/训练模块导入失败: {str(e)}")
    SYNC_AVAILABLE = False


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
                            # 基本成功消息
                            success_msg = f'✅ 成功添加期号 {period} 的数据'

                            # 【关键修复】：立即获取合并数据并强制同步到COS
                            combined_data = get_combined_lottery_data()

                            # 自动同步到COS和触发训练
                            if SYNC_AVAILABLE:
                                try:
                                    print("\n" + "="*60)
                                    print("🚀 自动触发数据同步和模型训练")
                                    print("="*60)

                                    # 步骤1：同步数据到本地文件和COS（核心：持久化到云端）
                                    sync_result = sync_new_data([new_record], combined_data)

                                    # 显示同步结果
                                    success_msg += f"\n{sync_result.get('message', '数据同步完成')}"

                                    # 显示详细同步状态
                                    for detail in sync_result.get('details', []):
                                        success_msg += f"\n{detail}"

                                    # 步骤2：触发后台训练
                                    training_result = trigger_training(combined_data)

                                    if training_result.get('success'):
                                        success_msg += f"\n✅ 模型训练已启动（后台运行）"
                                        success_msg += f"\n   日志: {training_result.get('log_file')}"
                                    else:
                                        success_msg += f"\n⚠️  训练未启动: {training_result.get('message')}"

                                except Exception as e:
                                    import traceback
                                    success_msg += f"\n⚠️  自动化流程异常: {str(e)}"
                                    traceback.print_exc()
                            else:
                                # 如果同步模块不可用，至少尝试直接上传到COS
                                try:
                                    from utils._cos_data_loader import upload_to_cos
                                    if upload_to_cos(combined_data):
                                        success_msg += "\n✅ 数据已上传到腾讯云COS"
                                    else:
                                        success_msg += "\n⚠️  COS上传失败，数据仅保存在本地（可能在容器重启后丢失）"
                                except Exception as e:
                                    success_msg += f"\n⚠️  COS上传异常: {str(e)}"

                            result = {
                                'status': 'success',
                                'message': success_msg
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
            elif action == 'training_status':
                # 获取训练状态
                if SYNC_AVAILABLE:
                    training_status = get_training_status()
                    result = {
                        'status': 'success',
                        'training': training_status
                    }
                else:
                    result = {
                        'status': 'error',
                        'message': '训练模块不可用'
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
