"""融合预测API - ML + 灵修"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

class PredictionMerger:
    """预测融合器"""
    
    def __init__(self, ml_weight=0.7, spiritual_weight=0.3):
        self.ml_weight = ml_weight
        self.spiritual_weight = spiritual_weight
    
    def merge_predictions(self, ml_predictions, spiritual_prediction):
        """融合ML预测和灵修预测"""
        
        if not ml_predictions or not spiritual_prediction:
            raise Exception('需要ML预测和灵修预测数据')
        
        spiritual_front = set(spiritual_prediction['front_zone'])
        spiritual_back = set(spiritual_prediction['back_zone'])
        spiritual_conf = spiritual_prediction.get('confidence', 0.75)
        
        final_predictions = []
        
        for i, ml_pred in enumerate(ml_predictions):
            ml_front = set(ml_pred['front_zone'])
            ml_back = set(ml_pred['back_zone'])
            ml_conf = ml_pred.get('confidence', 0.75)
            
            # 计算重叠度
            front_overlap = ml_front & spiritual_front
            back_overlap = ml_back & spiritual_back
            
            overlap_count = len(front_overlap) + len(back_overlap)
            
            # 融合前区号码
            final_front = list(front_overlap)  # 先加重叠的
            
            # 按权重补充
            ml_only = list(ml_front - spiritual_front)
            spiritual_only = list(spiritual_front - ml_front)
            
            needed = 5 - len(final_front)
            ml_count = int(needed * self.ml_weight)
            spiritual_count = needed - ml_count
            
            final_front.extend(ml_only[:ml_count])
            final_front.extend(spiritual_only[:spiritual_count])
            
            # 如果还不够5个，随机补充
            while len(final_front) < 5:
                all_candidates = list((ml_front | spiritual_front) - set(final_front))
                if all_candidates:
                    final_front.append(random.choice(all_candidates))
                else:
                    final_front.append(random.randint(1, 35))
            
            final_front = sorted(final_front[:5])
            
            # 融合后区号码
            if back_overlap:
                final_back = list(back_overlap)
            else:
                final_back = [ml_back.pop() if ml_back else random.randint(1, 12)]
            
            while len(final_back) < 2:
                candidates = list((ml_back | spiritual_back) - set(final_back))
                if candidates:
                    final_back.append(random.choice(list(candidates)))
                else:
                    final_back.append(random.randint(1, 12))
            
            final_back = sorted(final_back[:2])
            
            # 计算融合后的置信度
            base_confidence = ml_conf * self.ml_weight + spiritual_conf * self.spiritual_weight
            overlap_bonus = overlap_count * 0.03  # 每个重叠号码+3%
            final_confidence = min(base_confidence + overlap_bonus, 0.95)
            
            final_predictions.append({
                'group': i + 1,
                'strategy': ml_pred.get('strategy', '融合策略') + ' + 灵修',
                'front_zone': final_front,
                'back_zone': final_back,
                'confidence': round(final_confidence, 3),
                'fusion_info': {
                    'ml_weight': self.ml_weight,
                    'spiritual_weight': self.spiritual_weight,
                    'overlap_count': overlap_count,
                    'overlap_bonus': round(overlap_bonus, 3)
                }
            })
        
        return final_predictions

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 接收ML预测和灵修预测
            ml_predictions = request_data.get('ml_predictions', [])
            spiritual_prediction = request_data.get('spiritual_prediction', {})
            
            # 权重配置（可自定义）
            ml_weight = request_data.get('ml_weight', 0.7)
            spiritual_weight = request_data.get('spiritual_weight', 0.3)
            
            # 创建融合器
            merger = PredictionMerger(ml_weight, spiritual_weight)
            
            # 融合预测
            final_predictions = merger.merge_predictions(ml_predictions, spiritual_prediction)
            
            response = {
                'status': 'success',
                'final_predictions': final_predictions,
                'fusion_config': {
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
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
