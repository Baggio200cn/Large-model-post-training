from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 最新开奖数据 - 请在每次开奖后手动更新这里
        latest_results = {
            'period': '25112',  # 👈 更新期数
            'draw_date': '2025-10-06',  # 👈 更新日期
            'draw_time': '20:30:00',
            'winning_numbers': {
                'front_zone': [5, 12, 18, 24, 33],  # 👈 更新前区号码
                'back_zone': [6, 11]  # 👈 更新后区号码
            },
            'prize_info': {
                'total_sales': '32,156万元',  # 👈 更新销售额
                'jackpot_pool': '2,456万元',  # 👈 更新奖池
                'total_winners': '2,345,678注'  # 👈 更新中奖注数
            },
            'next_draw': {
                'date': '2025-10-09',  # 👈 更新下期日期
                'period': '25113',  # 👈 更新下期期数
                'estimated_jackpot': '2,800万元'
            },
            'regional_winners': [
                {'province': '广东', 'city': '深圳', 'winners': 1, 'prize_level': '一等奖'},
                {'province': '江苏', 'city': '南京', 'winners': 1, 'prize_level': '一等奖'}
            ],
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_note': f'数据更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }
        
        response = {
            'status': 'success',
            'latest_results': latest_results,
            'data_source': 'manual_update',
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# 更新说明：
# 1. 每周开奖后（周一、三、六晚上）
# 2. 访问 https://www.lottery.gov.cn 查看最新结果
# 3. 更新上面标记 👈 的数据
# 4. 提交到GitHub，Vercel会自动重新部署
# 5. 整个过程不到5分钟
