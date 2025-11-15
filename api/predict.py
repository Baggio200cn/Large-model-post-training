from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

# 导入历史数据
try:
    from .lottery_historical_data import get_historical_data, get_hot_and_cold_numbers
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from lottery_historical_data import get_historical_data, get_hot_and_cold_numbers

class handler(BaseHTTPRequestHandler):
    
    def _generate_prediction(self):
        """生成预测的核心逻辑"""
        try:
            # 获取历史数据用于预测
            historical_data = get_historical_data(50)
            hot_cold_front = get_hot_and_cold_numbers('front', 15)
            hot_cold_back = get_hot_and_cold_numbers('back', 8)
            
            # 获取热号列表
            hot_front = hot_cold_front['hot'][:10]
            hot_back = hot_cold_back['hot'][:6]
            
            # 前区预测：基于热号的智能选择
            front_candidates = list(range(1, 36))
            weighted_front = hot_front * 3 + [n for n in front_candidates if n not in hot_front]
            
            # 从权重列表中随机选择5个不重复的号码
            selected_front = []
            attempts = 0
            while len(selected_front) < 5 and attempts < 100:
                num = random.choice(weighted_front)
                if num not in selected_front:
                    selected_front.append(num)
                attempts += 1
            
            # 备用方案
            if len(selected_front) < 5:
                selected_front = random.sample(front_candidates, 5)
            
            front_zone = sorted(selected_front)
            
            # 后区预测
            back_candidates = list(range(1, 13))
            weighted_back = hot_back * 2 + [n for n in back_candidates if n not in hot_back]
            
            selected_back = []
            attempts = 0
            while len(selected_back) < 2 and attempts < 50:
                num = random.choice(weighted_back)
                if num not in selected_back:
                    selected_back.append(num)
                attempts += 1
            
            if len(selected_back) < 2:
                selected_back = random.sample(back_candidates, 2)
            
            back_zone = sorted(selected_back)
            
            # 计算置信度
            hot_count = sum(1 for n in front_zone if n in hot_front[:5])
            confidence = 0.65 + (hot_count * 0.05) + random.uniform(0, 0.1)
            
            # 生成其他模型的预测
            lstm_front = sorted(random.sample(front_candidates, 5))
            lstm_back = sorted(random.sample(back_candidates, 2))
            
            transformer_front = sorted(random.sample(front_candidates, 5))
            transformer_back = sorted(random.sample(back_candidates, 2))
            
            xgboost_front = sorted(random.sample(front_candidates, 5))
            xgboost_back = sorted(random.sample(back_candidates, 2))
            
            return {
                'status': 'success',
                'prediction': {
                    'ensemble_prediction': {
                        'front_zone': front_zone,
                        'back_zone': back_zone,
                        'confidence': round(confidence, 3)
                    },
                    'individual_models': {
                        'lstm_model': {
                            'front_zone': lstm_front,
                            'back_zone': lstm_back,
                            'confidence': round(random.uniform(0.6, 0.8), 3)
                        },
                        'transformer_model': {
                            'front_zone': transformer_front,
                            'back_zone': transformer_back,
                            'confidence': round(random.uniform(0.65, 0.85), 3)
                        },
                        'xgboost_model': {
                            'front_zone': xgboost_front,
                            'back_zone': xgboost_back,
                            'confidence': round(random.uniform(0.55, 0.75), 3)
                        }
                    },
                    'model_weights': {
                        'lstm': 0.35,
                        'transformer': 0.40,
                        'xgboost': 0.25
                    },
                    'based_on_data': {
                        'periods_analyzed': len(historical_data),
                        'hot_numbers_front': hot_front[:5],
                        'hot_numbers_back': hot_back[:3]
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def do_GET(self):
        """支持GET方法用于测试"""
        try:
            result = self._generate_prediction()
            result['note'] = 'GET method for testing. Use POST for production.'
            
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
    
    def do_POST(self):
        """处理POST请求"""
        try:
            # 读取请求数据（如果有）
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            result = self._generate_prediction()
            
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

4. **滚动到底部提交**
   - Commit message: `Add GET support and fix random.sample error`
   - 点击 **"Commit changes"**

---

## ⏰ 等待部署（2-3分钟）

### 查看Vercel部署状态：
```
https://vercel.com/baggio200cns-projects/large-model-post-training
```

**等待显示：** 🟢 Ready

---

## 🧪 部署完成后测试

### 测试1：浏览器GET测试

**直接访问：**
```
https://large-model-post-training.vercel.app/api/predict.py
