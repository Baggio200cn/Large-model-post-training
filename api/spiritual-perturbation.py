from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 灵修图片列表
SPIRITUAL_IMAGES = [
    {'id': 1, 'name': 'lotus', 'desc': '莲花冥想图', 'meaning': '纯净与觉醒', 'energy': 0.85},
    {'id': 2, 'name': 'mountain', 'desc': '高山禅境图', 'meaning': '稳定与高远', 'energy': 0.78},
    {'id': 3, 'name': 'ocean', 'desc': '海浪律动图', 'meaning': '流动与变化', 'energy': 0.92},
    {'id': 4, 'name': 'forest', 'desc': '森林宁静图', 'meaning': '自然与和谐', 'energy': 0.81},
    {'id': 5, 'name': 'sunset', 'desc': '夕阳脉轮图', 'meaning': '能量与平衡', 'energy': 0.88}
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
    
    # 月相影响（简
