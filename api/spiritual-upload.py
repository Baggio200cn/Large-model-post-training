# -*- coding: utf-8 -*-
"""
灵修上传模块API
支持图片和文本材料上传，每次产生不同的预测结果
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import hashlib
import random
import re


class SpiritualProcessor:
    """灵修材料处理器"""
    
    def __init__(self, image_data=None, text_data=None):
        self.image_data = image_data or ""
        self.text_data = text_data or ""
        self.energy_seed = self._calculate_energy_seed()
        random.seed(self.energy_seed)
    
    def _calculate_energy_seed(self):
        """根据上传内容计算唯一能量种子"""
        timestamp = str(datetime.now().timestamp())
        
        # 组合所有输入生成唯一种子
        seed_source = timestamp
        
        if self.image_data:
            # 图片数据的MD5作为种子一部分
            img_hash = hashlib.md5(self.image_data.encode()[:1000]).hexdigest()
            seed_source += img_hash
        
        if self.text_data:
            # 文本数据的MD5作为种子一部分
            text_hash = hashlib.md5(self.text_data.encode()).hexdigest()
            seed_source += text_hash
            # 文本长度也影响种子
            seed_source += str(len(self.text_data))
            # 中文字符数量
            chinese_count = len(re.findall(r'[\u4e00-\u9fff]', self.text_data))
            seed_source += str(chinese_count)
        
        # 生成最终种子
        final_hash = hashlib.sha256(seed_source.encode()).hexdigest()
        return int(final_hash[:8], 16)
    
    def analyze_image(self):
        """分析图片能量"""
        if not self.image_data:
            return {
                'energy': 0.5,
                'type': '中性能量',
                'description': '未上传图片，使用默认能量值'
            }
        
        # 基于图片数据特征计算能量
        data_length = len(self.image_data)
        
        # 模拟图片能量分析
        energy = (self.energy_seed % 1000) / 1000.0
        energy = 0.3 + energy * 0.6  # 范围 0.3-0.9
        
        # 根据能量值确定类型
        if energy > 0.7:
            energy_type = '阳性能量'
            description = '图片散发强烈正能量，适合选择大号'
        elif energy > 0.5:
            energy_type = '平衡能量'
            description = '图片能量平衡，适合均衡选号'
        else:
            energy_type = '阴性能量'
            description = '图片能量内敛，适合选择小号'
        
        # 颜色能量（模拟）
        color_energies = ['红色热情', '蓝色冷静', '绿色生机', '金色财运', '紫色神秘']
        color_energy = color_energies[self.energy_seed % len(color_energies)]
        
        return {
            'energy': round(energy, 3),
            'type': energy_type,
            'description': description,
            'color_energy': color_energy,
            'vibration_level': (self.energy_seed % 10) + 1,
            'chakra_resonance': ['根轮', '脐轮', '太阳轮', '心轮', '喉轮', '眉心轮', '顶轮'][self.energy_seed % 7]
        }
    
    def analyze_text(self):
        """分析文本能量"""
        if not self.text_data:
            return {
                'energy': 0.5,
                'keywords': [],
                'sentiment': 'neutral',
                'description': '未上传文本，使用默认能量值'
            }
        
        text = self.text_data
        
        # 提取文本中的数字
        numbers = re.findall(r'\d+', text)
        extracted_numbers = []
        for n in numbers:
            num = int(n)
            if 1 <= num <= 35:
                extracted_numbers.append(num)
        
        # 分析情感倾向
        positive_words = ['好', '吉', '顺', '旺', '发', '福', '喜', '乐', '财', '运', '赢', '中']
        negative_words = ['差', '凶', '难', '险', '亏', '败', '忧', '愁', '失', '空']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            energy = 0.6 + (positive_count * 0.05)
        elif negative_count > positive_count:
            sentiment = 'negative'
            energy = 0.4 - (negative_count * 0.03)
        else:
            sentiment = 'neutral'
            energy = 0.5
        
        energy = max(0.2, min(0.9, energy))
        
        # 五行分析
        five_elements = {
            '金': ['金', '银', '铁', '钢', '白', '西'],
            '木': ['木', '林', '森', '青', '绿', '东'],
            '水': ['水', '河', '海', '雨', '黑', '北'],
            '火': ['火', '炎', '热', '红', '南', '光'],
            '土': ['土', '地', '山', '黄', '中', '城']
        }
        
        element_scores = {}
        for element, keywords in five_elements.items():
            score = sum(1 for kw in keywords if kw in text)
            element_scores[element] = score
        
        dominant_element = max(element_scores, key=element_scores.get) if any(element_scores.values()) else '土'
        
        return {
            'energy': round(energy, 3),
            'keywords': extracted_numbers[:5],
            'sentiment': sentiment,
            'lucky_chars': positive_count,
            'warning_chars': negative_count,
            'dominant_element': dominant_element,
            'element_scores': element_scores,
            'text_length': len(text),
            'description': f'文本分析完成，主导五行为{dominant_element}，情感倾向{sentiment}'
        }
    
    def generate_spiritual_numbers(self):
        """基于灵修分析生成预测号码"""
        image_analysis = self.analyze_image()
        text_analysis = self.analyze_text()
        
        # 综合能量值
        combined_energy = (image_analysis['energy'] + text_analysis['energy']) / 2
        
        # 生成前区号码 (1-35选5个)
        front_candidates = list(range(1, 36))
        
        # 如果文本中有数字，优先考虑
        text_numbers = text_analysis.get('keywords', [])
        priority_numbers = [n for n in text_numbers if 1 <= n <= 35]
        
        # 根据能量调整号码倾向
        if combined_energy > 0.7:
            # 高能量偏向大号
            weights = [i * 2 for i in range(1, 36)]
        elif combined_energy < 0.4:
            # 低能量偏向小号
            weights = [36 - i for i in range(1, 36)]
        else:
            # 平衡能量均匀分布
            weights = [1] * 35
        
        # 优先号码加权
        for num in priority_numbers:
            if 1 <= num <= 35:
                weights[num - 1] *= 3
        
        # 加权随机选择
        front_zone = []
        available = list(range(1, 36))
        available_weights = weights.copy()
        
        for _ in range(5):
            if not available:
                break
            total = sum(available_weights)
            if total == 0:
                selected = random.choice(available)
            else:
                r = random.uniform(0, total)
                cumsum = 0
                selected = available[0]
                for i, num in enumerate(available):
                    cumsum += available_weights[i]
                    if cumsum >= r:
                        selected = num
                        break
            
            front_zone.append(selected)
            idx = available.index(selected)
            available.pop(idx)
            available_weights.pop(idx)
        
        front_zone = sorted(front_zone)
        
        # 生成后区号码 (1-12选2个)
        back_candidates = list(range(1, 13))
        back_weights = [1] * 12
        
        # 文本中1-12的数字优先
        for num in priority_numbers:
            if 1 <= num <= 12:
                back_weights[num - 1] *= 3
        
        back_zone = []
        available_back = list(range(1, 13))
        available_back_weights = back_weights.copy()
        
        for _ in range(2):
            if not available_back:
                break
            total = sum(available_back_weights)
            if total == 0:
                selected = random.choice(available_back)
            else:
                r = random.uniform(0, total)
                cumsum = 0
                selected = available_back[0]
                for i, num in enumerate(available_back):
                    cumsum += available_back_weights[i]
                    if cumsum >= r:
                        selected = num
                        break
            
            back_zone.append(selected)
            idx = available_back.index(selected)
            available_back.pop(idx)
            available_back_weights.pop(idx)
        
        back_zone = sorted(back_zone)
        
        # 计算置信度
        base_confidence = 0.5
        if self.image_data:
            base_confidence += 0.1
        if self.text_data:
            base_confidence += 0.1
        if priority_numbers:
            base_confidence += 0.05 * min(len(priority_numbers), 3)
        
        confidence = min(0.85, base_confidence + random.uniform(0, 0.1))
        
        return {
            'front_zone': front_zone,
            'back_zone': back_zone,
            'confidence': round(confidence, 3),
            'energy_level': round(combined_energy, 3),
            'energy_seed': self.energy_seed
        }
    
    def get_guidance(self):
        """获取灵修指导建议"""
        image_analysis = self.analyze_image()
        text_analysis = self.analyze_text()
        combined_energy = (image_analysis['energy'] + text_analysis['energy']) / 2
        
        # 冥想建议
        if combined_energy > 0.7:
            meditation = '当前能量充沛，建议进行10分钟静心冥想，保持内心平和'
        elif combined_energy > 0.5:
            meditation = '能量平衡，建议15分钟深度冥想，增强直觉感应'
        else:
            meditation = '能量较弱，建议20分钟能量冥想，提升精神状态'
        
        # 吉时建议
        hour = datetime.now().hour
        lucky_times = {
            (5, 7): '卯时(5-7点)',
            (7, 9): '辰时(7-9点)',
            (9, 11): '巳时(9-11点)',
            (11, 13): '午时(11-13点)',
            (13, 15): '未时(13-15点)',
            (15, 17): '申时(15-17点)',
            (17, 19): '酉时(17-19点)',
            (19, 21): '戌时(19-21点)',
            (21, 23): '亥时(21-23点)',
            (23, 1): '子时(23-1点)',
            (1, 3): '丑时(1-3点)',
            (3, 5): '寅时(3-5点)'
        }
        
        current_time = '午时(11-13点)'  # 默认
        for (start, end), name in lucky_times.items():
            if start <= hour < end:
                current_time = name
                break
        
        # 能量建议
        if combined_energy > 0.7:
            energy_advice = '能量旺盛，适合行动，把握机会'
        elif combined_energy > 0.5:
            energy_advice = '能量稳定，适合思考，静待时机'
        else:
            energy_advice = '能量蓄积，适合休养，厚积薄发'
        
        return {
            'meditation_suggestion': meditation,
            'lucky_time': current_time,
            'energy_advice': energy_advice,
            'mantra': ['心静自然凉', '随缘不变', '福至心灵', '天道酬勤'][self.energy_seed % 4]
        }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            # 获取上传的图片和文本
            image_data = request_data.get('image_data', '')  # Base64编码的图片
            text_data = request_data.get('text_data', '')    # 文本内容
            
            # 创建处理器
            processor = SpiritualProcessor(image_data, text_data)
            
            # 分析并生成预测
            image_analysis = processor.analyze_image()
            text_analysis = processor.analyze_text()
            prediction = processor.generate_spiritual_numbers()
            guidance = processor.get_guidance()
            
            response = {
                'status': 'success',
                'spiritual_prediction': prediction,
                'analysis_details': {
                    'image_analysis': image_analysis,
                    'text_analysis': text_analysis,
                    'has_image': bool(image_data),
                    'has_text': bool(text_data)
                },
                'guidance': guidance,
                'meta': {
                    'energy_seed': prediction['energy_seed'],
                    'generated_at': datetime.now().isoformat(),
                    'input_summary': {
                        'image_size': len(image_data) if image_data else 0,
                        'text_length': len(text_data) if text_data else 0
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
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """GET请求返回使用说明"""
        response = {
            'status': 'success',
            'message': '灵修上传API - 请使用POST方法',
            'usage': {
                'method': 'POST',
                'content_type': 'application/json',
                'parameters': {
                    'image_data': 'Base64编码的图片数据（可选）',
                    'text_data': '文本材料内容（可选）'
                },
                'example': {
                    'image_data': 'data:image/jpeg;base64,/9j/4AAQ...',
                    'text_data': '今日感悟：心静自然凉，万事皆可期。幸运数字8、15、23。'
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
