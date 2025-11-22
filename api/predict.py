from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from _lottery_data import LOTTERY_HISTORY
from _ml_predictor import MLPredictor

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
                        'data_source': 'Real ML analysis',
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
                    'features_used': ['Frequency Analysis', 'Missing Value', 'Odd-Even Ratio', 'Sum Value', 'Span Analysis', 'Pattern Recognition'],
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
            error_response = {'status': 'error', 'message': str(e), 'error_type': type(e).__name__, 'timestamp': datetime.now().isoformat()}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        self.do_POST()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Commit: "Fix: Update imports to use underscore prefix"**

**等待2分钟部署，测试预测功能！**

---

# 🗄️ 阶段2：MongoDB数据存储

## 步骤1：注册MongoDB Atlas（免费）

1. **访问：** https://www.mongodb.com/cloud/atlas/register
2. **注册免费账号**
3. **创建免费集群**（选择最近的区域）
4. **创建数据库用户**（记住用户名和密码）
5. **添加IP白名单**：选择 "Allow Access from Anywhere" (0.0.0.0/0)
6. **获取连接字符串**（类似）：
```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/lottery?retryWrites=true&w=majority
```

---

## 步骤2：更新requirements.txt

**编辑 `requirements.txt`，添加：**
```
requests==2.31.0
python-dateutil==2.8.2
pymongo==4.6.1
