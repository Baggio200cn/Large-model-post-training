"""灵修API - 简化版（向后兼容）"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 简化版灵修响应（不需要上传图片/文字）
            time_seed = int(datetime.now().timestamp()) % 10000
            random.seed(time_seed)
            
            spiritual_images = [
                'lotus_meditation.jpg',
                'mountain_zen.jpg', 
                'ocean_waves.jpg',
                'forest_tranquility.jpg',
                'sunset_chakra.jpg'
            ]
            
            selected_image = random.choice(spiritual_images)
            descriptions = {
                'lotus_meditation.jpg': '莲花冥想图，象征纯净与觉醒',
                'mountain_zen.jpg': '高山禅境图，代表稳定与高远',
                'ocean_waves.jpg': '海浪律动图，体现流动与变化',
                'forest_tranquility.jpg': '森林宁静图，传递自然与和谐',
                'sunset_chakra.jpg': '夕阳脉轮图，展现能量与平衡'
            }
            
            response = {
                'status': 'success',
                'message': '这是简化版灵修API，完整功能请使用 /api/spiritual-upload 和 /api/spiritual-predict',
                'spiritual_perturbation': {
                    'spiritual_image': {
                        'filename': selected_image,
                        'description': descriptions.get(selected_image, '神秘灵修图像')
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
                            '一切皆有可能',
                            '安住当下，自在如光'
                        ])
                    }
                },
                'energy_reading': {
                    'cosmic_energy': f'{random.randint(60, 95)}%',
                    'earth_energy': f'{random.randint(50, 90)}%',
                    'personal_energy': f'{random.randint(70, 100)}%'
                },
                'upgrade_tip': '💡 使用新版灵修系统获得更精准的预测：上传您的灵修图片和文字到 /spiritual.html',
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
        # POST请求也支持
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

---

## 🎯 更新后的系统架构
```
灵修系统 API 层级：

Level 1 - 快速接口（旧版兼容）
├── /api/spiritual              # 简化版，随机灵修因子
    └── 用途：主页快速测试

Level 2 - 完整系统（新版）
├── /api/spiritual-upload       # 上传图片+文字
├── /api/spiritual-predict      # 生成灵修预测
└── /api/predict-final          # ML+灵修融合
    └── 用途：/spiritual.html 专用页面
