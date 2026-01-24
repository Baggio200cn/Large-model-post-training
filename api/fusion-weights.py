# -*- coding: utf-8 -*-
"""
EWMA自动权重分配模块
根据历史预测准确率动态调整ML和灵修预测的权重
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# 添加api目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class WeightCalculator:
    """EWMA权重计算器"""

    def __init__(self, decay_factor=0.9):
        """
        初始化权重计算器
        decay_factor: 衰减因子，越大表示越重视历史数据（0-1之间）
        """
        self.decay_factor = decay_factor
        # 初始准确率 - 基于经验值
        self.ml_accuracy = 0.70  # ML初始准确率70%
        self.spiritual_accuracy = 0.30  # 灵修初始准确率30%
        self.total_predictions = 0

    def update_accuracy(self, ml_hits, ml_total, spiritual_hits, spiritual_total):
        """
        更新准确率（EWMA算法）
        ml_hits: ML命中数
        ml_total: ML总预测数
        spiritual_hits: 灵修命中数
        spiritual_total: 灵修总预测数
        """
        if ml_total > 0:
            new_ml_acc = ml_hits / ml_total
            self.ml_accuracy = (self.decay_factor * self.ml_accuracy +
                               (1 - self.decay_factor) * new_ml_acc)

        if spiritual_total > 0:
            new_spiritual_acc = spiritual_hits / spiritual_total
            self.spiritual_accuracy = (self.decay_factor * self.spiritual_accuracy +
                                      (1 - self.decay_factor) * new_spiritual_acc)

        self.total_predictions += 1

    def get_weights(self):
        """
        获取归一化权重
        返回: (ml_weight, spiritual_weight)
        """
        total = self.ml_accuracy + self.spiritual_accuracy
        if total == 0:
            return 0.7, 0.3  # 默认权重

        ml_weight = self.ml_accuracy / total
        spiritual_weight = self.spiritual_accuracy / total

        # 确保权重在合理范围内 (0.3-0.8)
        ml_weight = max(0.3, min(0.8, ml_weight))
        spiritual_weight = 1.0 - ml_weight

        return round(ml_weight, 3), round(spiritual_weight, 3)

    def get_stats(self):
        """获取统计信息"""
        ml_w, sp_w = self.get_weights()
        return {
            'ml_accuracy': round(self.ml_accuracy, 3),
            'spiritual_accuracy': round(self.spiritual_accuracy, 3),
            'ml_weight': ml_w,
            'spiritual_weight': sp_w,
            'total_predictions': self.total_predictions,
            'decay_factor': self.decay_factor
        }


# 全局权重计算器实例
calculator = WeightCalculator(decay_factor=0.85)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """获取当前权重"""
        try:
            ml_weight, spiritual_weight = calculator.get_weights()
            stats = calculator.get_stats()

            result = {
                'status': 'success',
                'weights': {
                    'ml': ml_weight,
                    'spiritual': spiritual_weight
                },
                'stats': stats,
                'description': f'ML机器学习({int(ml_weight*100)}%) + 灵修直觉({int(spiritual_weight*100)}%)'
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_result = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        """更新权重"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            action = params.get('action', 'update')

            if action == 'update':
                # 更新准确率
                ml_hits = params.get('ml_hits', 0)
                ml_total = params.get('ml_total', 0)
                spiritual_hits = params.get('spiritual_hits', 0)
                spiritual_total = params.get('spiritual_total', 0)

                calculator.update_accuracy(ml_hits, ml_total, spiritual_hits, spiritual_total)

                ml_weight, spiritual_weight = calculator.get_weights()
                stats = calculator.get_stats()

                result = {
                    'status': 'success',
                    'message': '权重已更新',
                    'weights': {
                        'ml': ml_weight,
                        'spiritual': spiritual_weight
                    },
                    'stats': stats
                }

            elif action == 'reset':
                # 重置权重
                global calculator
                decay_factor = params.get('decay_factor', 0.85)
                calculator = WeightCalculator(decay_factor=decay_factor)

                result = {
                    'status': 'success',
                    'message': '权重已重置',
                    'weights': {
                        'ml': 0.7,
                        'spiritual': 0.3
                    }
                }

            elif action == 'batch_update':
                # 批量更新（用于历史数据回测）
                records = params.get('records', [])
                for record in records:
                    calculator.update_accuracy(
                        record.get('ml_hits', 0),
                        record.get('ml_total', 5),  # 前区5个号码
                        record.get('spiritual_hits', 0),
                        record.get('spiritual_total', 5)
                    )

                ml_weight, spiritual_weight = calculator.get_weights()
                stats = calculator.get_stats()

                result = {
                    'status': 'success',
                    'message': f'已处理{len(records)}条记录',
                    'weights': {
                        'ml': ml_weight,
                        'spiritual': spiritual_weight
                    },
                    'stats': stats
                }
            else:
                result = {
                    'status': 'error',
                    'message': '未知操作'
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_result = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
