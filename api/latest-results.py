from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import re

# 尝试导入requests，如果失败则使用urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

# 备份静态数据（当实时抓取失败时使用）
# 最后更新: 2025-12-08 - 请在后台管理页面更新此数据
BACKUP_DATA = [
    {"period": "25139", "date": "2025-12-06", "front": [8, 18, 22, 30, 35], "back": [1, 4]},
    {"period": "25138", "date": "2025-12-03", "front": [1, 3, 19, 21, 23], "back": [7, 11]},
    {"period": "25137", "date": "2025-12-01", "front": [7, 8, 9, 11, 22], "back": [5, 11]},
    {"period": "25136", "date": "2025-11-29", "front": [7, 12, 18, 27, 33], "back": [2, 11]},
    {"period": "25135", "date": "2025-11-26", "front": [2, 10, 16, 28, 32], "back": [1, 7]},
]

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """GET请求 - 实时抓取最新开奖数据，失败时使用备份数据"""
        try:
            # 尝试从多个数据源抓取
            result = None
            error_msg = ""
            data_source = "realtime"
            
            # 数据源1: 500彩票网
            try:
                result = self._fetch_from_500()
                data_source = "500.com"
            except Exception as e:
                error_msg += f"500彩票网: {str(e)}; "
            
            # 数据源2: 彩宝网
            if not result:
                try:
                    result = self._fetch_from_caibao()
                    data_source = "caibao"
                except Exception as e:
                    error_msg += f"彩宝网: {str(e)}; "
            
            # 数据源3: 开彩网API
            if not result:
                try:
                    result = self._fetch_from_opencai()
                    data_source = "opencai"
                except Exception as e:
                    error_msg += f"开彩网: {str(e)}; "
            
            # 如果所有实时数据源都失败，使用备份数据
            if not result and BACKUP_DATA:
                latest = BACKUP_DATA[0]
                result = {
                    'period': latest['period'],
                    'draw_date': latest['date'],
                    'front_zone': latest['front'],
                    'back_zone': latest['back'],
                    'display': f"{' '.join([str(n).zfill(2) for n in latest['front']])} + {' '.join([str(n).zfill(2) for n in latest['back']])}"
                }
                data_source = "backup"
                error_msg = "实时抓取失败，使用备份数据。" + error_msg
            
            if result:
                # 构建最近开奖列表
                recent_results = []
                if data_source == "backup":
                    for item in BACKUP_DATA[:10]:
                        recent_results.append({
                            'period': item['period'],
                            'date': item['date'],
                            'front_zone': item['front'],
                            'back_zone': item['back']
                        })
                
                response = {
                    'status': 'success',
                    'latest_result': result,
                    'recent_results': recent_results if recent_results else [],
                    'data_source': data_source,
                    'is_realtime': data_source != "backup",
                    'fetch_time': datetime.now().isoformat(),
                    'message': error_msg if data_source == "backup" else "",
                    'timestamp': datetime.now().isoformat()
                }
            else:
                response = {
                    'status': 'error',
                    'message': f'数据获取失败: {error_msg}',
                    'timestamp': datetime.now().isoformat()
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error(str(e))
    
    def _fetch_url(self, url, timeout=10):
        """统一的URL请求方法"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
        if HAS_REQUESTS:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.encoding = 'utf-8'
            return response.text
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8')
    
    def _fetch_from_500(self):
        """从500彩票网抓取数据"""
        url = 'https://kaijiang.500.com/dlt.shtml'
        html = self._fetch_url(url)
        
        # 解析HTML提取数据
        # 查找期号
        period_match = re.search(r'<span class="expect">.*?(\d{5,7}).*?</span>', html, re.DOTALL)
        if not period_match:
            period_match = re.search(r'第(\d{5,7})期', html)
        
        if not period_match:
            raise Exception("无法解析期号")
        
        period = period_match.group(1)
        
        # 查找开奖号码 - 500彩票网格式
        # 前区号码
        front_pattern = r'<li class="ball_red">(\d+)</li>'
        front_matches = re.findall(front_pattern, html)
        
        # 后区号码
        back_pattern = r'<li class="ball_blue">(\d+)</li>'
        back_matches = re.findall(back_pattern, html)
        
        if len(front_matches) >= 5 and len(back_matches) >= 2:
            front_zone = [int(n) for n in front_matches[:5]]
            back_zone = [int(n) for n in back_matches[:2]]
        else:
            # 备用解析方式
            numbers_match = re.search(r'开奖号码[：:]\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\+?\s*(\d+)\s+(\d+)', html)
            if numbers_match:
                front_zone = [int(numbers_match.group(i)) for i in range(1, 6)]
                back_zone = [int(numbers_match.group(i)) for i in range(6, 8)]
            else:
                raise Exception("无法解析开奖号码")
        
        # 查找开奖日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html)
        draw_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        return {
            'period': period,
            'draw_date': draw_date,
            'front_zone': front_zone,
            'back_zone': back_zone,
            'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
        }
    
    def _fetch_from_caibao(self):
        """从彩宝网抓取数据"""
        url = 'https://www.78500.cn/kaijiang/dlt/'
        html = self._fetch_url(url)
        
        # 解析期号
        period_match = re.search(r'第(\d{5,7})期', html)
        if not period_match:
            raise Exception("无法解析期号")
        period = period_match.group(1)
        
        # 解析号码 - 查找数字序列
        numbers_match = re.search(r'(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', html)
        if not numbers_match:
            raise Exception("无法解析开奖号码")
        
        front_zone = [int(numbers_match.group(i)) for i in range(1, 6)]
        back_zone = [int(numbers_match.group(i)) for i in range(6, 8)]
        
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html)
        draw_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        return {
            'period': period,
            'draw_date': draw_date,
            'front_zone': front_zone,
            'back_zone': back_zone,
            'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
        }
    
    def _fetch_from_opencai(self):
        """从开彩网API抓取数据"""
        # 开彩网提供JSON API
        url = 'https://www.opencai.net/api/dlt/'
        
        try:
            data = self._fetch_url(url)
            json_data = json.loads(data)
            
            if json_data and len(json_data) > 0:
                latest = json_data[0]
                numbers = latest.get('opencode', '').replace('+', ',').split(',')
                
                if len(numbers) >= 7:
                    front_zone = [int(n.strip()) for n in numbers[:5]]
                    back_zone = [int(n.strip()) for n in numbers[5:7]]
                    
                    return {
                        'period': latest.get('expect', ''),
                        'draw_date': latest.get('opentime', '')[:10],
                        'front_zone': front_zone,
                        'back_zone': back_zone,
                        'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
                    }
        except:
            pass
        
        raise Exception("开彩网API请求失败")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_error(self, message):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'status': 'error', 'message': message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
