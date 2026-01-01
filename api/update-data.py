from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.request
import re

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """POST请求 - 处理数据更新"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            action = request_data.get('action', 'add')
            
            if action == 'add':
                result = self._add_lottery_data(request_data)
            elif action == 'auto_fetch':
                result = self._auto_fetch_latest()
            elif action == 'delete':
                result = self._delete_lottery_data(request_data)
            else:
                result = {'status': 'error', 'message': f'未知操作: {action}'}
            
            self._send_response(result)
            
        except Exception as e:
            self._send_response({'status': 'error', 'message': str(e)})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _add_lottery_data(self, data):
        """添加新的开奖数据"""
        period = data.get('period')
        date = data.get('date')
        front_zone = data.get('front_zone', [])
        back_zone = data.get('back_zone', [])
        
        # 验证数据
        if not period:
            return {'status': 'error', 'message': '期号不能为空'}
        
        if not date:
            return {'status': 'error', 'message': '日期不能为空'}
        
        if len(front_zone) != 5:
            return {'status': 'error', 'message': '前区必须有5个号码'}
        
        if len(back_zone) != 2:
            return {'status': 'error', 'message': '后区必须有2个号码'}
        
        # 验证号码范围
        for num in front_zone:
            if not (1 <= num <= 35):
                return {'status': 'error', 'message': f'前区号码 {num} 超出范围(1-35)'}
        
        for num in back_zone:
            if not (1 <= num <= 12):
                return {'status': 'error', 'message': f'后区号码 {num} 超出范围(1-12)'}
        
        # 检查重复
        if len(set(front_zone)) != 5:
            return {'status': 'error', 'message': '前区号码有重复'}
        
        if len(set(back_zone)) != 2:
            return {'status': 'error', 'message': '后区号码有重复'}
        
        # 构建数据记录
        new_record = {
            'period': period,
            'date': date,
            'numbers': sorted(front_zone) + sorted(back_zone)
        }
        
        # 注意：在Vercel无服务器环境中，我们无法直接修改文件
        # 这里返回成功信息和需要更新的数据格式
        # 实际更新需要通过GitHub API或手动更新
        
        return {
            'status': 'success',
            'message': '数据验证通过！请按以下格式更新 latest-results.py 中的 LOTTERY_DATA 数组',
            'record': new_record,
            'code_snippet': f'''
# 将以下代码添加到 LOTTERY_DATA 数组的开头:
{{"period": "{period}", "date": "{date}", "numbers": {sorted(front_zone) + sorted(back_zone)}}},
''',
            'instructions': [
                '1. 打开 GitHub 仓库中的 api/latest-results.py',
                '2. 找到 LOTTERY_DATA 数组',
                '3. 在数组开头添加上面的代码',
                '4. 提交更改，Vercel 将自动部署',
                '5. 同时更新 api/data-analysis.py 中的数据'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _auto_fetch_latest(self):
        """自动抓取最新开奖数据"""
        try:
            # 尝试从多个数据源抓取
            sources = [
                self._fetch_from_source1,
                self._fetch_from_source2
            ]
            
            for fetch_func in sources:
                try:
                    result = fetch_func()
                    if result:
                        return {
                            'status': 'success',
                            'message': '成功获取最新开奖数据',
                            'data': result,
                            'instructions': [
                                '请手动将数据更新到 api/latest-results.py',
                                '或者配置 GitHub Actions 自动更新'
                            ],
                            'timestamp': datetime.now().isoformat()
                        }
                except Exception as e:
                    continue
            
            return {
                'status': 'error',
                'message': '无法从任何数据源获取数据，请检查网络或数据源状态',
                'suggestion': '建议使用 GitHub Actions 定时任务自动抓取',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'自动抓取失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _fetch_from_source1(self):
        """从数据源1抓取（示例）"""
        # 由于网络限制，这里返回示例数据
        # 实际使用时需要配置允许的域名
        return None
    
    def _fetch_from_source2(self):
        """从数据源2抓取（示例）"""
        return None
    
    def _delete_lottery_data(self, data):
        """删除开奖数据"""
        period = data.get('period')
        
        if not period:
            return {'status': 'error', 'message': '请指定要删除的期号'}
        
        return {
            'status': 'success',
            'message': f'请手动从 latest-results.py 中删除期号 {period} 的数据',
            'instructions': [
                '1. 打开 GitHub 仓库中的 api/latest-results.py',
                '2. 找到 LOTTERY_DATA 数组',
                f'3. 删除 period 为 {period} 的记录',
                '4. 提交更改',
                '5. 同时更新 api/data-analysis.py'
            ],
            'timestamp': datetime.now().isoformat()
        }
