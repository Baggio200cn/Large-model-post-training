from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 导入历史数据
try:
    from .lottery_historical_data import get_latest_draw, get_historical_data
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from lottery_historical_data import get_latest_draw, get_historical_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 基于最新数据生成灵修因子
            latest = get_latest_draw()
            all_data = get_historical_data()
            
            # 使用最新期号作为随机种子，确保可重复性
            if latest:
                seed = int(latest['period'])
                random.seed(seed)
            
            spiritual_images = [
                'lotus_meditation.jpg',
                'mountain_zen.jpg', 
                'ocean_waves.jpg',
                'forest_tranquility.jpg',
                'sunset_chakra.jpg'
            ]
            
            selected_image = random.choice(spiritual_images)
            
            response = {
                'status': 'success',
                'spiritual_perturbation': {
                    'spiritual_image': {
                        'filename': selected_image,
                        'description': self._get_image_description(selected_image)
                    },
                    'perturbation_factors': {
                        'chaos_factor': round(random.uniform(0.1, 0.9), 3),
                        'harmony_factor': round(random.uniform(0.1, 0.9), 3),
                        'energy_level': random.choice(['极高', '高', '中等', '低', '极低']),
                        'cosmic_alignment': round(random.uniform(0.0, 1.0), 3)
                    },
                    'overall_intensity': round(random.uniform(0.3, 0.8), 3),
                    'spiritual_guidance': {
                        'meditation_time': f'{random.randint(5, 30)}分钟',
                        'recommended_mantra': random.choice([
                            '愿智慧照亮前路',
                            '心静自然凉',
                            '随缘不变，不变随缘',
                            '一切皆有可能'
                        ])
                    },
                    'based_on_period': latest['period'] if latest else None
                },
                'energy_reading': {
                    'cosmic_energy': f'{random.randint(60, 95)}%',
                    'earth_energy': f'{random.randint(50, 90)}%',
                    'personal_energy': f'{random.randint(70, 100)}%'
                },
                'data_info': {
                    'total_periods': len(all_data),
                    'latest_period': latest['period'] if latest else None
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
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def _get_image_description(self, filename):
        descriptions = {
            'lotus_meditation.jpg': '莲花冥想图，象征纯净与觉醒',
            'mountain_zen.jpg': '高山禅境图，代表稳定与高远',
            'ocean_waves.jpg': '海浪律动图，体现流动与变化',
            'forest_tranquility.jpg': '森林宁静图，传递自然与和谐',
            'sunset_chakra.jpg': '夕阳脉轮图，展现能量与平衡'
        }
        return descriptions.get(filename, '神秘灵修图像，蕴含无限可能')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
