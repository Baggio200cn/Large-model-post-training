<<<<<<< HEAD
﻿from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    response = {
        'status': 'healthy',
        'service': '大乐透预测系统',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }
    return response
=======
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os

KV_REST_API_URL = os.environ.get('KV_REST_API_URL') or os.environ.get('KV_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

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


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # 检测KV配置
        kv_configured = bool(KV_REST_API_URL and KV_REST_API_TOKEN)
        
        # 尝试获取数据来验证KV是否真正可用
        kv_working = False
        total_periods = 0
        data_source = 'none'
        
        if kv_configured:
            try:
                history = kv_get('lottery_history')
                if history and isinstance(history, list):
                    kv_working = True
                    total_periods = len(history)
                    data_source = 'kv_storage'
            except:
                pass
        
        if not kv_working:
            # 使用备份数据
            total_periods = 10
            data_source = 'backup'
        
        result = {
            'status': 'healthy',
            'version': '2.1.0',
            'kv_available': kv_working,
            'kv_configured': kv_configured,
            'total_periods': total_periods,
            'data_source': data_source,
            'endpoints': [
                '/api/health',
                '/api/latest-results',
                '/api/admin-data',
                '/api/generate-tweet',
                '/api/spiritual'
            ]
        }
        
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
>>>>>>> 75fe0abe06fc410ae65f8e03c73d15ef57737fbd
