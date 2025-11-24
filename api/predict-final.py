from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class PredictionMerger:
    def __init__(self, ml_weight=0.7, spiritual_weight=0.3):
        self.ml_weight = ml_weight
        self.spiritual_weight = spiritual_weight
    
    def merge_predictions(self, ml_predictions, spiritual_prediction):
        merged_predictions = []
        
        for idx, ml_pred in enumerate(ml_predictions):
            ml_front = set(ml_pred['front_zone'])
            ml_back = set(ml_pred['back_zone'])
            
            sp_front = set(spiritual_prediction['front_zone'])
            sp_back = set(spiritual_prediction['back_zone'])
            
            overlap_front = len(ml_front & sp_front)
            overlap_back = len(ml_back & sp_back)
            
            final_front = list(ml_front & sp_front)
            
            ml_count = int((5 - len(final_front)) * self.ml_weight)
            final_front.extend(list(ml_front - sp_front)[:ml_count])
            
            remaining_needed = 5 - len(final_front)
            final_front.extend(list(sp_front - ml_front)[:remaining_needed])
            
            final_back = list(ml_back & sp_back)
            if len(final_back) < 2:
                ml_back_list = list(ml_back - sp_back)
                sp_back_list = list(sp_back - ml_back)
                combined = ml_back_list + sp_back_list
                final_back.extend(combined[:(2 - len(final_back))])
            
            original_confidence = ml_pred['confidence']
            overlap_bonus = (overlap_front * 0.03) + (overlap_back * 0.03)
            final_confidence = min(original_confidence + overlap_bonus, 0.95)
            
            merged_pred = {
                'group': idx + 1,
                'strategy': ml_pred.get('strategy', '未知策略') + ' + 灵修',
                'front_zone': sorted(final_front[:5]),
                'back_zone': sorted(final_back[:2]),
                'confidence': round(final_confidence, 2),
                'fusion_info': {
                    'ml_weight': self.ml_weight,
                    'spiritual_weight': self.spiritual_weight,
                    'overlap_count': overlap_front + overlap_back,
                    'overlap_bonus': round(overlap_bonus, 2)
                }
            }
            
            merged_predictions.append(merged_pred)
        
        return merged_predictions

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            ml_predictions = request_data.get('ml_predictions', [])
            spiritual_prediction = request_data.get('spiritual_prediction', {})
            ml_weight = request_data.get('ml_weight', 0.7)
            spiritual_weight = request_data.get('spiritual_weight', 0.3)
            
            if not ml_predictions:
                raise ValueError('缺少ML预测数据')
            if not spiritual_prediction:
                raise ValueError('缺少灵修预测数据')
            
            merger = PredictionMerger(ml_weight, spiritual_weight)
            final_predictions = merger.merge_predictions(ml_predictions, spiritual_prediction)
            
            response = {
                'status': 'success',
                'final_predictions': final_predictions,
                'fusion_params': {
                    'ml_weight': ml_weight,
                    'spiritual_weight': spiritual_weight,
                    'total_groups': len(final_predictions)
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
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
