"""最新开奖结果API - All-in-One版本"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 生成模拟的最新开奖结果
            draw_date = datetime.now() - timedelta(days=random.randint(1, 3))
            period = f'25{random.randint(100, 150):03d}'
            front_zone = sorted(random.sample(range(1, 36), 5))
            back_zone = sorted(random.sample(range(1, 13), 2))
            
            # 生成中奖统计
            first_prize = random.randint(0, 3)
            second_prize = random.randint(5, 25)
            
            provinces = ['北京', '上海', '广东', '江苏', '浙江', '山东']
            selected_provinces = random.sample(provinces, random.randint(2, 4))
            
            regional_winners = [
                {
                    'province': prov,
                    'winners': random.randint(1, 3),
                    'prize_level': random.choice(['一等奖', '二等奖', '三等奖'])
                }
                for prov in selected_provinces
            ]
            
            response = {
                'status': 'success',
                'latest_results': {
                    'period': period,
                    'draw_date': draw_date.strftime('%Y-%m-%d'),
                    'draw_time': '21:15:00',
                    'winning_numbers': {
                        'front_zone': front_zone,
                        'back_zone': back_zone,
                        'display': f"{' '.join([f'{n:02d}' for n in front_zone])} + {' '.join([f'{n:02d}' for n in back_zone])}"
                    },
                    'prize_breakdown': [
                        {
                            'level': '一等奖',
                            'condition': '前区5个号码+后区2个号码',
                            'winners': first_prize,
                            'prize_per_winner': f'{random.randint(500, 1500)}万元',
                            'total_amount': f'{first_prize * random.randint(500, 1500)}万元' if first_prize > 0 else '0元'
                        },
                        {
                            'level': '二等奖',
                            'condition': '前区5个号码+后区1个号码',
                            'winners': second_prize,
                            'prize_per_winner': f'{random.randint(15, 50)}万元',
                            'total_amount': f'{second_prize * random.randint(15, 50)}万元'
                        },
                        {
                            'level': '三等奖',
                            'condition': '前区5个号码',
                            'winners': random.randint(50, 200),
                            'prize_per_winner': f'{random.randint(8000, 15000)}元',
                            'total_amount': f'{random.randint(400, 3000)}万元'
                        }
                    ],
                    'total_sales': f'{random.randint(18000, 35000)}万元',
                    'jackpot_info': {
                        'current_pool': f'{random.randint(800, 2000)}万元',
                        'is_rollover': random.choice([True, False])
                    },
                    'regional_winners': regional_winners,
                    'statistics': {
                        'total_winners': random.randint(10000, 50000),
                        'total_prize_amount': f'{random.randint(8000, 18000)}万元'
                    },
                    'next_draw': {
                        'date': (draw_date + timedelta(days=7)).strftime('%Y-%m-%d'),
                        'estimated_jackpot': f'{random.randint(800, 2000)}万元'
                    }
                },
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
    
    def do_POST(self):
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
