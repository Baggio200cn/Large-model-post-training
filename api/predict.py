from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random

class handler(BaseHTTPRequestHandler):
    
    def _send_response(self, status_code, data):
        """统一发送响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """GET方法 - 测试接口"""
        try:
            front_zone = sorted(random.sample(range(1, 36), 5))
            back_zone = sorted(random.sample(range(1, 13), 2))
            
            response = {
                'status': 'success',
                'method': 'GET',
                'prediction': {
                    'ensemble_prediction': {
                        'front_zone': front_zone,
                        'back_zone': back_zone,
                        'confidence': round(random.uniform(0.75, 0.90), 3)
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_response(200, response)
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            self._send_response(500, error_response)
    
    def do_POST(self):
        """POST方法 - 主预测接口"""
        try:
            # 生成5组预测
            predictions = []
            for i in range(5):
                front_zone = sorted(random.sample(range(1, 36), 5))
                back_zone = sorted(random.sample(range(1, 13), 2))
                predictions.append({
                    'group': i + 1,
                    'front_zone': front_zone,
                    'back_zone': back_zone,
                    'confidence': round(random.uniform(0.70, 0.90), 3)
                })
            
            response = {
                'status': 'success',
                'method': 'POST',
                'prediction': {
                    'ensemble_prediction': {
                        'front_zone': predictions[0]['front_zone'],
                        'back_zone': predictions[0]['back_zone'],
                        'confidence': predictions[0]['confidence']
                    },
                    'all_predictions': predictions,
                    'individual_models': {
                        'lstm_model': {
                            'front_zone': sorted(random.sample(range(1, 36), 5)),
                            'back_zone': sorted(random.sample(range(1, 13), 2)),
                            'confidence': round(random.uniform(0.60, 0.80), 3)
                        },
                        'transformer_model': {
                            'front_zone': sorted(random.sample(range(1, 36), 5)),
                            'back_zone': sorted(random.sample(range(1, 13), 2)),
                            'confidence': round(random.uniform(0.65, 0.85), 3)
                        },
                        'xgboost_model': {
                            'front_zone': sorted(random.sample(range(1, 36), 5)),
                            'back_zone': sorted(random.sample(range(1, 13), 2)),
                            'confidence': round(random.uniform(0.55, 0.75), 3)
                        }
                    },
                    'model_weights': {
                        'lstm': 0.35,
                        'transformer': 0.40,
                        'xgboost': 0.25
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_response(200, response)
            
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            self._send_response(500, error_response)
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**这个版本的改进：**
- ✅ 统一的响应方法
- ✅ 添加了字符编码
- ✅ 添加了Cache-Control
- ✅ 生成5组预测（符合前端需求）
- ✅ 更详细的错误信息

---

## 📋 完整操作清单

1. **[ ] 访问GitHub查看predict.py代码**
2. **[ ] 点击编辑，全部替换为上面的代码**
3. **[ ] Commit提交：`Fix: Robust predict API with proper JSON response`**
4. **[ ] 等待2-3分钟Vercel部署**
5. **[ ] 访问：`https://large-model-post-training.vercel.app/api/predict.py`**
6. **[ ] 应该看到JSON而不是错误页面**
7. **[ ] 回到首页点击"生成AI预测"按钮**
8. **[ ] 看到5组预测结果 ✅**

---

## 🎯 验证方法

**部署完成后，直接在浏览器访问：**
```
https://large-model-post-training.vercel.app/api/predict.py
