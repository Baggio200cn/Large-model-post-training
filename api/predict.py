from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from lottery_historical_data import LOTTERY_HISTORY
from ml_predictor import MLPredictor

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            predictor = MLPredictor(LOTTERY_HISTORY)
            features = predictor.features
            predictions = predictor.generate_predictions(5)
            
            response = {
                'status': 'success',
                'prediction': {
                    'all_predictions': predictions,
                    'ensemble_prediction': predictions[0],
                    'based_on_data': {
                        'periods_analyzed': len(LOTTERY_HISTORY),
                        'data_range': f"{LOTTERY_HISTORY[0]['period']}-{LOTTERY_HISTORY[-1]['period']}",
                        'data_source': 'Real historical lottery data with ML analysis',
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
