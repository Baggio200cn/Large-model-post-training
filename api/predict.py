"""
预测API - 零外部依赖版本
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
            # 获取模型文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'frequency_model.pkl')
            
            # 检查文件是否存在
            if not os.path.exists(model_path):
                self._send_error_response(
                    503,
                    '模型文件未找到',
                    f'路径: {model_path}'
                )
                return
            
            # 加载模型
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            except Exception as e:
                self._send_error_response(
                    500,
                    '模型加载失败',
                    str(e)
                )
                return
            
            # 生成预测
            predictions = self._make_prediction(model)
            
            # 返回成功结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'data': predictions,
                'disclaimer': '⚠️ 本预测仅供学习参考，不构成购彩建议。彩票是随机事件，请理性对待。'
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(500, '服务器内部错误', str(e))
    
    def _send_error_response(self, code, error, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': error,
            'message': message
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def _make_prediction(self, model):
        """生成预测"""
        # 获取概率字典
        red_probs = model.get('red_probabilities', {})
        blue_probs = model.get('blue_probabilities', {})
        
        # 排序
        red_sorted = sorted(red_probs.items(), key=lambda x: x[1], reverse=True)[:10]
        blue_sorted = sorted(blue_probs.items(), key=lambda x: x[1], reverse=True)[:6]
        
        def get_reason(prob, ball_type):
            """根据概率判断号码类型"""
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
                    'number': int(n),
                    'probability': round(float(p), 4),
                    'reason': get_reason(p, 'red')
                }
                for n, p in red_sorted
            ],
            'blue': [
                {
                    'number': int(n),
                    'probability': round(float(p), 4),
                    'reason': get_reason(p, 'blue')
                }
                for n, p in blue_sorted
            ],
            'model_info': {
                'window_size': model.get('window_size', 50),
                'trained_at': model.get('trained_at', 'unknown')
            }
        }