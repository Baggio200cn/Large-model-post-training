"""
灵修直觉预测 API - 支持图片+文字多模态输入
基于图像色彩分析和文字情感分析生成预测
"""
from http.server import BaseHTTPRequestHandler
import json
import base64
import io
import sys
import os
from typing import Dict, List, Tuple

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class SpiritualPredictor:
    """灵修预测器"""

    def __init__(self):
        # 色彩-能量映射
        self.color_energy_map = {
            'red': {'energy': 0.9, 'zone': 'high'},      # 红色 → 高区
            'orange': {'energy': 0.8, 'zone': 'high'},   # 橙色
            'yellow': {'energy': 0.7, 'zone': 'medium'}, # 黄色 → 中区
            'green': {'energy': 0.6, 'zone': 'medium'},  # 绿色
            'blue': {'energy': 0.4, 'zone': 'low'},      # 蓝色 → 低区
            'purple': {'energy': 0.5, 'zone': 'medium'}, # 紫色
            'white': {'energy': 0.8, 'zone': 'high'},    # 白色 → 阳
            'black': {'energy': 0.2, 'zone': 'low'}      # 黑色 → 阴
        }

        # 关键词-能量映射
        self.keyword_energy_map = {
            '火': 0.9, '热': 0.85, '阳': 0.8, '光': 0.75,
            '水': 0.3, '冷': 0.25, '阴': 0.2, '暗': 0.15,
            '金': 0.7, '木': 0.6, '土': 0.5,
            '天': 0.8, '地': 0.4, '人': 0.6,
            '龙': 0.9, '凤': 0.85, '虎': 0.8, '鹤': 0.7
        }

    def analyze_image_simple(self, image_base64: str) -> Dict:
        """
        简化版图像分析（不依赖PIL）
        从base64中提取基础信息

        Args:
            image_base64: base64编码的图片

        Returns:
            {'dominant_color': str, 'energy': float, 'brightness': float}
        """
        # 简化实现：基于文件大小和编码特征推测
        data_length = len(image_base64)

        # 模拟分析结果（实际应该用PIL或OpenCV）
        # 这里用伪随机但确定性的方法
        hash_val = sum(ord(c) for c in image_base64[:100]) % 100

        if hash_val < 20:
            color = 'red'
        elif hash_val < 35:
            color = 'orange'
        elif hash_val < 50:
            color = 'yellow'
        elif hash_val < 65:
            color = 'green'
        elif hash_val < 80:
            color = 'blue'
        else:
            color = 'purple'

        energy_info = self.color_energy_map.get(color, {'energy': 0.5, 'zone': 'medium'})

        return {
            'dominant_color': color,
            'energy': energy_info['energy'],
            'zone': energy_info['zone'],
            'brightness': (data_length % 100) / 100.0
        }

    def analyze_text(self, text: str) -> Dict:
        """
        文字情感分析

        Args:
            text: 用户输入的文字

        Returns:
            {'energy': float, 'keywords': List[str]}
        """
        if not text:
            return {'energy': 0.5, 'keywords': []}

        # 检测关键词
        found_keywords = []
        total_energy = 0.5  # 基础能量

        for keyword, energy in self.keyword_energy_map.items():
            if keyword in text:
                found_keywords.append(keyword)
                total_energy += (energy - 0.5) * 0.2  # 调整权重

        # 限制能量范围
        total_energy = max(0.1, min(0.9, total_energy))

        return {
            'energy': total_energy,
            'keywords': found_keywords,
            'length': len(text)
        }

    def generate_prediction(self,
                           image_analysis: Dict = None,
                           text_analysis: Dict = None) -> Dict:
        """
        基于多模态分析生成预测

        Args:
            image_analysis: 图像分析结果
            text_analysis: 文字分析结果

        Returns:
            {'front': [5个号码], 'back': [2个号码], 'energy': float, 'method': str}
        """
        # 计算综合能量
        img_energy = image_analysis['energy'] if image_analysis else 0.5
        txt_energy = text_analysis['energy'] if text_analysis else 0.5

        # 图像权重60%，文字权重40%
        total_energy = img_energy * 0.6 + txt_energy * 0.4

        # 根据能量值生成号码
        front_zone = self._generate_front_numbers(total_energy, image_analysis)
        back_zone = self._generate_back_numbers(total_energy, text_analysis)

        return {
            'front_zone': sorted(front_zone),
            'back_zone': sorted(back_zone),
            'energy': total_energy,
            'energy_level': self._get_energy_level(total_energy),
            'image_influence': img_energy,
            'text_influence': txt_energy,
            'method': 'multimodal_spiritual_analysis'
        }

    def _generate_front_numbers(self, energy: float, image_analysis: Dict) -> List[int]:
        """生成前区5个号码"""
        import random

        numbers = []
        zone = image_analysis.get('zone', 'medium') if image_analysis else 'medium'

        # 根据能量区间选择号码范围
        if zone == 'high':
            pool = list(range(20, 36))  # 高能量 → 大数
        elif zone == 'low':
            pool = list(range(1, 16))   # 低能量 → 小数
        else:
            pool = list(range(8, 28))   # 中能量 → 中间数

        # 能量越高，越倾向于选大数
        if energy > 0.7:
            pool = sorted(pool, reverse=True)
        elif energy < 0.3:
            pool = sorted(pool)

        # 随机选择5个
        random.seed(int(energy * 10000))  # 使用能量值作为种子
        numbers = random.sample(pool, min(5, len(pool)))

        # 如果不足5个，从全范围补充
        if len(numbers) < 5:
            remaining = list(set(range(1, 36)) - set(numbers))
            numbers.extend(random.sample(remaining, 5 - len(numbers)))

        return numbers[:5]

    def _generate_back_numbers(self, energy: float, text_analysis: Dict) -> List[int]:
        """生成后区2个号码"""
        import random

        # 后区范围 1-12
        keywords = text_analysis.get('keywords', []) if text_analysis else []

        # 特殊关键词映射
        special_map = {
            '龙': [3, 9],    # 龙 → 3, 9
            '虎': [7, 11],   # 虎 → 7, 11
            '凤': [5, 10],   # 凤 → 5, 10
            '鹤': [2, 8]     # 鹤 → 2, 8
        }

        # 检查是否有特殊关键词
        for keyword in keywords:
            if keyword in special_map:
                return special_map[keyword]

        # 否则根据能量值生成
        random.seed(int(energy * 5000))
        if energy > 0.6:
            pool = list(range(7, 13))  # 高能量 → 大数
        elif energy < 0.4:
            pool = list(range(1, 7))   # 低能量 → 小数
        else:
            pool = list(range(1, 13))  # 中能量 → 全范围

        return sorted(random.sample(pool, 2))

    def _get_energy_level(self, energy: float) -> str:
        """能量等级描述"""
        if energy >= 0.8:
            return '极强'
        elif energy >= 0.6:
            return '强'
        elif energy >= 0.4:
            return '中等'
        elif energy >= 0.2:
            return '弱'
        else:
            return '极弱'


