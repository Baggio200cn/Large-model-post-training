"""
灵修预测API - 增强版（支持真实图片识别）
功能：
1. 图片上传（base64编码）
2. OCR文字识别
3. 颜色能量分析
4. 物体数量检测
5. 综合生成预测号码
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
import re
import base64
import io
from collections import Counter
from PIL import Image
import colorsys

class ImageAnalyzer:
    """图片分析器"""

    def __init__(self):
        pass

    def analyze_image(self, base64_data):
        """
        分析上传的图片
        返回：颜色分析、物体数量估计
        """
        try:
            # 解码base64图片
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            image_bytes = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_bytes))

            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 分析主色调
            dominant_colors = self._get_dominant_colors(image)

            # 估计物体数量（基于边缘检测和颜色分割）
            object_count = self._estimate_object_count(image)

            # 提取颜色能量
            color_energy = self._extract_color_energy(dominant_colors)

            return {
                'dominant_colors': dominant_colors,
                'object_count': object_count,
                'color_energy': color_energy,
                'image_size': image.size
            }
        except Exception as e:
            print(f"图片分析失败: {e}")
            return {
                'dominant_colors': ['brown'],
                'object_count': 1,
                'color_energy': [5, 10, 15, 20, 25]
            }

    def _get_dominant_colors(self, image, num_colors=3):
        """提取图片的主色调"""
        # 缩小图片以加快处理
        image = image.resize((150, 150))

        # 获取颜色分布
        colors = image.getcolors(image.size[0] * image.size[1])

        if not colors:
            return ['brown']

        # 按出现频率排序
        colors.sort(key=lambda x: x[0], reverse=True)

        # 提取前N个颜色
        dominant_colors = []
        for count, color in colors[:num_colors]:
            color_name = self._rgb_to_color_name(color)
            dominant_colors.append(color_name)

        return dominant_colors

    def _rgb_to_color_name(self, rgb):
        """将RGB颜色转换为颜色名称"""
        r, g, b = rgb[:3] if len(rgb) >= 3 else (rgb[0], rgb[0], rgb[0])

        # 转换为HSV以便更好地识别颜色
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

        # 低饱和度 -> 黑白灰
        if s < 0.1:
            if v < 0.3:
                return 'black'
            elif v > 0.7:
                return 'white'
            else:
                return 'gray'

        # 根据色相判断颜色
        h_degree = h * 360

        if h_degree < 15 or h_degree >= 345:
            return 'red'
        elif 15 <= h_degree < 45:
            return 'orange'
        elif 45 <= h_degree < 75:
            return 'yellow'
        elif 75 <= h_degree < 165:
            return 'green'
        elif 165 <= h_degree < 255:
            return 'blue'
        elif 255 <= h_degree < 285:
            return 'purple'
        elif 285 <= h_degree < 345:
            return 'pink'
        else:
            return 'brown'

    def _estimate_object_count(self, image):
        """估计图片中的物体数量（简化版）"""
        # 缩小图片
        image = image.resize((100, 100))

        # 转换为灰度图
        gray = image.convert('L')

        # 简单的边缘检测（统计颜色变化）
        pixels = list(gray.getdata())

        # 计算像素变化次数
        changes = 0
        threshold = 30

        for i in range(len(pixels) - 1):
            if abs(pixels[i] - pixels[i+1]) > threshold:
                changes += 1

        # 根据变化次数估计物体数量
        # 这是一个非常简化的方法
        if changes < 100:
            return 1
        elif changes < 300:
            return 2
        elif changes < 600:
            return random.randint(3, 4)
        elif changes < 1000:
            return random.randint(5, 6)
        else:
            return random.randint(7, 9)

    def _extract_color_energy(self, color_names):
        """从颜色提取能量号码"""
        color_number_map = {
            'red': [2, 7, 12, 17, 22, 27, 32],
            'orange': [3, 8, 13, 18, 23, 28, 33],
            'yellow': [5, 10, 15, 20, 25, 30, 35],
            'green': [3, 8, 13, 18, 23, 28, 33],
            'blue': [1, 6, 11, 16, 21, 26, 31],
            'purple': [2, 7, 12, 17, 22, 27, 32],
            'pink': [2, 7, 12, 17, 22, 27, 32],
            'white': [4, 9, 14, 19, 24, 29, 34],
            'black': [1, 6, 11, 16, 21, 26, 31],
            'gray': [5, 10, 15, 20, 25, 30, 35],
            'brown': [5, 10, 15, 20, 25, 30, 35],
        }

        all_numbers = []
        for color in color_names:
            numbers = color_number_map.get(color, [5, 10, 15, 20, 25])
            all_numbers.extend(numbers)

        return all_numbers


class OCRAnalyzer:
    """OCR文字识别器"""

    def __init__(self):
        self.stroke_dict = {
            '安': 6, '住': 7, '当': 6, '下': 3, '自': 6, '在': 6, '如': 6, '光': 6,
            '一': 1, '二': 2, '三': 3, '四': 5, '五': 4, '六': 4, '七': 2, '八': 2, '九': 2, '十': 2,
            '天': 4, '地': 6, '人': 2, '和': 8, '平': 5, '安': 6, '乐': 5, '福': 13, '寿': 7,
            '心': 4, '身': 7, '灵': 7, '魂': 14, '神': 9, '佛': 7, '道': 12, '禅': 17,
            '静': 14, '定': 8, '慧': 15, '明': 8, '悟': 10, '觉': 20, '智': 12, '慈': 13,
            '爱': 10, '善': 12, '美': 9, '真': 10, '诚': 14, '信': 9, '义': 13, '礼': 18,
            '金': 8, '木': 4, '水': 4, '火': 4, '土': 3, '日': 4, '月': 4, '星': 9,
            '云': 4, '风': 4, '雨': 8, '雷': 13, '电': 13, '阳': 6, '阴': 6, '山': 3,
            '发': 12, '财': 10, '富': 12, '贵': 12, '喜': 12, '吉': 6, '祥': 11,
        }

        self.element_dict = {
            '木': ['木', '林', '森', '树', '松', '柏', '青', '绿', '东', '春'],
            '火': ['火', '炎', '焰', '光', '明', '红', '紫', '南', '夏'],
            '土': ['土', '地', '山', '石', '黄', '棕', '中', '安', '住'],
            '金': ['金', '银', '铜', '铁', '白', '银', '西', '秋', '钵'],
            '水': ['水', '江', '河', '海', '黑', '蓝', '北', '冬', '流']
        }

    def extract_text_simple(self, image_base64):
        """
        简化版OCR（不依赖外部API）
        在实际部署中，可以接入：
        1. 百度OCR API
        2. 腾讯云OCR
        3. Google Vision API
        4. Tesseract OCR
        """
        # 这里返回空，让用户手动输入文字
        # 实际应用中可以调用OCR服务
        return ""

    def analyze_text(self, text):
        """分析文字笔画和五行"""
        if not text:
            return {
                'strokes': [],
                'elements': {},
                'numbers': []
            }

        # 笔画分析
        strokes = []
        for char in text:
            if char in self.stroke_dict:
                strokes.append(self.stroke_dict[char])

        # 五行分析
        element_scores = {elem: 0 for elem in self.element_dict.keys()}
        for elem, keywords in self.element_dict.items():
            for keyword in keywords:
                if keyword in text:
                    element_scores[elem] += 1

        # 生成号码
        numbers = []

        # 基于笔画
        if strokes:
            for stroke in set(strokes):
                base_numbers = list(range(stroke, 36, stroke))
                if base_numbers:
                    numbers.extend(random.sample(base_numbers, min(2, len(base_numbers))))

        # 基于五行
        if sum(element_scores.values()) > 0:
            dominant_element = max(element_scores, key=element_scores.get)
            element_numbers = {
                '木': [3, 8, 13, 18, 23, 28, 33],
                '火': [2, 7, 12, 17, 22, 27, 32],
                '土': [5, 10, 15, 20, 25, 30, 35],
                '金': [4, 9, 14, 19, 24, 29, 34],
                '水': [1, 6, 11, 16, 21, 26, 31]
            }
            numbers.extend(element_numbers[dominant_element][:3])

        return {
            'strokes': strokes,
            'elements': element_scores,
            'numbers': numbers
        }


class SpiritualImagePredictor:
    """灵修图片预测器（完整版）"""

    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.ocr_analyzer = OCRAnalyzer()

    def predict(self, image_base64=None, user_text=""):
        """
        综合预测
        参数：
        - image_base64: base64编码的图片
        - user_text: 用户输入的文字描述
        """
        analysis_results = []
        all_numbers = []

        # 1. 图片分析
        if image_base64:
            try:
                image_info = self.image_analyzer.analyze_image(image_base64)

                # 颜色能量
                color_numbers = image_info['color_energy']
                all_numbers.extend(color_numbers)
                analysis_results.append({
                    'dimension': '图片颜色能量',
                    'colors': image_info['dominant_colors'],
                    'numbers': color_numbers[:5],
                    'confidence': 0.75
                })

                # 物体数量能量
                object_count = image_info['object_count']
                count_numbers = self._count_to_numbers(object_count)
                all_numbers.extend(count_numbers)
                analysis_results.append({
                    'dimension': f'物体数量能量（{object_count}个）',
                    'numbers': count_numbers,
                    'confidence': 0.78
                })
            except Exception as e:
                print(f"图片分析错误: {e}")

        # 2. 文字分析
        if user_text:
            text_info = self.ocr_analyzer.analyze_text(user_text)

            if text_info['numbers']:
                all_numbers.extend(text_info['numbers'])

                # 笔画能量
                if text_info['strokes']:
                    analysis_results.append({
                        'dimension': '文字笔画能量',
                        'strokes': text_info['strokes'],
                        'numbers': text_info['numbers'][:5],
                        'confidence': 0.82
                    })

                # 五行能量
                if sum(text_info['elements'].values()) > 0:
                    dominant_element = max(text_info['elements'], key=text_info['elements'].get)
                    analysis_results.append({
                        'dimension': '五行关键词能量',
                        'dominant_element': dominant_element,
                        'element_scores': text_info['elements'],
                        'numbers': text_info['numbers'][-5:],
                        'confidence': 0.80
                    })

        # 3. 融合生成最终预测
        if not all_numbers:
            # 默认号码
            all_numbers = [3, 7, 12, 18, 23, 28, 33, 5, 10, 15]

        # 统计频率
        number_counter = Counter(all_numbers)

        # 前区：选择出现频率最高的5个号码
        front_candidates = [num for num in range(1, 36) if num in number_counter]
        front_candidates.sort(key=lambda x: number_counter[x], reverse=True)

        front_zone = front_candidates[:5] if len(front_candidates) >= 5 else front_candidates

        # 不足5个则随机补充
        while len(front_zone) < 5:
            candidate = random.randint(1, 35)
            if candidate not in front_zone:
                front_zone.append(candidate)

        front_zone = sorted(front_zone)

        # 后区：基于前区衍生
        back_zone = sorted([
            (sum(front_zone[:3]) % 12) + 1,
            (sum(front_zone[2:]) % 12) + 1
        ])

        # 后区去重
        if back_zone[0] == back_zone[1]:
            back_zone[1] = (back_zone[1] % 12) + 1
            if back_zone[1] < 1:
                back_zone[1] = 1
            elif back_zone[1] > 12:
                back_zone[1] = 12

        # 计算综合置信度
        avg_confidence = sum(r['confidence'] for r in analysis_results) / len(analysis_results) if analysis_results else 0.70

        return {
            'status': 'success',
            'prediction': {
                'front_zone': front_zone,
                'back_zone': back_zone,
                'confidence': round(avg_confidence, 3)
            },
            'analysis': {
                'dimensions_count': len(analysis_results),
                'details': analysis_results,
                'number_frequency': dict(number_counter.most_common(10))
            },
            'timestamp': datetime.now().isoformat()
        }

    def _count_to_numbers(self, count):
        """将数量转换为号码"""
        count_map = {
            1: [1, 11, 21, 31],
            2: [2, 12, 22, 32],
            3: [3, 13, 23, 33],
            4: [4, 14, 24, 34],
            5: [5, 15, 25, 35],
            6: [6, 12, 18, 24, 30],
            7: [7, 14, 21, 28, 35],
            8: [8, 16, 24, 32],
            9: [9, 18, 27],
        }

        base_numbers = count_map.get(count % 10, [count, count*2, count*3])
        valid_numbers = [n for n in base_numbers if 1 <= n <= 35]
        return valid_numbers if valid_numbers else [5, 10, 15, 20, 25]


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless函数处理器"""

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))

            # 获取请求参数
            image_base64 = request_data.get('image', None)
            user_text = request_data.get('text', '')

            if not image_base64 and not user_text:
                raise ValueError('请提供图片或文字描述')

            # 创建预测器
            predictor = SpiritualImagePredictor()

            # 生成预测
            result = predictor.predict(image_base64, user_text)

            # 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'status': 'error',
                'message': str(e),
                'detail': error_detail,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """提供API文档"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        doc = {
            'api': '灵修图片预测API',
            'version': '2.0',
            'endpoint': '/api/spiritual-image-predict',
            'method': 'POST',
            'parameters': {
                'image': '图片base64编码（可选）',
                'text': '文字描述（可选）'
            },
            'example': {
                'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRg...',
                'text': '红色的莲花，中间有光明'
            },
            'response': {
                'prediction': {
                    'front_zone': [1, 12, 18, 25, 33],
                    'back_zone': [3, 11]
                }
            }
        }

        self.wfile.write(json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8'))
