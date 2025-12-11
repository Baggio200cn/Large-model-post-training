from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import urllib.request
import urllib.error

# ============ Upstash Redis 配置 ============
# 支持多种环境变量名称
KV_REST_API_URL = os.environ.get('KV_REST_API_URL') or os.environ.get('STORAGE_URL') or os.environ.get('UPSTASH_REDIS_REST_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN') or os.environ.get('STORAGE_TOKEN') or os.environ.get('UPSTASH_REDIS_REST_TOKEN', '')

# ============ 默认备份数据 ============
DEFAULT_BACKUP_DATA = [
    {"period": "25141", "date": "2025-12-10", "front": [4, 9, 24, 28, 29], "back": [2, 10]},
    {"period": "25140", "date": "2025-12-08", "front": [4, 5, 13, 18, 34], "back": [2, 8]},
    {"period": "25139", "date": "2025-12-06", "front": [8, 18, 22, 30, 35], "back": [1, 4]},
    {"period": "25138", "date": "2025-12-03", "front": [1, 3, 19, 21, 23], "back": [7, 11]},
    {"period": "25137", "date": "2025-12-01", "front": [7, 8, 9, 11, 22], "back": [5, 11]},
    {"period": "25136", "date": "2025-11-29", "front": [7, 11, 15, 16, 23], "back": [9, 11]},
    {"period": "25135", "date": "2025-11-26", "front": [2, 10, 16, 28, 32], "back": [1, 7]},
    {"period": "25134", "date": "2025-11-24", "front": [7, 12, 18, 27, 33], "back": [2, 11]},
    {"period": "25133", "date": "2025-11-22", "front": [3, 14, 22, 29, 35], "back": [4, 9]},
    {"period": "25132", "date": "2025-11-19", "front": [5, 11, 17, 25, 31], "back": [3, 8]},
]

def kv_get(key):
    """从 Vercel KV 获取数据"""
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        return None
    try:
        url = f"{KV_REST_API_URL}/get/{key}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {KV_REST_API_TOKEN}')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('result'):
                return json.loads(data['result'])
    except Exception as e:
        print(f"KV GET error: {e}")
    return None

def kv_set(key, value):
    """保存数据到 Vercel KV"""
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        return False
    try:
        url = f"{KV_REST_API_URL}/set/{key}"
        data = json.dumps(value).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Authorization', f'Bearer {KV_REST_API_TOKEN}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception as e:
        print(f"KV SET error: {e}")
    return False

def get_lottery_data():
    """获取彩票数据：优先从KV，否则用默认数据"""
    # 尝试从 KV 获取
    kv_data = kv_get('lottery_data')
    if kv_data and isinstance(kv_data, list) and len(kv_data) > 0:
        return kv_data, "kv_storage"
    
    # 使用默认备份数据
    return DEFAULT_BACKUP_DATA, "default_backup"

def save_lottery_data(data):
    """保存彩票数据到 KV"""
    return kv_set('lottery_data', data)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 获取数据
            lottery_data, data_source = get_lottery_data()
            
            if not lottery_data:
                raise Exception("无可用数据")
            
            # 获取最新一期
            latest = lottery_data[0]
            
            # 构建返回结果
            result = {
                'period': latest['period'],
                'draw_date': latest['date'],
                'date': latest['date'],
                'front_zone': latest['front'],
                'back_zone': latest['back'],
                'numbers': latest['front'] + latest['back'],
                'display': f"{' '.join([f'{n:02d}' for n in latest['front']])} + {' '.join([f'{n:02d}' for n in latest['back']])}"
            }
            
            # 最近开奖记录
            recent_results = []
            for item in lottery_data[:10]:
                recent_results.append({
                    'period': item['period'],
                    'date': item['date'],
                    'front_zone': item['front'],
                    'back_zone': item['back'],
                    'numbers': item['front'] + item['back'],
                    'display': f"{' '.join([f'{n:02d}' for n in item['front']])} + {' '.join([f'{n:02d}' for n in item['back']])}"
                })
            
            # 计算数据范围
            first_period = lottery_data[-1]['period'] if lottery_data else 'N/A'
            last_period = lottery_data[0]['period'] if lottery_data else 'N/A'
            
            # KV 是否可用
            kv_available = bool(KV_REST_API_URL and KV_REST_API_TOKEN)
            
            response = {
                'status': 'success',
                'latest_result': result,
                'recent_results': recent_results,
                'total_periods': len(lottery_data),
                'data_range': f"第{first_period}期 - 第{last_period}期",
                'data_source': data_source,
                'is_realtime': data_source == "kv_storage",
                'kv_available': kv_available,
                'timestamp': datetime.now().isoformat(),
                'message': f'数据来源：{"Vercel KV 存储" if data_source == "kv_storage" else "默认备份数据"}'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理数据更新请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            action = request_data.get('action', '')
            
            if action == 'add':
                # 添加新数据
                new_entry = request_data.get('entry', {})
                if not new_entry.get('period') or not new_entry.get('front') or not new_entry.get('back'):
                    raise Exception("缺少必要字段: period, front, back")
                
                # 获取现有数据
                lottery_data, _ = get_lottery_data()
                
                # 检查是否已存在
                existing_periods = [item['period'] for item in lottery_data]
                if new_entry['period'] in existing_periods:
                    raise Exception(f"期号 {new_entry['period']} 已存在")
                
                # 添加到开头
                lottery_data.insert(0, new_entry)
                
                # 只保留最近50期
                lottery_data = lottery_data[:50]
                
                # 保存到 KV
                if save_lottery_data(lottery_data):
                    response = {
                        'status': 'success',
                        'message': f"成功添加第 {new_entry['period']} 期数据",
                        'total_periods': len(lottery_data)
                    }
                else:
                    raise Exception("保存到 KV 失败，请检查 KV 配置")
            
            elif action == 'delete':
                # 删除数据
                period = request_data.get('period', '')
                if not period:
                    raise Exception("缺少期号")
                
                lottery_data, _ = get_lottery_data()
                original_count = len(lottery_data)
                lottery_data = [item for item in lottery_data if item['period'] != period]
                
                if len(lottery_data) == original_count:
                    raise Exception(f"未找到期号 {period}")
                
                if save_lottery_data(lottery_data):
                    response = {
                        'status': 'success',
                        'message': f"成功删除第 {period} 期数据",
                        'total_periods': len(lottery_data)
                    }
                else:
                    raise Exception("保存到 KV 失败")
            
            elif action == 'init':
                # 初始化 KV 数据（用默认数据填充）
                if save_lottery_data(DEFAULT_BACKUP_DATA):
                    response = {
                        'status': 'success',
                        'message': f"成功初始化 {len(DEFAULT_BACKUP_DATA)} 期数据到 KV",
                        'total_periods': len(DEFAULT_BACKUP_DATA)
                    }
                else:
                    raise Exception("初始化 KV 失败，请检查 KV 配置")
            
            else:
                raise Exception(f"未知操作: {action}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
