"""预测API - 主要endpoint"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 尝试从数据库加载，如果失败则使用本地数据
try:
    from _db import get_all_lottery_data
    USE_DATABASE = True
except:
    from _lottery_data import LOTTERY_HISTORY
    USE_DATABASE = False

from _ml_predictor import MLPredictor

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 获取数据
            if USE_DATABASE:
                lottery_data = get_all_lottery_data()
                if not lottery_data or len(lottery_data) == 0:
                    lottery_data = []
                    data_source = 'Database (empty - using fallback)'
                else:
                    data_source = f'MongoDB ({len(lottery_data)} periods)'
            else:
                lottery_data = LOTTERY_HISTORY
                data_source = f'Local file ({len(lottery_data)} periods)'
            
            if not lottery_data or len(lottery_data) < 10:
                raise Exception(f"历史数据不足（需要至少10期，当前{len(lottery_data)}期）")
            
            # 创建预测器
            predictor = MLPredictor(lottery_data)
            features = predictor.features
            predictions = predictor.generate_predictions(5)
            
            # 构建响应
            response = {
                'status': 'success',
                'prediction': {
                    'all_predictions': predictions,
                    'ensemble_prediction': predictions[0],
                    'based_on_data': {
                        'periods_analyzed': len(lottery_data),
                        'data_range': f"{lottery_data[0]['period']}-{lottery_data[-1]['period']}",
                        'data_source': data_source,
                        'hot_numbers_front': features['front_hot'],
                        'hot_numbers_back': features['back_hot'],
                        'cold_numbers_front': features['front_cold'],
                        'cold_numbers_back': features['back_cold'],
                        'front_odd_ratio': round(features['front_odd_ratio'], 3),
                        'front_sum_mean': round(features['front_sum_mean'], 2),
                        'front_span_mean': round(features['front_span_mean'], 2)
                    }
                },
                'ml_info': {
                    'model_type': 'Statistical ML with Feature Engineering',
                    'features_used': [
                        'Frequency Analysis',
                        'Missing Value Tracking',
                        'Odd-Even Ratio',
                        'Sum Value Trend',
                        'Span Analysis',
                        'Pattern Recognition'
                    ],
                    'strategies': [p['strategy'] for p in predictions]
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
            error_response = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        self.do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
