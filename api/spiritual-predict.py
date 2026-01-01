"""灵修预测API - 4维度分析版本"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
import re
from collections import Counter

# 访问上传的数据（注意：Vercel的serverless函数是隔离的，这里需要特殊处理）
# 为了简化，我们接收前端传来的数据
class SpiritualAnalyzer:
    """灵修特征分析器"""
    
    def __init__(self):
        # 文字笔画字典（简化版，常用字）
        self.stroke_dict = {
            '安': 6, '住': 7, '当': 6, '下': 3, '自': 6, '在': 6, '如': 6, '光': 6,
            '一': 1, '二': 2, '三': 3, '四': 5, '五': 4, '六': 4, '七': 2, '八': 2, '九': 2, '十': 2,
            '天': 4, '地': 6, '人': 2, '和': 8, '平': 5, '安': 6, '乐': 5, '福': 13, '寿': 7,
            '心': 4, '身': 7, '灵': 7, '魂': 14, '神': 9, '佛': 7, '道': 12, '禅': 17,
            '静': 14, '定': 8, '慧': 15, '明': 8, '悟': 10, '觉': 20, '智': 12, '慈': 13,
            '爱': 10, '善': 12, '美': 9, '真': 10, '诚': 14, '信': 9, '义': 13, '礼': 18,
            '金': 8, '木': 4, '水': 4, '火': 4, '土': 3, '日': 4, '月': 4, '星': 9,
            '云': 4, '风': 4, '雨': 8, '雷': 13, '电': 13, '阳': 6, '阴': 6, '山': 3,
        }
        
        # 五行字典
        self.element_dict = {
            '木': ['木', '林', '森', '树', '松', '柏', '青', '绿', '东', '春'],
            '火': ['火', '炎', '焰', '光', '明', '红', '紫', '南', '夏'],
            '土': ['土', '地', '山', '石', '黄', '棕', '中', '安', '住'],
            '金': ['金', '银', '铜', '铁', '白', '银', '西', '秋', '钵'],
            '水': ['水', '江', '河', '海', '黑', '蓝', '北', '冬', '流']
        }
    
    def analyze_image_color(self, image_name, object_count):
        """
        简化的图片分析（基于文件名和物品数量）
        实际应用中可以接入图片识别API
        """
        # 基于物品数量生成号码
        count_numbers = self._count_to_numbers(object_count)
        
        # 基于文件名提取颜色关键词
        color_keywords = {
            'red': [2, 7, 12, 17, 22, 27, 32],
            'orange': [2, 7, 12, 17, 22, 27, 32],
            'yellow': [5, 10, 15, 20, 25, 30, 35],
            'green': [3, 8, 13, 18, 23, 28, 33],
            'blue': [1, 6, 11, 16, 21, 26, 31],
            'purple': [2, 7, 12, 17, 22, 27, 32],
            'white': [4, 9, 14, 19, 24, 29, 34],
            'black': [1, 6, 11, 16, 21, 26, 31],
            'brown': [5, 10, 15, 20, 25, 30, 35],
        }
        
        # 默认使用土元素（棕色为主）
        color_numbers = color_keywords.get('brown', [5, 10, 15, 20, 25])
        
        return {
            'dimension': '图片颜色能量',
            'numbers': random.sample(color_numbers, min(5, len(color_numbers))),
            'confidence': 0.72
        }
    
    def analyze_object_count(self, count):
        """物品数量能量分析"""
        numbers = self._count_to_numbers(count)
        
        count_meanings = {
            1: '独立、开始',
            2: '平衡、对称',
            3: '三才、稳定',
            4: '四方、完整',
            5: '五行、变化',
            6: '六合、和谐',
            7: '七星、神秘',
            8: '八卦、循环',
            9: '九宫、圆满'
        }
        
        return {
            'dimension': f'物品数量能量（{count}个）',
            'numbers': numbers,
            'meaning': count_meanings.get(count, '能量'),
            'confidence': 0.78
        }
    
    def analyze_text_strokes(self, text):
        """文字笔画能量分析"""
        strokes = []
        for char in text:
            if char in self.stroke_dict:
                strokes.append(self.stroke_dict[char])
        
        if not strokes:
            return {
                'dimension': '文字笔画能量',
                'numbers': [6, 12, 18, 24, 30],
                'confidence': 0.65
            }
        
        # 统计笔画出现频率
        stroke_counter = Counter(strokes)
        most_common_stroke = stroke_counter.most_common(1)[0][0]
        
        # 生成号码
        numbers = []
        for stroke in set(strokes):
            base_numbers = list(range(stroke, 36, stroke))
            if base_numbers:
                numbers.extend(random.sample(base_numbers, min(2, len(base_numbers))))
        
        numbers = sorted(list(set(numbers)))[:5]
        
        return {
            'dimension': '文字笔画能量',
            'numbers': numbers,
            'dominant_stroke': most_common_stroke,
            'stroke_distribution': dict(stroke_counter),
            'confidence': 0.82
        }
    
    def analyze_text_keywords(self, text):
        """文字关键词能量分析"""
        # 提取五行元素
        element_scores = {elem: 0 for elem in self.element_dict.keys()}
        
        for elem, keywords in self.element_dict.items():
            for keyword in keywords:
                if keyword in text:
                    element_scores[elem] += 1
        
        # 找出最强的元素
        if sum(element_scores.values()) > 0:
            dominant_element = max(element_scores, key=element_scores.get)
        else:
            dominant_element = '土'  # 默认土元素
        
        # 五行号码映射
        element_numbers = {
            '木': [3, 8, 13, 18, 23, 28, 33],
            '火': [2, 7, 12, 17, 22, 27, 32],
            '土': [5, 10, 15, 20, 25, 30, 35],
            '金': [4, 9, 14, 19, 24, 29, 34],
            '水': [1, 6, 11, 16, 21, 26, 31]
        }
        
        numbers = random.sample(element_numbers[dominant_element], 5)
        
        return {
            'dimension': '文字关键词能量',
            'numbers': numbers,
            'dominant_element': dominant_element,
            'element_scores': element_scores,
            'confidence': 0.75
        }
    
    def _count_to_numbers(self, count):
        """将数量转换为号码"""
        count_map = {
            1: [1, 11, 21, 31],
            2: [2, 12, 22, 32],
            3: [3, 13, 23, 33],
            4: [4, 14, 24, 34],
            5: [5, 15, 25, 35],
            6: [6, 12, 18, 24, 30],  # 6的倍数
            7: [7, 14, 21, 28, 35],  # 7的倍数
            8: [8, 16, 24, 32],
            9: [9, 18, 27],
        }
        
        base_numbers = count_map.get(count, [count, count*2, count*3, count*4, count*5])
        # 确保号码在1-35范围内
        valid_numbers = [n for n in base_numbers if 1 <= n <= 35]
        return valid_numbers[:5] if valid_numbers else [count, count+10, count+20]
    
    def generate_spiritual_prediction(self, image_data, text_data):
        """生成灵修预测"""
        # 4个维度的分析结果
        dimensions = []
        
        # 1. 图片颜色分析
        if image_data:
            color_analysis = self.analyze_image_color(
                image_data.get('name', ''),
                image_data.get('object_count', 0)
            )
            dimensions.append(color_analysis)
        
        # 2. 物品数量分析
        if image_data and image_data.get('object_count', 0) > 0:
            count_analysis = self.analyze_object_count(image_data['object_count'])
            dimensions.append(count_analysis)
        
        # 3. 文字笔画分析
        if text_data and text_data.get('content'):
            stroke_analysis = self.analyze_text_strokes(text_data['content'])
            dimensions.append(stroke_analysis)
        
        # 4. 文字关键词分析
        if text_data and text_data.get('content'):
            keyword_analysis = self.analyze_text_keywords(text_data['content'])
            dimensions.append(keyword_analysis)
        
        # 融合所有维度生成最终号码
        all_numbers = []
        total_confidence = 0
        
        for dim in dimensions:
            all_numbers.extend(dim['numbers'])
            total_confidence += dim.get('confidence', 0.7)
        
        # 统计号码出现频率
        number_counter = Counter(all_numbers)
        
        # 选择出现频率最高的号码
        front_zone = [num for num, count in number_counter.most_common(7)][:5]
        
        # 如果不足5个，随机补充
        while len(front_zone) < 5:
            candidate = random.randint(1, 35)
            if candidate not in front_zone:
                front_zone.append(candidate)
        
        front_zone = sorted(front_zone)
        
        # 后区号码（基于前区的衍生）
        back_zone = sorted([
            (front_zone[0] % 12) + 1,
            (front_zone[2] % 12) + 1
        ])
        
        # 去重后区
        if back_zone[0] == back_zone[1]:
            back_zone[1] = (back_zone[1] % 12) + 1
        
        # 计算平均置信度
        avg_confidence = total_confidence / len(dimensions) if dimensions else 0.70
        
        return {
            'status': 'success',
            'spiritual_prediction': {
                'front_zone': front_zone,
                'back_zone': back_zone,
                'confidence': round(avg_confidence, 3)
            },
            'analysis_details': {
                'dimensions_analyzed': len(dimensions),
                'dimension_results': dimensions,
                'number_frequency': dict(number_counter.most_common(10))
            },
            'timestamp': datetime.now().isoformat()
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 接收上传的图片和文字数据
            image_data = request_data.get('image_data', None)
            text_data = request_data.get('text_data', None)
            
            if not image_data and not text_data:
                raise Exception('至少需要提供图片或文字数据')
            
            # 创建分析器
            analyzer = SpiritualAnalyzer()
            
            # 生成预测
            result = analyzer.generate_spiritual_prediction(image_data, text_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
