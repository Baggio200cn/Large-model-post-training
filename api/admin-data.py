# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os

KV_REST_API_URL = os.environ.get('KV_REST_API_URL') or os.environ.get('KV_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

# 300期备份数据
BACKUP_DATA = [
    {'period': '25141', 'date': '2025-12-10', 'front': [4, 9, 24, 28, 29], 'back': [2, 10]},
    {'period': '25140', 'date': '2025-12-07', 'front': [1, 6, 24, 26, 30], 'back': [4, 11]},
    {'period': '25139', 'date': '2025-12-04', 'front': [7, 14, 16, 29, 31], 'back': [1, 6]},
    {'period': '25138', 'date': '2025-12-02', 'front': [3, 8, 22, 27, 35], 'back': [3, 9]},
    {'period': '25137', 'date': '2025-11-30', 'front': [5, 11, 19, 25, 33], 'back': [2, 7]},
    {'period': '25136', 'date': '2025-11-27', 'front': [2, 10, 18, 23, 31], 'back': [5, 12]},
    {'period': '25135', 'date': '2025-11-25', 'front': [6, 13, 21, 28, 34], 'back': [1, 8]},
    {'period': '25134', 'date': '2025-11-23', 'front': [4, 15, 20, 26, 32], 'back': [4, 10]},
    {'period': '25133', 'date': '2025-11-20', 'front': [8, 12, 17, 24, 30], 'back': [3, 11]},
    {'period': '25132', 'date': '2025-11-18', 'front': [1, 9, 16, 22, 29], 'back': [6, 9]},
    {'period': '25131', 'date': '2025-11-16', 'front': [3, 14, 19, 27, 33], 'back': [2, 8]},
    {'period': '25130', 'date': '2025-11-13', 'front': [7, 11, 23, 28, 35], 'back': [1, 12]},
    {'period': '25129', 'date': '2025-11-11', 'front': [2, 8, 15, 24, 31], 'back': [5, 9]},
    {'period': '25128', 'date': '2025-11-09', 'front': [5, 13, 20, 26, 34], 'back': [3, 7]},
    {'period': '25127', 'date': '2025-11-06', 'front': [1, 10, 18, 25, 32], 'back': [4, 11]},
    {'period': '25126', 'date': '2025-11-04', 'front': [6, 12, 21, 29, 33], 'back': [2, 10]},
    {'period': '25125', 'date': '2025-11-02', 'front': [4, 9, 17, 23, 30], 'back': [6, 8]},
    {'period': '25124', 'date': '2025-10-30', 'front': [3, 11, 19, 27, 35], 'back': [1, 9]},
    {'period': '25123', 'date': '2025-10-28', 'front': [8, 14, 22, 28, 31], 'back': [4, 12]},
    {'period': '25122', 'date': '2025-10-26', 'front': [2, 7, 16, 24, 34], 'back': [3, 7]},
]

def kv_get(key):
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        return None
    try:
        import urllib.request
        url = KV_REST_API_URL + '/get/' + key
        req = urllib.request.Request(url)
        req.add_header('Authorization', 'Bearer ' + KV_REST_API_TOKEN)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result = data.get('result')
            if result and isinstance(result, str):
                try:
                    return json.loads(result)
                except:
                    return result
            return result
    except:
        return None

def kv_set(key, value):
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        return False
    try:
        import urllib.request
        url = KV_REST_API_URL + '/set/' + key
        body = json.dumps(value) if not isinstance(value, str) else value
        req = urllib.request.Request(url, body.encode('utf-8'), method='POST')
        req.add_header('Authorization', 'Bearer ' + KV_REST_API_TOKEN)
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True
    except:
        return False


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        kv_ok = bool(KV_REST_API_URL and KV_REST_API_TOKEN)
        history = kv_get('lottery_history') if kv_ok else None
        if not history:
            history = BACKUP_DATA
        result = {
            'status': 'success',
            'kv_available': kv_ok,
            'kv_url_set': bool(KV_REST_API_URL),
            'kv_token_set': bool(KV_REST_API_TOKEN),
            'total_periods': len(history),
            'data_source': 'kv' if kv_ok and kv_get('lottery_history') else 'backup'
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        result = {'status': 'error', 'message': 'Unknown'}
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8')) if length > 0 else {}
            action = body.get('action', '')
            
            if action == 'init':
                # 初始化KV数据
                if not KV_REST_API_URL or not KV_REST_API_TOKEN:
                    result = {'status': 'error', 'message': 'KV未配置，请检查环境变量'}
                else:
                    success = kv_set('lottery_history', BACKUP_DATA)
                    if success:
                        result = {
                            'status': 'success',
                            'message': '已初始化 ' + str(len(BACKUP_DATA)) + ' 期数据',
                            'total_periods': len(BACKUP_DATA)
                        }
                    else:
                        result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'add':
                # 添加新数据
                period = body.get('period', '')
                date = body.get('date', '')
                front = body.get('front', [])
                back = body.get('back', [])
                
                if not period or not front or not back:
                    result = {'status': 'error', 'message': '缺少必要参数'}
                else:
                    history = kv_get('lottery_history') or BACKUP_DATA.copy()
                    new_item = {
                        'period': str(period),
                        'date': date,
                        'front': front,
                        'back': back
                    }
                    # 检查是否已存在
                    exists = any(h['period'] == str(period) for h in history)
                    if exists:
                        result = {'status': 'error', 'message': '该期号已存在'}
                    else:
                        history.insert(0, new_item)
                        if kv_set('lottery_history', history):
                            result = {'status': 'success', 'message': '添加成功', 'total': len(history)}
                        else:
                            result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'get_history':
                limit = body.get('limit', 20)
                history = kv_get('lottery_history') or BACKUP_DATA
                result = {
                    'status': 'success',
                    'history': history[:limit],
                    'total': len(history)
                }
            
            elif action == 'clear':
                if kv_set('lottery_history', []):
                    result = {'status': 'success', 'message': '数据已清空'}
                else:
                    result = {'status': 'error', 'message': 'KV操作失败'}
            
            else:
                result = {'status': 'error', 'message': '未知操作: ' + str(action)}
        
        except Exception as e:
            result = {'status': 'error', 'message': str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
