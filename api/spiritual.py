from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
import hashlib
import base64

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """GET请求 - 返回基础灵修因子（无上传内容）"""
        try:
            result = self._generate_spiritual_prediction(None, None)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error(str(e))
    
    def do_POST(self):
        """POST请求 - 接收图片/文字，生成个性化灵修预测"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            # 获取上传内容
            image_data = request_data.get('image', None)  # Base64编码的图片
            text_input = request_data.get('text', None)   # 灵修文字
            
            result = self._generate_spiritual_prediction(image_data, text_input)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error(str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_error(self, message):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {'status': 'error', 'message': message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def _generate_energy_seed(self, image_data, text_input):
        """根据上传内容生成能量种子"""
        seed_components = []
        
        # 时间因子
        now = datetime.now()
        time_factor = now.hour * 3600 + now.minute * 60 + now.second
        seed_components.append(str(time_factor))
        
        # 图片能量提取
        if image_data:
            # 从Base64图片数据提取能量签名
            try:
                # 取图片数据的哈希值
                img_hash = hashlib.md5(image_data.encode()).hexdigest()
                seed_components.append(img_hash[:16])
            except:
                seed_components.append("default_img")
        
        # 文字能量提取
        if text_input:
            # 文字内容哈希
            text_hash = hashlib.sha256(text_input.encode()).hexdigest()
            seed_components.append(text_hash[:16])
            
            # 提取文字中的数字（如果有）
            numbers_in_text = [int(c) for c in text_input if c.isdigit()]
            if numbers_in_text:
                seed_components.append(str(sum(numbers_in_text)))
        
        # 生成最终能量种子
        combined = "_".join(seed_components)
        final_seed = int(hashlib.md5(combined.encode()).hexdigest()[:8], 16)
        
        return final_seed, combined
    
    def _analyze_text_energy(self, text_input):
        """分析文字的能量属性"""
        if not text_input:
            return None
        
        # 五行关键词映射
        five_elements = {
            '金': ['金', '白', '秋', '西', '肺', '辛', '收', '坚', '刚', '锐'],
            '木': ['木', '青', '春', '东', '肝', '酸', '生', '仁', '直', '曲'],
            '水': ['水', '黑', '冬', '北', '肾', '咸', '藏', '智', '润', '下'],
            '火': ['火', '红', '夏', '南', '心', '苦', '长', '礼', '炎', '上'],
            '土': ['土', '黄', '中', '脾', '甘', '化', '信', '稳', '厚', '载']
        }
        
        # 情绪关键词
        emotions = {
            '平静': ['静', '安', '宁', '平', '淡', '定', '禅', '空'],
            '喜悦': ['喜', '乐', '欢', '笑', '开心', '快乐', '幸福'],
            '期待': ['望', '期', '盼', '愿', '希', '想', '梦'],
            '感恩': ['谢', '恩', '德', '福', '感激', '珍惜']
        }
        
        # 分析五行能量
        element_scores = {}
        for element, keywords in five_elements.items():
            score = sum(1 for kw in keywords if kw in text_input)
            if score > 0:
                element_scores[element] = score
        
        dominant_element = max(element_scores, key=element_scores.get) if element_scores else '土'
        
        # 分析情绪能量
        emotion_scores = {}
        for emotion, keywords in emotions.items():
            score = sum(1 for kw in keywords if kw in text_input)
            if score > 0:
                emotion_scores[emotion] = score
        
        dominant_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else '平静'
        
        return {
            'dominant_element': dominant_element,
            'element_scores': element_scores,
            'dominant_emotion': dominant_emotion,
            'emotion_scores': emotion_scores,
            'text_length': len(text_input),
            'has_numbers': any(c.isdigit() for c in text_input)
        }
    
    def _generate_spiritual_numbers(self, seed, text_analysis):
        """根据能量种子生成灵修预测号码"""
        random.seed(seed)
        
        # 基础号码池
        front_pool = list(range(1, 36))
        back_pool = list(range(1, 13))
        
        # 如果有文字分析，根据五行调整权重
        if text_analysis:
            element = text_analysis.get('dominant_element', '土')
            
            # 五行对应的幸运数字范围
            element_numbers = {
                '金': [4, 9, 14, 19, 24, 29, 34],  # 4, 9 属金
                '木': [3, 8, 13, 18, 23, 28, 33],  # 3, 8 属木
                '水': [1, 6, 11, 16, 21, 26, 31],  # 1, 6 属水
                '火': [2, 7, 12, 17, 22, 27, 32],  # 2, 7 属火
                '土': [5, 10, 15, 20, 25, 30, 35]  # 5, 10 属土
            }
            
            lucky_numbers = element_numbers.get(element, [])
            
            # 增加幸运数字的权重（重复添加到池中）
            for num in lucky_numbers:
                if num in front_pool:
                    front_pool.extend([num] * 2)
        
        # 随机选择前区5个号码
        front_zone = []
        temp_pool = front_pool.copy()
        for _ in range(5):
            num = random.choice(temp_pool)
            front_zone.append(num)
            temp_pool = [n for n in temp_pool if n != num]
        front_zone = sorted(list(set(front_zone)))
        
        # 确保有5个号码
        while len(front_zone) < 5:
            num = random.randint(1, 35)
            if num not in front_zone:
                front_zone.append(num)
        front_zone = sorted(front_zone[:5])
        
        # 随机选择后区2个号码
        back_zone = sorted(random.sample(back_pool, 2))
        
        # 计算置信度（基于能量强度）
        base_confidence = random.uniform(0.65, 0.85)
        if text_analysis:
            # 文字越长，能量越集中
            length_bonus = min(text_analysis['text_length'] / 100, 0.1)
            base_confidence += length_bonus
        
        return {
            'front_zone': front_zone,
            'back_zone': back_zone,
            'confidence': round(min(base_confidence, 0.95), 3)
        }
    
    def _generate_spiritual_prediction(self, image_data, text_input):
        """生成完整的灵修预测结果"""
        
        # 生成能量种子
        energy_seed, seed_signature = self._generate_energy_seed(image_data, text_input)
        
        # 分析文字能量
        text_analysis = self._analyze_text_energy(text_input) if text_input else None
        
        # 生成灵修预测号码
        spiritual_numbers = self._generate_spiritual_numbers(energy_seed, text_analysis)
        
        # 确定输入类型
        input_type = 'none'
        if image_data and text_input:
            input_type = 'image_and_text'
        elif image_data:
            input_type = 'image_only'
        elif text_input:
            input_type = 'text_only'
        
        # 灵修图像描述
        spiritual_images = [
            {'name': '莲花冥想', 'meaning': '纯净与觉醒，心灵澄澈'},
            {'name': '高山禅境', 'meaning': '稳定与高远，志向坚定'},
            {'name': '海浪律动', 'meaning': '流动与变化，顺势而为'},
            {'name': '森林宁静', 'meaning': '自然与和谐，生生不息'},
            {'name': '夕阳脉轮', 'meaning': '能量与平衡，身心合一'}
        ]
        
        random.seed(energy_seed)
        selected_image = random.choice(spiritual_images)
        
        # 生成灵修指导语
        mantras = [
            '心静自然凉，数字自然来',
            '随缘不变，不变随缘',
            '一念清净，万象皆空',
            '顺应天时，感应地气',
            '心诚则灵，意到则成'
        ]
        
        # 能量因子
        chaos_factor = round(random.uniform(0.1, 0.9), 3)
        harmony_factor = round(random.uniform(0.1, 0.9), 3)
        cosmic_alignment = round(random.uniform(0.3, 1.0), 3)
        
        energy_levels = ['极高', '高', '中等', '低']
        energy_level = random.choice(energy_levels)
        
        result = {
            'status': 'success',
            'input_received': {
                'type': input_type,
                'has_image': image_data is not None,
                'has_text': text_input is not None,
                'text_preview': text_input[:50] + '...' if text_input and len(text_input) > 50 else text_input
            },
            'energy_analysis': {
                'seed': energy_seed,
                'signature': seed_signature[:32] + '...' if len(seed_signature) > 32 else seed_signature,
                'text_analysis': text_analysis
            },
            'spiritual_prediction': {
                'front_zone': spiritual_numbers['front_zone'],
                'back_zone': spiritual_numbers['back_zone'],
                'confidence': spiritual_numbers['confidence'],
                'prediction_type': '灵修直觉预测'
            },
            'spiritual_factors': {
                'chaos_factor': chaos_factor,
                'harmony_factor': harmony_factor,
                'cosmic_alignment': cosmic_alignment,
                'energy_level': energy_level,
                'overall_intensity': round((chaos_factor + harmony_factor + cosmic_alignment) / 3, 3)
            },
            'spiritual_image': {
                'name': selected_image['name'],
                'meaning': selected_image['meaning']
            },
            'guidance': {
                'mantra': random.choice(mantras),
                'meditation_time': f'{random.randint(5, 20)}分钟',
                'best_time': f'{random.randint(5, 9)}:00 - {random.randint(9, 12)}:00',
                'element_advice': f"今日宜{text_analysis['dominant_element'] if text_analysis else '静心'}，顺应自然规律"
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return result
