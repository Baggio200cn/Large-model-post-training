"""
大乐透ML预测系统 - 真正的机器学习版本
使用从腾讯云COS加载的训练模型：
- XGBoost (sklearn)
- RandomForest (sklearn)
- LSTM (ONNX)
- Transformer (ONNX)
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def get_historical_data():
    """获取历史数据：优先从COS，否则使用本地备份"""
    try:
        # 检查COS配置
        cos_configured = all([
            os.getenv('TENCENT_SECRET_ID'),
            os.getenv('TENCENT_SECRET_KEY'),
            os.getenv('TENCENT_COS_BUCKET'),
            os.getenv('TENCENT_COS_REGION')
        ])

        if cos_configured:
            from utils._cos_data_loader import get_lottery_data
            data = get_lottery_data()
            if data and len(data) > 0:
                return data, 'tencent_cos'

    except Exception as e:
        print(f"⚠️  从COS加载数据失败: {e}")

    # 回退到本地数据
    try:
        from utils._lottery_data import lottery_data
        return lottery_data, 'local_backup'
    except Exception as e:
        print(f"⚠️  加载本地数据失败: {e}")

    # 最后的备份数据
    return FALLBACK_DATA, 'embedded_fallback'


# 嵌入式备份数据
FALLBACK_DATA = [
    {'period': '25142', 'front_zone': [9, 10, 14, 27, 29], 'back_zone': [2, 9]},
    {'period': '25141', 'front_zone': [4, 9, 24, 28, 29], 'back_zone': [2, 10]},
    {'period': '25140', 'front_zone': [1, 6, 24, 26, 30], 'back_zone': [4, 11]},
    {'period': '25139', 'front_zone': [7, 14, 16, 29, 31], 'back_zone': [1, 6]},
    {'period': '25138', 'front_zone': [3, 8, 22, 27, 35], 'back_zone': [3, 9]},
    {'period': '25137', 'front_zone': [5, 11, 19, 25, 33], 'back_zone': [2, 7]},
    {'period': '25136', 'front_zone': [2, 10, 18, 23, 31], 'back_zone': [5, 12]},
    {'period': '25135', 'front_zone': [6, 13, 21, 28, 34], 'back_zone': [1, 8]},
    {'period': '25134', 'front_zone': [4, 15, 20, 26, 32], 'back_zone': [4, 10]},
    {'period': '25133', 'front_zone': [8, 12, 17, 24, 30], 'back_zone': [3, 11]},
]


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        """处理预测请求"""
        try:
            # 获取历史数据
            historical_data, data_source = get_historical_data()

            if len(historical_data) < 10:
                raise Exception(f"历史数据不足: {len(historical_data)}期")

            # 检查是否使用COS模型
            use_cos_models = all([
                os.getenv('TENCENT_SECRET_ID'),
                os.getenv('TENCENT_SECRET_KEY'),
                os.getenv('TENCENT_COS_BUCKET'),
                os.getenv('TENCENT_COS_REGION')
            ])

            # 创建预测器
            try:
                from utils._real_ml_predictor import RealMLPredictor
                predictor = RealMLPredictor(historical_data, use_cos_models=use_cos_models)
                ml_version = 'real_ml'
            except ImportError as e:
                print(f"⚠️  无法导入RealMLPredictor: {e}")
                # 回退到简单预测
                from utils._ml_predictor import MLPredictor
                predictor = MLPredictor(historical_data)
                ml_version = 'simple_ml'

            # 获取预测结果
            if ml_version == 'real_ml':
                ensemble_result = predictor.ensemble_predict()
                all_predictions = predictor.get_all_predictions()

                response = {
                    'status': 'success',
                    'prediction': {
                        'ensemble_prediction': {
                            'front_zone': ensemble_result['front'],
                            'back_zone': ensemble_result['back'],
                            'confidence': ensemble_result['confidence'],
                            'models_used': ensemble_result['total_models'],
                            'cos_models_used': ensemble_result['cos_models_used']
                        },
                        'individual_models': {
                            name: {
                                'front_zone': pred['front'],
                                'back_zone': pred['back'],
                                'confidence': pred['confidence'],
                                'source': pred['source'],
                                'description': pred['description']
                            }
                            for name, pred in ensemble_result['individual_predictions'].items()
                        },
                        'based_on_data': {
                            'periods_analyzed': len(historical_data),
                            'data_source': data_source,
                            'hot_numbers_front': all_predictions['features']['front_hot'],
                            'hot_numbers_back': all_predictions['features']['back_hot']
                        }
                    },
                    'ml_info': {
                        'version': ml_version,
                        'models': ['XGBoost', 'RandomForest', 'LSTM', 'Transformer'],
                        'model_format': {
                            'xgboost': 'sklearn (.pkl)',
                            'random_forest': 'sklearn (.pkl)',
                            'lstm': 'ONNX (.onnx)',
                            'transformer': 'ONNX (.onnx)'
                        },
                        'weights': ensemble_result['weights'],
                        'model_sources': ensemble_result['model_sources']
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # 简单预测回退
                predictions = predictor.generate_predictions(5)
                response = {
                    'status': 'success',
                    'prediction': {
                        'ensemble_prediction': {
                            'front_zone': predictions[0]['front_zone'],
                            'back_zone': predictions[0]['back_zone'],
                            'confidence': predictions[0]['confidence']
                        },
                        'all_predictions': predictions,
                        'based_on_data': {
                            'periods_analyzed': len(historical_data),
                            'data_source': data_source
                        }
                    },
                    'ml_info': {
                        'version': ml_version,
                        'note': '使用简化ML预测（COS模型加载失败）'
                    },
                    'timestamp': datetime.now().isoformat()
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        """GET请求同样返回预测结果"""
        self.do_POST()

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
