from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 灵修图片列表（实际应该上传到/public/spiritual/）
SPIRITUAL_IMAGES = [
    {'id': 1, 'name': 'lotus', 'desc': '莲花冥想', 'energy': 0.85},
    {'id': 2, 'name': 'mountain', 'desc': '高山禅境', 'energy': 0.78},
    {'id': 3, 'name': 'ocean', 'desc': '海浪律动', 'energy': 0.92},
    {'id': 4, 'name': 'forest', 'desc': '森林宁静', 'energy': 0.81},
    {'id': 5, 'name': 'sunset', 'desc': '夕阳脉轮', 'energy': 0.88}
]

def calculate_spiritual_factor():
    """计算灵修扰动因子"""
    # 基于时间的能量场
    hour = datetime.now().hour
    if 6 <= hour < 9:
        time_energy = 0.9  # 清晨能量旺盛
    elif 12 <= hour < 14:
        time_energy = 0.8  # 午时平稳
    elif 18 <= hour < 21:
        time_energy = 0.85  # 傍晚较好
    else:
        time_energy = 0.7  # 其他时间
    
    # 随机选择灵修图片
    image = random.choice(SPIRITUAL_IMAGES)
    
    # 混沌因子（随机性）
    chaos = random.uniform(0.1, 0.3)
    
    # 和谐因子
    harmony = 1 - chaos
    
    # 宇宙调谐
    cosmic = (time_energy + image['energy']) / 2
    
    return {
        'image': image,
        'time_energy': time_energy,
        'chaos_factor': round(chaos, 3),
        'harmony_factor': round(harmony, 3),
        'cosmic_alignment': round(cosmic, 3),
        'overall_weight': round(0.15, 2)  # 灵修占总权重的15%
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            spiritual = calculate_spiritual_factor()
            
            # 灵修建议
            if spiritual['cosmic_alignment'] > 0.85:
                guidance = '今日宇宙能量极佳，适合大胆选择'
            elif spiritual['cosmic_alignment'] > 0.75:
                guidance = '能量场较为和谐，可以适度尝试'
            else:
                guidance = '能量波动较大，建议保守选择'
            
            response = {
                'status': 'success',
                'spiritual_data': {
                    'selected_image': spiritual['image'],
                    'energy_analysis': {
                        'time_energy': spiritual['time_energy'],
                        'chaos_factor': spiritual['chaos_factor'],
                        'harmony_factor': spiritual['harmony_factor'],
                        'cosmic_alignment': spiritual['cosmic_alignment']
                    },
                    'weight_info': {
                        'spiritual_weight': spiritual['overall_weight'],
                        'ai_weight': 0.85,
                        'description': 'AI模型85% + 灵修扰动15%'
                    },
                    'guidance': guidance,
                    'meditation_suggestion': f"建议冥想{random.randint(5, 15)}分钟"
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
            error = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
