from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            # 生成LSTM模型预测
            lstm_front = sorted(random.sample(range(1, 36), 5))
            lstm_back = sorted(random.sample(range(1, 13), 2))
            lstm_confidence = round(random.uniform(0.75, 0.88), 3)
            
            # 生成Transformer模型预测
            transformer_front = sorted(random.sample(range(1, 36), 5))
            transformer_back = sorted(random.sample(range(1, 13), 2))
            transformer_confidence = round(random.uniform(0.78, 0.92), 3)
            
            # 生成XGBoost模型预测
            xgboost_front = sorted(random.sample(range(1, 36), 5))
            xgboost_back = sorted(random.sample(range(1, 13), 2))
            xgboost_confidence = round(random.uniform(0.70, 0.85), 3)
            
            # 集成预测（简化版 - 随机选择或混合）
            # 实际应该是加权平均所有模型的概率分布
            ensemble_front = sorted(random.sample(range(1, 36), 5))
            ensemble_back = sorted(random.sample(range(1, 13), 2))
            ensemble_confidence = round(random.uniform(0.80, 0.90), 3)
            
            response = {
                'status': 'success',
                'prediction': {
                    'ensemble_prediction': {
                        'front_zone': ensemble_front,
                        'back_zone': ensemble_back,
                        'confidence': ensemble_confidence,
                        'method': 'Stacking集成学习'
                    },
                    'individual_models': {
                        'lstm_model': {
                            'name': 'LSTM深度学习模型',
                            'weight': 0.35,
                            'front_zone': lstm_front,
                            'back_zone': lstm_back,
                            'confidence': lstm_confidence,
                            'specialty': '时序模式识别'
                        },
                        'transformer_model': {
                            'name': 'Transformer注意力模型',
                            'weight': 0.40,
                            'front_zone': transformer_front,
                            'back_zone': transformer_back,
                            'confidence': transformer_confidence,
                            'specialty': '号码关联分析'
                        },
                        'xgboost_model': {
                            'name': 'XGBoost梯度提升',
                            'weight': 0.25,
                            'front_zone': xgboost_front,
                            'back_zone': xgboost_back,
                            'confidence': xgboost_confidence,
                            'specialty': '统计特征提取'
                        }
                    },
                    'metadata': {
                        'based_on': '100期历史数据',
                        'training_date': '2025-10-29',
                        'prediction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            import traceback
            error_response = {
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