class handler(BaseHTTPRequestHandler):
    """API Handler"""

    def do_POST(self):
        """处理POST请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            # 提取输入
            image_base64 = data.get('image')  # base64编码的图片
            text = data.get('text', '')       # 文字描述

            # 初始化预测器
            predictor = SpiritualPredictor()

            # 分析图像
            image_analysis = None
            if image_base64:
                image_analysis = predictor.analyze_image_simple(image_base64)

            # 分析文字
            text_analysis = predictor.analyze_text(text)

            # 生成预测
            prediction = predictor.generate_prediction(image_analysis, text_analysis)

            # 构建响应
            response = {
                'success': True,
                'spiritual_prediction': prediction,
                'image_analysis': image_analysis,
                'text_analysis': text_analysis,
                'interpretation': self._generate_interpretation(prediction, text_analysis)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'success': False,
                'error': str(e),
                'message': '灵修分析失败，请检查输入'
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _generate_interpretation(self, prediction: Dict, text_analysis: Dict) -> str:
        """生成解读文字"""
        energy_level = prediction['energy_level']
        keywords = text_analysis.get('keywords', [])

        interpretation = f"🔮 灵修感应强度：{energy_level}\n\n"

        if keywords:
            interpretation += f"检测到关键能量词：{', '.join(keywords)}\n"

        interpretation += f"\n能量值 {prediction['energy']:.2f} "
        interpretation += f"(图像影响 {prediction['image_influence']:.2f}, "
        interpretation += f"文字影响 {prediction['text_influence']:.2f})\n\n"
        interpretation += "建议综合其他预测方法使用。"

        return interpretation
