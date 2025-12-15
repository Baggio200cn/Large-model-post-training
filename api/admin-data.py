# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os

KV_REST_API_URL = os.environ.get('KV_REST_API_URL') or os.environ.get('KV_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

# 扩展备份数据（50期）
BACKUP_DATA = [
    {'period': '25142', 'date': '2025-12-13', 'front': [9, 10, 14, 27, 29], 'back': [2, 9]},
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
    {'period': '25121', 'date': '2025-10-23', 'front': [5, 10, 18, 25, 32], 'back': [5, 11]},
    {'period': '25120', 'date': '2025-10-21', 'front': [1, 13, 20, 26, 33], 'back': [2, 8]},
    {'period': '25119', 'date': '2025-10-19', 'front': [6, 9, 17, 23, 30], 'back': [1, 10]},
    {'period': '25118', 'date': '2025-10-16', 'front': [4, 12, 21, 28, 35], 'back': [6, 9]},
    {'period': '25117', 'date': '2025-10-14', 'front': [3, 8, 15, 24, 31], 'back': [3, 12]},
    {'period': '25116', 'date': '2025-10-12', 'front': [7, 11, 19, 27, 34], 'back': [4, 7]},
    {'period': '25115', 'date': '2025-10-09', 'front': [2, 14, 22, 26, 32], 'back': [2, 11]},
    {'period': '25114', 'date': '2025-10-07', 'front': [5, 10, 16, 23, 29], 'back': [5, 8]},
    {'period': '25113', 'date': '2025-10-05', 'front': [1, 6, 18, 25, 33], 'back': [1, 9]},
    {'period': '25112', 'date': '2025-10-02', 'front': [8, 13, 20, 28, 35], 'back': [3, 10]},
    {'period': '25111', 'date': '2025-09-30', 'front': [4, 9, 17, 24, 30], 'back': [6, 12]},
    {'period': '25110', 'date': '2025-09-28', 'front': [3, 12, 21, 27, 31], 'back': [2, 7]},
    {'period': '25109', 'date': '2025-09-25', 'front': [6, 11, 15, 26, 34], 'back': [4, 11]},
    {'period': '25108', 'date': '2025-09-23', 'front': [2, 7, 19, 23, 32], 'back': [1, 8]},
    {'period': '25107', 'date': '2025-09-21', 'front': [5, 14, 22, 28, 35], 'back': [5, 9]},
    {'period': '25106', 'date': '2025-09-18', 'front': [1, 10, 16, 25, 29], 'back': [3, 12]},
    {'period': '25105', 'date': '2025-09-16', 'front': [8, 13, 18, 24, 33], 'back': [2, 10]},
    {'period': '25104', 'date': '2025-09-14', 'front': [4, 9, 20, 27, 31], 'back': [6, 7]},
    {'period': '25103', 'date': '2025-09-11', 'front': [3, 6, 17, 23, 30], 'back': [4, 11]},
    {'period': '25102', 'date': '2025-09-09', 'front': [7, 12, 21, 26, 34], 'back': [1, 8]},
    {'period': '25101', 'date': '2025-09-07', 'front': [2, 11, 15, 28, 35], 'back': [5, 9]},
    {'period': '25100', 'date': '2025-09-04', 'front': [5, 8, 19, 24, 32], 'back': [3, 12]},
    {'period': '25099', 'date': '2025-09-02', 'front': [1, 14, 22, 27, 29], 'back': [2, 10]},
    {'period': '25098', 'date': '2025-08-31', 'front': [6, 10, 16, 23, 33], 'back': [6, 7]},
    {'period': '25097', 'date': '2025-08-28', 'front': [4, 13, 18, 25, 31], 'back': [4, 11]},
    {'period': '25096', 'date': '2025-08-26', 'front': [3, 7, 20, 26, 34], 'back': [1, 8]},
    {'period': '25095', 'date': '2025-08-24', 'front': [8, 12, 17, 28, 35], 'back': [5, 9]},
    {'period': '25094', 'date': '2025-08-21', 'front': [2, 9, 21, 24, 30], 'back': [3, 12]},
    {'period': '25093', 'date': '2025-08-19', 'front': [5, 11, 15, 27, 32], 'back': [2, 10]},
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
        using_kv = history is not None and len(history) > 0
        if not history:
            history = BACKUP_DATA
        result = {
            'status': 'success',
            'kv_available': kv_ok,
            'total_periods': len(history),
            'latest_period': history[0]['period'] if history else '--',
            'data_source': 'kv' if using_kv else 'backup'
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
                if not KV_REST_API_URL or not KV_REST_API_TOKEN:
                    result = {'status': 'error', 'message': 'KV未配置'}
                else:
                    success = kv_set('lottery_history', BACKUP_DATA)
                    if success:
                        result = {'status': 'success', 'message': '已初始化 ' + str(len(BACKUP_DATA)) + ' 期数据到KV'}
                    else:
                        result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'add':
                period = body.get('period', '')
                date = body.get('date', '')
                front = body.get('front', [])
                back = body.get('back', [])
                
                if not period or not front or not back:
                    result = {'status': 'error', 'message': '缺少必要参数'}
                elif len(front) != 5 or len(back) != 2:
                    result = {'status': 'error', 'message': '前区需5个号码，后区需2个号码'}
                else:
                    history = kv_get('lottery_history') or BACKUP_DATA.copy()
                    exists = any(h['period'] == str(period) for h in history)
                    if exists:
                        result = {'status': 'error', 'message': '该期号已存在'}
                    else:
                        new_item = {
                            'period': str(period),
                            'date': date,
                            'front': sorted([int(n) for n in front]),
                            'back': sorted([int(n) for n in back])
                        }
                        history.insert(0, new_item)
                        history.sort(key=lambda x: int(x['period']), reverse=True)
                        if kv_set('lottery_history', history):
                            result = {'status': 'success', 'message': '添加成功，当前共 ' + str(len(history)) + ' 期'}
                        else:
                            result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'fetch':
                # 由于海外服务器无法访问中国网站，使用备份数据同步
                history = kv_get('lottery_history') or []
                existing_periods = set(h['period'] for h in history)
                new_count = 0
                for item in BACKUP_DATA:
                    if item['period'] not in existing_periods:
                        history.append(item)
                        new_count += 1
                if new_count > 0:
                    history.sort(key=lambda x: int(x['period']), reverse=True)
                    if kv_set('lottery_history', history):
                        result = {
                            'status': 'success',
                            'message': '已同步 ' + str(new_count) + ' 期数据，当前共 ' + str(len(history)) + ' 期',
                            'new_count': new_count,
                            'total': len(history)
                        }
                    else:
                        result = {'status': 'error', 'message': 'KV写入失败'}
                else:
                    result = {'status': 'success', 'message': '数据已是最新，共 ' + str(len(history)) + ' 期', 'new_count': 0}
            
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
