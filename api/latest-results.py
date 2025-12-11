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
                    'date': latest['date'],  # 兼容字段
                    'front_zone': latest['front'],
                    'back_zone': latest['back'],
                    'numbers': latest['front'] + latest['back'],  # 兼容字段：合并号码
                    'display': f"{' '.join([str(n).zfill(2) for n in latest['front']])} + {' '.join([str(n).zfill(2) for n in latest['back']])}"
                }
                data_source = "backup"
                error_msg = "实时抓取失败，使用备份数据。" + error_msg
            
            if result:
                # 确保result有兼容字段
                if 'date' not in result:
                    result['date'] = result.get('draw_date', '')
                if 'numbers' not in result:
                    result['numbers'] = result.get('front_zone', []) + result.get('back_zone', [])
                
                # 构建最近开奖列表（兼容两种格式）
                recent_results = []
                if data_source == "backup":
                    for item in BACKUP_DATA[:10]:
                        recent_results.append({
                            'period': item['period'],
                            'date': item['date'],
                            'draw_date': item['date'],
                            'front_zone': item['front'],
                            'back_zone': item['back'],
                            'numbers': item['front'] + item['back']  # 兼容字段
                        })
                
                # 计算数据范围
                if BACKUP_DATA:
                    first_period = BACKUP_DATA[-1]['period']
                    last_period = BACKUP_DATA[0]['period']
                    data_range = f"第{first_period}期 - 第{last_period}期"
                else:
                    data_range = "暂无数据"
                
                response = {
                    'status': 'success',
                    'latest_result': result,
                    'recent_results': recent_results if recent_results else [],
                    'data_source': data_source,
                    'is_realtime': data_source != "backup",
                    'fetch_time': datetime.now().isoformat(),
                    'message': error_msg if data_source == "backup" else "",
                    # 兼容admin.html的字段
                    'total_periods': len(BACKUP_DATA),
                    'data_range': data_range,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                response = {
                    'status': 'error',
                    'message': f'无法从任何数据源获取数据，请检查网络或数据源状态',
                    'timestamp': datetime.now().isoformat()
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
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _make_request(self, url, timeout=10):
        """统一的HTTP请求方法"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if HAS_REQUESTS:
            response = requests.get(url, headers=headers, timeout=timeout)
            return response.text
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8')
    
    def _fetch_from_500(self):
        """从500彩票网抓取"""
        url = "https://datachart.500.com/dlt/history/newinc/history.php"
        html = self._make_request(url)
        
        # 解析HTML获取最新一期数据
        # 500彩票网格式: <tr class="t_tr1"><td>25139</td><td>2025-12-06</td><td>...</td></tr>
        period_match = re.search(r'<td[^>]*>(\d{5,7})</td>', html)
        if not period_match:
            raise Exception("无法解析期号")
        
        period = period_match.group(1)
        
        # 提取日期
        date_match = re.search(r'<td[^>]*>(\d{4}-\d{2}-\d{2})</td>', html)
        date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        # 提取前区号码 (红球)
        front_pattern = r'<td class="t_cfont2">(\d+)</td>'
        front_matches = re.findall(front_pattern, html)
        if len(front_matches) < 5:
            raise Exception("无法解析前区号码")
        
        front_zone = [int(n) for n in front_matches[:5]]
        
        # 提取后区号码 (蓝球)
        back_pattern = r'<td class="t_cfont4">(\d+)</td>'
        back_matches = re.findall(back_pattern, html)
        if len(back_matches) < 2:
            raise Exception("无法解析后区号码")
        
        back_zone = [int(n) for n in back_matches[:2]]
        
        return {
            'period': period,
            'draw_date': date,
            'date': date,  # 兼容字段
            'front_zone': front_zone,
            'back_zone': back_zone,
            'numbers': front_zone + back_zone,  # 兼容字段
            'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
        }
    
    def _fetch_from_caibao(self):
        """从彩宝网抓取"""
        url = "https://www.zhcw.com/kjxx/dlt/"
        html = self._make_request(url)
        
        # 彩宝网解析逻辑
        period_match = re.search(r'第\s*(\d{5,7})\s*期', html)
        if not period_match:
            raise Exception("无法解析期号")
        
        period = period_match.group(1)
        
        # 提取号码
        ball_pattern = r'<em[^>]*class="[^"]*ball[^"]*"[^>]*>(\d+)</em>'
        balls = re.findall(ball_pattern, html)
        
        if len(balls) < 7:
            raise Exception("无法解析号码")
        
        front_zone = [int(n) for n in balls[:5]]
        back_zone = [int(n) for n in balls[5:7]]
        
        return {
            'period': period,
            'draw_date': datetime.now().strftime('%Y-%m-%d'),
            'date': datetime.now().strftime('%Y-%m-%d'),  # 兼容字段
            'front_zone': front_zone,
            'back_zone': back_zone,
            'numbers': front_zone + back_zone,  # 兼容字段
            'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
        }
    
    def _fetch_from_opencai(self):
        """从开彩网API抓取"""
        url = "https://www.opencai.net/api/dlt/"
        data = self._make_request(url)
        
        try:
            json_data = json.loads(data)
            if isinstance(json_data, list) and len(json_data) > 0:
                latest = json_data[0]
                numbers = latest.get('opencode', '').split(',')
                
                if len(numbers) >= 7:
                    front_zone = [int(n) for n in numbers[:5]]
                    back_zone = [int(n) for n in numbers[5:7]]
                    
                    return {
                        'period': latest.get('expect', ''),
                        'draw_date': latest.get('opentime', '')[:10],
                        'date': latest.get('opentime', '')[:10],  # 兼容字段
                        'front_zone': front_zone,
                        'back_zone': back_zone,
                        'numbers': front_zone + back_zone,  # 兼容字段
                        'display': f"{' '.join([str(n).zfill(2) for n in front_zone])} + {' '.join([str(n).zfill(2) for n in back_zone])}"
                    }
        except:
            pass
        
        raise Exception("API数据解析失败")
