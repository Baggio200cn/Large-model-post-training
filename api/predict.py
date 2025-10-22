"""
预测API
提供彩票号码预测功能
"""

from http.server import BaseHTTPRequestHandler
import json
import pickle
import os


class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 加载模型
            model_path = 'data/models/frequency_model.pkl'
            
            if not os.path.exists(model_path):
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    'success': False,
                    'error': '模型未训练',
                    'message': '请先运行训练脚本: python scripts/train_simple_model.py'
                }
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode())
                return
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # 进行预测
            predictions = self._make_prediction(model)
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'data': predictions,
                'disclaimer': '⚠️ 本预测仅供学习参考，不构成购彩建议。彩票是随机事件，请理性对待。'
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            
        except Exception as e:
            self.send_error(500, f'Error: {str(e)}')
    
    def _make_prediction(self, model: dict) -> dict:
        """生成预测"""
        # 按概率排序
        red_sorted = sorted(
            model['red_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        blue_sorted = sorted(
            model['blue_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:6]
        
        def get_reason(prob, ball_type):
            if ball_type == 'red':
                if prob > 0.025:
                    return "高频热号"
                elif prob > 0.02:
                    return "中频温号"
                else:
                    return "低频冷号"
            else:
                if prob > 0.1:
                    return "高频热号"
                elif prob > 0.08:
                    return "中频温号"
                else:
                    return "低频冷号"
        
        return {
            'red': [
                {
                    'number': n,
                    'probability': round(p, 4),
                    'reason': get_reason(p, 'red')
                }
                for n, p in red_sorted
            ],
            'blue': [
                {
                    'number': n,
                    'probability': round(p, 4),
                    'reason': get_reason(p, 'blue')
                }
                for n, p in blue_sorted
            ],
            'model_info': {
                'window_size': model.get('window_size', 100),
                'trained_at': model.get('trained_at', 'unknown')
            }
        }
