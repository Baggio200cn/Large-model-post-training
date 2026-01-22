"""
智能融合预测 API
整合多个模型，使用自适应权重生成最终预测
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from typing import Dict, List
from collections import Counter

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class FusionPredictor:
    """融合预测器"""

    def __init__(self):
        # 尝试加载自适应权重管理器
        try:
            from utils.adaptive_weights import get_weight_manager
            self.weight_manager = get_weight_manager()
            self.use_adaptive = True
        except:
            self.weight_manager = None
            self.use_adaptive = False
            # 默认权重
            self.default_weights = {
                'ml_lstm': 0.30,
                'ml_xgboost': 0.25,
                'spiritual': 0.20,
                'statistical': 0.25
            }

    def get_weights(self) -> Dict[str, float]:
        """获取当前权重"""
        if self.use_adaptive and self.weight_manager:
            weights = self.weight_manager.get_weights()
            # 如果权重为空，使用默认值
            return weights if weights else self.default_weights
        else:
            return self.default_weights

    def fuse_predictions(self, predictions: Dict[str, Dict]) -> Dict:
        """
        融合多个预测结果

        Args:
            predictions: {
                'ml_lstm': {'front': [1,5,12,20,31], 'back': [3,9]},
                'spiritual': {'front': [7,14,19,28,35], 'back': [1,11]},
                ...
            }

        Returns:
            融合后的预测结果
        """
        weights = self.get_weights()

        # 收集所有号码及其加权得分
        front_scores = {}  # {号码: 加权得分}
        back_scores = {}

        for model, pred in predictions.items():
            weight = weights.get(model, 0.0)

            # 前区号码
            for num in pred.get('front', []):
                front_scores[num] = front_scores.get(num, 0) + weight

            # 后区号码
            for num in pred.get('back', []):
                back_scores[num] = back_scores.get(num, 0) + weight

        # 选择得分最高的号码
        front_zone = sorted(front_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        front_zone = sorted([num for num, score in front_zone])

        back_zone = sorted(back_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        back_zone = sorted([num for num, score in back_zone])

        # 计算置信度（归一化的平均权重）
        confidence = sum(weights.values()) / len(weights) if weights else 0.5

        return {
            'front_zone': front_zone,
            'back_zone': back_zone,
            'confidence': confidence,
            'weights_used': weights,
            'adaptive_enabled': self.use_adaptive
        }

    def get_performance_summary(self) -> Dict:
        """获取模型表现摘要"""
        if not self.use_adaptive or not self.weight_manager:
            return {
                'available': False,
                'message': '自适应权重系统未启用'
            }

        stats = self.weight_manager.get_performance_stats()
        return {
            'available': True,
            'statistics': stats
        }


class handler(BaseHTTPRequestHandler):
    """API Handler"""

    def do_POST(self):
        """处理POST请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            # 提取各模型的预测结果
            predictions = data.get('predictions', {})

            if not predictions:
                raise ValueError('缺少预测数据')

            # 初始化融合器
            predictor = FusionPredictor()

            # 执行融合
            result = predictor.fuse_predictions(predictions)

            # 获取性能统计（如果可用）
            performance = predictor.get_performance_summary()

            # 构建响应
            response = {
                'success': True,
                'fusion_prediction': result,
                'performance_stats': performance,
                'input_models': list(predictions.keys())
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        """获取当前权重状态"""
        try:
            predictor = FusionPredictor()
            weights = predictor.get_weights()
            performance = predictor.get_performance_summary()

            response = {
                'success': True,
                'current_weights': weights,
                'performance_stats': performance,
                'adaptive_enabled': predictor.use_adaptive
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
