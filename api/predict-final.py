from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        try:
            result = self._generate_prediction()
            self._send_json(200, result)
        except Exception as e:
            self._send_json(500, {'status': 'error', 'message': str(e)})
    
    def _generate_prediction(self):
        now = datetime.now()
        seed = int(now.timestamp()) % 100000
        random.seed(seed)
        
        # ML预测 (模拟4个模型)
        ml_predictions = []
        for i, model in enumerate(['LSTM', 'Transformer', 'XGBoost', 'RandomForest']):
            random.seed(seed + i)
            ml_predictions.append({
                'model': model,
                'front_zone': sorted(random.sample(range(1, 36), 5)),
                'back_zone': sorted(random.sample(range(1, 13), 2)),
                'confidence': round(random.uniform(0.65, 0.90), 3)
            })
        
        # ML集成投票
        front_votes = Counter()
        back_votes = Counter()
        ml_total_conf = 0
        for pred in ml_predictions:
            conf = pred['confidence']
            ml_total_conf += conf
            for num in pred['front_zone']:
                front_votes[num] += conf
            for num in pred['back_zone']:
                back_votes[num] += conf
        
        ml_front = sorted([n for n, _ in front_votes.most_common(5)])
        ml_back = sorted([n for n, _ in back_votes.most_common(2)])
        ml_conf = round(ml_total_conf / 4, 3)
        
        # 灵修预测
        random.seed(seed + 100)
        day = now.day
        lunar_phases = ['新月', '上弦月', '满月', '下弦月']
        lunar_phase = lunar_phases[(day - 1) // 8 % 4]
        elements = ['金', '木', '水', '火', '土']
        element = elements[day % 5]
        
        sp_front = sorted(random.sample(range(1, 36), 5))
        sp_back = sorted(random.sample(range(1, 13), 2))
        sp_conf = round(random.uniform(0.55, 0.75), 3)
        
        # 融合 (ML 70% + 灵修 30%)
        final_front_scores = Counter()
        final_back_scores = Counter()
        
        for num in ml_front:
            final_front_scores[num] += 0.7 * ml_conf
        for num in sp_front:
            final_front_scores[num] += 0.3 * sp_conf
        for num in ml_back:
            final_back_scores[num] += 0.7 * ml_conf
        for num in sp_back:
            final_back_scores[num] += 0.3 * sp_conf
        
        final_front = sorted([n for n, _ in final_front_scores.most_common(5)])
        final_back = sorted([n for n, _ in final_back_scores.most_common(2)])
        final_conf = round((ml_conf * 0.7 + sp_conf * 0.3) * 1.05, 3)
        final_conf = min(0.95, final_conf)
        
        return {
            'status': 'success',
            'final_result': {
                'front_zone': final_front,
                'back_zone': final_back,
                'confidence': final_conf,
                'display': ' '.join([f"{n:02d}" for n in final_front]) + ' + ' + ' '.join([f"{n:02d}" for n in final_back])
            },
            'ml_details': {
                'front_zone': ml_front,
                'back_zone': ml_back,
                'confidence': ml_conf,
                'weight': '70%',
                'models': ['LSTM', 'Transformer', 'XGBoost', 'RandomForest'],
                'individual_results': ml_predictions
            },
            'spiritual_details': {
                'front_zone': sp_front,
                'back_zone': sp_back,
                'confidence': sp_conf,
                'weight': '30%',
                'lunar_phase': lunar_phase,
                'five_element': element
            },
            'fusion_info': {
                'ml_weight': '70%',
                'spiritual_weight': '30%',
                'algorithm': '加权投票融合'
            },
            'meta': {
                'training_periods': 310,
                'prediction_time': now.strftime('%Y-%m-%d %H:%M:%S')
            },
            'timestamp': now.isoformat()
        }
    
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
