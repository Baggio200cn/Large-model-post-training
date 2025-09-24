from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
import math

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 基于时间和宇宙因子的复合随机种子
            time_seed = int(datetime.now().timestamp()) % 10000
            cosmic_seed = self._calculate_cosmic_influence()
            combined_seed = (time_seed + cosmic_seed) % 99991
            random.seed(combined_seed)
            
            # 生成灵修扰动数据
            spiritual_data = self._generate_spiritual_perturbation()
            
            response = {
                'status': 'success',
                'spiritual_perturbation': spiritual_data,
                'cosmic_metadata': {
                    'calculation_time': datetime.now().isoformat(),
                    'cosmic_seed': cosmic_seed,
                    'lunar_phase': self._get_lunar_phase(),
                    'energy_signature': self._generate_energy_signature()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _calculate_cosmic_influence(self):
        """计算宇宙影响因子"""
        now = datetime.now()
        
        # 基于时间的多重因子
        hour_factor = now.hour * 127
        minute_factor = now.minute * 61
        day_factor = now.day * 31
        month_factor = now.month * 12
        
        # 星座影响（简化版黄道12宫）
        zodiac_factor = (now.month * 30 + now.day) % 360
        
        # 五行影响（基于年份）
        wuxing_factor = now.year % 5 * 73
        
        cosmic_influence = (
            hour_factor + minute_factor + day_factor + 
            month_factor + zodiac_factor + wuxing_factor
        ) % 10000
        
        return cosmic_influence
    
    def _get_lunar_phase(self):
        """获取月相信息（简化计算）"""
        now = datetime.now()
        # 简化的月相计算，基于日期的周期性
        lunar_cycle = (now.day % 28) / 28.0
        
        if lunar_cycle < 0.125:
            return {"phase": "新月", "energy": "新生", "influence": 0.2}
        elif lunar_cycle < 0.375:
            return {"phase": "上弦月", "energy": "成长", "influence": 0.6}
        elif lunar_cycle < 0.625:
            return {"phase": "满月", "energy": "圆满", "influence": 1.0}
        elif lunar_cycle < 0.875:
            return {"phase": "下弦月", "energy": "释放", "influence": 0.4}
        else:
            return {"phase": "残月", "energy": "净化", "influence": 0.1}
    
    def _generate_energy_signature(self):
        """生成能量签名"""
        now = datetime.now()
        signature_base = f"{now.year}{now.month:02d}{now.day:02d}{now.hour:02d}"
        
        # 转换为能量数值
        energy_sum = sum(int(digit) for digit in signature_base)
        energy_signature = f"EN{energy_sum:04d}_{now.hour:02d}{now.minute:02d}"
        
        return energy_signature
    
    def _generate_spiritual_perturbation(self):
        """生成灵修扰动数据"""
        # 选择灵修图像
        spiritual_images = [
            {
                'filename': 'lotus_meditation.jpg',
                'description': '莲花冥想图，象征纯净与觉醒',
                'element': '水',
                'chakra': '顶轮',
                'energy_type': '净化'
            },
            {
                'filename': 'mountain_zen.jpg',
                'description': '高山禅境图，代表稳定与高远',
                'element': '土',
                'chakra': '根轮',
                'energy_type': '稳定'
            },
            {
                'filename': 'ocean_waves.jpg',
                'description': '海浪律动图，体现流动与变化',
                'element': '水',
                'chakra': '性轮',
                'energy_type': '流动'
            },
            {
                'filename': 'forest_tranquility.jpg',
                'description': '森林宁静图，传递自然与和谐',
                'element': '木',
                'chakra': '心轮',
                'energy_type': '和谐'
            },
            {
                'filename': 'sunset_chakra.jpg',
                'description': '夕阳脉轮图，展现能量与平衡',
                'element': '火',
                'chakra': '太阳轮',
                'energy_type': '激活'
            },
            {
                'filename': 'crystal_meditation.jpg',
                'description': '水晶冥想图，聚焦意识与直觉',
                'element': '金',
                'chakra': '眉心轮',
                'energy_type': '聚焦'
            }
        ]
        
        selected_image = random.choice(spiritual_images)
        
        # 生成扰动因子
        chaos_factor = self._generate_chaos_factor()
        harmony_factor = self._generate_harmony_factor()
        cosmic_alignment = self._generate_cosmic_alignment()
        
        # 计算总体强度
        overall_intensity = (chaos_factor + harmony_factor + cosmic_alignment) / 3
        
        # 生成能量读数
        energy_reading = self._generate_energy_reading()
        
        # 生成灵修指引
        spiritual_guidance = self._generate_spiritual_guidance(selected_image)
        
        return {
            'spiritual_image': selected_image,
            'perturbation_factors': {
                'chaos_factor': round(chaos_factor, 3),
                'harmony_factor': round(harmony_factor, 3),
                'energy_level': self._categorize_energy_level(overall_intensity),
                'cosmic_alignment': round(cosmic_alignment, 3),
                'elemental_influence': selected_image['element'],
                'chakra_resonance': selected_image['chakra']
            },
            'overall_intensity': round(overall_intensity, 3),
            'energy_reading': energy_reading,
            'spiritual_guidance': spiritual_guidance,
            'manifestation_window': self._calculate_manifestation_window(),
            'recommended_actions': self._generate_recommended_actions(selected_image)
        }
    
    def _generate_chaos_factor(self):
        """生成混沌因子"""
        now = datetime.now()
        
        # 基于时间的混沌性
        time_chaos = (now.microsecond % 1000) / 1000.0
        
        # 加入一些数学混沌
        x = (now.hour * now.minute + now.second) / 100.0
        mathematical_chaos = abs(math.sin(x) * math.cos(x * 1.7))
        
        # 组合混沌因子
        chaos_factor = (time_chaos * 0.6 + mathematical_chaos * 0.4)
        return min(0.9, max(0.1, chaos_factor))
    
    def _generate_harmony_factor(self):
        """生成和谐因子"""
        now = datetime.now()
        
        # 基于黄金比例的和谐性
        golden_ratio = 1.618
        harmony_base = (now.day + now.hour) / golden_ratio
        harmony_factor = (harmony_base % 1) * 0.8 + 0.2
        
        return min(0.9, max(0.1, harmony_factor))
    
    def _generate_cosmic_alignment(self):
        """生成宇宙调谐因子"""
        now = datetime.now()
        
        # 模拟行星对齐影响
        day_of_year = now.timetuple().tm_yday
        cosmic_cycle = math.sin(2 * math.pi * day_of_year / 365.25)
        
        # 加入时间因子
        time_factor = math.cos(2 * math.pi * now.hour / 24)
        
        # 组合宇宙因子
        alignment = (cosmic_cycle + time_factor + 2) / 4  # 归一化到0-1
        return min(1.0, max(0.0, alignment))
    
    def _categorize_energy_level(self, intensity):
        """分类能量等级"""
        if intensity >= 0.8:
            return "极高"
        elif intensity >= 0.6:
            return "高"
        elif intensity >= 0.4:
            return "中等"
        elif intensity >= 0.2:
            return "低"
        else:
            return "极低"
    
    def _generate_energy_reading(self):
        """生成能量读数"""
        lunar_phase = self._get_lunar_phase()
        lunar_influence = lunar_phase['influence']
        
        return {
            'cosmic_energy': f"{random.randint(60, 95)}%",
            'earth_energy': f"{random.randint(50, 90)}%",
            'personal_energy': f"{random.randint(70, 100)}%",
            'lunar_energy': f"{int(lunar_influence * 100)}%",
            'elemental_energy': f"{random.randint(55, 85)}%"
        }
    
    def _generate_spiritual_guidance(self, selected_image):
        """生成灵修指引"""
        mantras = {
            '水': ['愿智慧如水般流淌', '净化心灵，洗涤尘埃', '流水不腐，心境常新'],
            '土': ['稳如磐石，心安如山', '脚踏实地，仰望星空', '大地之母，滋养万物'],
            '木': ['生机勃勃，向阳而生', '根深叶茂，心怀慈悲', '春风化雨，润物无声'],
            '火': ['光明照耀，温暖人心', '热情如火，照亮前路', '凤凰涅槃，浴火重生'],
            '金': ['明心见性，直指本心', '金刚不坏，智慧如镜', '洞察秋毫，明辨是非']
        }
        
        element = selected_image['element']
        selected_mantras = mantras.get(element, ['愿智慧照亮前路'])
        
        meditation_times = ['5分钟', '10分钟', '15分钟', '20分钟', '30分钟']
        
        return {
            'meditation_time': random.choice(meditation_times),
            'recommended_mantra': random.choice(selected_mantras),
            'chakra_focus': selected_image['chakra'],
            'breathing_pattern': self._generate_breathing_pattern(),
            'visualization': f"专注于{selected_image['description']}的意象"
        }
    
    def _generate_breathing_pattern(self):
        """生成呼吸模式"""
        patterns = [
            "4-7-8呼吸法（吸气4秒，屏息7秒，呼气8秒）",
            "方形呼吸法（吸气4秒，屏息4秒，呼气4秒，屏息4秒）",
            "自然呼吸法（随呼吸的自然节奏，保持觉知）",
            "深度腹式呼吸（缓慢深呼吸，专注腹部起伏）",
            "交替鼻孔呼吸（左右鼻孔交替呼吸，平衡能量）"
        ]
        return random.choice(patterns)
    
    def _calculate_manifestation_window(self):
        """计算显化时间窗口"""
        lunar_phase = self._get_lunar_phase()
        
        if lunar_phase['phase'] == '新月':
            return {'period': '新月后3-7天', 'quality': '新开始的最佳时机'}
        elif lunar_phase['phase'] == '上弦月':
            return {'period': '上弦月期间', 'quality': '积累能量，稳步前进'}
        elif lunar_phase['phase'] == '满月':
            return {'period': '满月前后3天', 'quality': '能量最强，显化最佳'}
        elif lunar_phase['phase'] == '下弦月':
            return {'period': '下弦月期间', 'quality': '释放阻碍，清理旧有'}
        else:
            return {'period': '残月期间', 'quality': '内省净化，准备新周期'}
    
    def _generate_recommended_actions(self, selected_image):
        """生成推荐行动"""
        element = selected_image['element']
        energy_type = selected_image['energy_type']
        
        actions_by_element = {
            '水': ['喝足够的水', '在水边冥想', '洗个舒缓的热水澡', '听流水声'],
            '土': ['赤脚接触大地', '园艺活动', '山地徒步', '稳定作息'],
            '木': ['拥抱树木', '森林浴', '种植绿植', '早起迎朝阳'],
            '火': ['观看日出日落', '点燃蜡烛冥想', '适度运动', '激发创造力'],
            '金': ['整理环境', '练习正念', '佩戴水晶', '专注呼吸']
        }
        
        base_actions = actions_by_element.get(element, ['保持正念', '深呼吸'])
        selected_actions = random.sample(base_actions, min(3, len(base_actions)))
        
        return {
            'immediate_actions': selected_actions,
            'daily_practice': f'每日进行{selected_image["chakra"]}能量冥想',
            'weekly_ritual': f'每周进行一次{element}元素净化仪式',
            'avoid_activities': ['负面思考', '过度焦虑', '熬夜晚睡']
        }
    
    def _send_error_response(self, error_message):
        """发送错误响应"""
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'status': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat(),
            'error_code': 'SPIRITUAL_CALCULATION_FAILED'
        }
        
        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
