# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import re

KV_REST_API_URL = os.environ.get('KV_REST_API_URL') or os.environ.get('KV_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

# 备份数据
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

def fetch_latest_from_web():
    """从500彩票网抓取最新开奖数据"""
    try:
        import urllib.request
        url = 'https://datachart.500.com/dlt/history/history.shtml'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('gb2312', errors='ignore')
            # 解析数据
            pattern = r'<tr[^>]*>\s*<td[^>]*>(\d{5})</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>'
            matches = re.findall(pattern, html)
            results = []
            for m in matches[:50]:  # 最多取50期
                period = m[0]
                front = sorted([int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5])])
                back = sorted([int(m[6]), int(m[7])])
                results.append({
                    'period': period,
                    'date': '',
                    'front': front,
                    'back': back
                })
            return results
    except Exception as e:
        return None

def fetch_from_lottery_gov():
    """从体彩官网API抓取"""
    try:
        import urllib.request
        url = 'https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize=30&is498=1&pageNo=1'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('value', {}).get('list', [])
            results = []
            for item in items:
                period = item.get('lotteryDrawNum', '')
                date = item.get('lotteryDrawTime', '')[:10] if item.get('lotteryDrawTime') else ''
                nums = item.get('lotteryDrawResult', '').split()
                if len(nums) >= 7:
                    front = sorted([int(n) for n in nums[:5]])
                    back = sorted([int(n) for n in nums[5:7]])
                    results.append({
                        'period': period,
                        'date': date,
                        'front': front,
                        'back': back
                    })
            return results
    except:
        return None


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        kv_ok = bool(KV_REST_API_URL and KV_REST_API_TOKEN)
        history = kv_get('lottery_history') if kv_ok else None
        if not history:
            history = BACKUP_DATA
        result = {
            'status': 'success',
            'kv_available': kv_ok,
            'total_periods': len(history),
            'latest_period': history[0]['period'] if history else '--',
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
                    result = {'status': 'error', 'message': 'KV未配置'}
                else:
                    success = kv_set('lottery_history', BACKUP_DATA)
                    if success:
                        result = {'status': 'success', 'message': '已初始化 ' + str(len(BACKUP_DATA)) + ' 期数据'}
                    else:
                        result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'add':
                # 手动添加数据
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
                            result = {'status': 'success', 'message': '添加成功', 'total': len(history)}
                        else:
                            result = {'status': 'error', 'message': 'KV写入失败'}
            
            elif action == 'fetch':
                # 自动抓取最新数据
                fetched = fetch_from_lottery_gov()
                if not fetched:
                    fetched = fetch_latest_from_web()
                
                if not fetched:
                    result = {'status': 'error', 'message': '抓取失败，请稍后重试'}
                else:
                    history = kv_get('lottery_history') or []
                    existing_periods = set(h['period'] for h in history)
                    new_count = 0
                    for item in fetched:
                        if item['period'] not in existing_periods:
                            history.append(item)
                            new_count += 1
                    history.sort(key=lambda x: int(x['period']), reverse=True)
                    if kv_set('lottery_history', history):
                        result = {
                            'status': 'success',
                            'message': '抓取完成，新增 ' + str(new_count) + ' 期数据',
                            'new_count': new_count,
                            'total': len(history)
                        }
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
