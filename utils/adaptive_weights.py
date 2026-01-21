"""
自适应权重管理系统
根据历史预测表现动态调整模型权重
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import math


class AdaptiveWeightManager:
    """动态权重管理器"""

    def __init__(self,
                 history_file: str = 'data/prediction_history.json',
                 weights_file: str = 'data/model_weights.json',
                 window_size: int = 20,
                 decay_factor: float = 0.9):
        """
        初始化

        Args:
            history_file: 预测历史文件
            weights_file: 权重文件
            window_size: 滑动窗口大小（评估最近N期）
            decay_factor: 时间衰减因子（0-1，越小衰减越快）
        """
        self.history_file = history_file
        self.weights_file = weights_file
        self.window_size = window_size
        self.decay_factor = decay_factor

        # 模型列表
        self.models = [
            'ml_random_forest',
            'ml_xgboost',
            'ml_lstm',
            'ml_transformer',
            'spiritual'
        ]

        # 初始权重（均等）
        self.default_weights = {model: 1.0/len(self.models) for model in self.models}

    def calculate_score(self,
                       prediction: Dict,
                       actual: Dict) -> float:
        """
        计算单期预测得分

        评分规则：
        - 前区每命中1个：10分
        - 后区每命中1个：20分
        - 前区位置完全匹配：额外+5分/个
        - 后区位置完全匹配：额外+10分/个

        Args:
            prediction: {"front": [1,5,12,20,31], "back": [3,9]}
            actual: {"front": [3,9,14,27,29], "back": [2,9]}

        Returns:
            总分（0-150分）
        """
        score = 0.0

        pred_front = set(prediction.get('front', []))
        pred_back = set(prediction.get('back', []))
        actual_front = set(actual.get('front', []))
        actual_back = set(actual.get('back', []))

        # 前区命中数
        front_hits = len(pred_front & actual_front)
        score += front_hits * 10

        # 后区命中数
        back_hits = len(pred_back & actual_back)
        score += back_hits * 20

        # 位置匹配奖励
        pred_front_list = prediction.get('front', [])
        actual_front_list = actual.get('front', [])
        for i in range(min(len(pred_front_list), len(actual_front_list))):
            if pred_front_list[i] == actual_front_list[i]:
                score += 5

        pred_back_list = prediction.get('back', [])
        actual_back_list = actual.get('back', [])
        for i in range(min(len(pred_back_list), len(actual_back_list))):
            if pred_back_list[i] == actual_back_list[i]:
                score += 10

        return score

    def update_history(self,
                      period: str,
                      predictions: Dict[str, Dict],
                      actual: Dict):
        """
        更新预测历史

        Args:
            period: 期号
            predictions: {model_name: {front: [...], back: [...]}}
            actual: {front: [...], back: [...]}
        """
        # 加载历史数据
        history = self._load_history()

        # 计算各模型得分
        scores = {}
        for model, pred in predictions.items():
            scores[model] = self.calculate_score(pred, actual)

        # 添加新记录
        history.append({
            'period': period,
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions,
            'actual': actual,
            'scores': scores
        })

        # 保存（只保留最近100期）
        history = history[-100:]
        self._save_history(history)

        # 更新权重
        self.update_weights()

    def update_weights(self):
        """
        基于历史表现更新权重
        使用指数加权移动平均（EWMA）
        """
        history = self._load_history()

        if len(history) == 0:
            # 没有历史数据，使用默认权重
            self._save_weights(self.default_weights)
            return

        # 获取最近N期数据
        recent = history[-self.window_size:]

        # 计算每个模型的加权平均得分
        weighted_scores = {model: 0.0 for model in self.models}
        weight_sum = 0.0

        for i, record in enumerate(recent):
            # 时间权重（越近期权重越高）
            time_weight = self.decay_factor ** (len(recent) - 1 - i)
            weight_sum += time_weight

            for model in self.models:
                score = record['scores'].get(model, 0)
                weighted_scores[model] += score * time_weight

        # 归一化
        if weight_sum > 0:
            for model in weighted_scores:
                weighted_scores[model] /= weight_sum

        # Softmax归一化转换为权重
        weights = self._softmax(weighted_scores, temperature=10.0)

        # 保存权重
        self._save_weights(weights)

        return weights

    def _softmax(self, scores: Dict[str, float], temperature: float = 1.0) -> Dict[str, float]:
        """
        Softmax归一化

        Args:
            scores: {model: score}
            temperature: 温度参数（越高分布越平滑）

        Returns:
            {model: weight} (所有权重和为1)
        """
        # 避免数值溢出
        max_score = max(scores.values()) if scores else 0
        exp_scores = {
            model: math.exp((score - max_score) / temperature)
            for model, score in scores.items()
        }

        total = sum(exp_scores.values())

        if total == 0:
            return self.default_weights

        return {model: exp_score / total for model, exp_score in exp_scores.items()}

    def get_weights(self) -> Dict[str, float]:
        """获取当前权重"""
        if not os.path.exists(self.weights_file):
            return self.default_weights

        try:
            with open(self.weights_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('weights', self.default_weights)
        except:
            return self.default_weights

    def get_performance_stats(self) -> Dict:
        """获取模型表现统计"""
        history = self._load_history()
        recent = history[-self.window_size:]

        stats = {}
        for model in self.models:
            scores = [r['scores'].get(model, 0) for r in recent if model in r['scores']]

            if scores:
                stats[model] = {
                    'avg_score': sum(scores) / len(scores),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'periods': len(scores)
                }
            else:
                stats[model] = {
                    'avg_score': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'periods': 0
                }

        return stats

    def _load_history(self) -> List[Dict]:
        """加载历史数据"""
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _save_history(self, history: List[Dict]):
        """保存历史数据"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _save_weights(self, weights: Dict[str, float]):
        """保存权重"""
        os.makedirs(os.path.dirname(self.weights_file), exist_ok=True)
        data = {
            'weights': weights,
            'updated_at': datetime.now().isoformat(),
            'window_size': self.window_size,
            'decay_factor': self.decay_factor
        }
        with open(self.weights_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# 全局单例
_weight_manager = None

def get_weight_manager() -> AdaptiveWeightManager:
    """获取全局权重管理器"""
    global _weight_manager
    if _weight_manager is None:
        _weight_manager = AdaptiveWeightManager()
    return _weight_manager


if __name__ == '__main__':
    # 测试代码
    manager = AdaptiveWeightManager()

    # 模拟几期数据
    print("模拟测试自适应权重系统\n")

    for period in range(25140, 25150):
        # 模拟预测
        predictions = {
            'ml_lstm': {'front': [3, 9, 14, 27, 29], 'back': [2, 9]},
            'ml_xgboost': {'front': [1, 5, 14, 20, 29], 'back': [3, 9]},
            'spiritual': {'front': [7, 14, 19, 28, 35], 'back': [1, 9]}
        }

        # 模拟实际开奖
        actual = {'front': [3, 9, 14, 27, 29], 'back': [2, 9]}

        # 更新历史
        manager.update_history(str(period), predictions, actual)

        # 显示当前权重
        weights = manager.get_weights()
        print(f"期号 {period} 权重分布：")
        for model, weight in weights.items():
            print(f"  {model}: {weight:.3f}")
        print()

    # 显示表现统计
    print("\n模型表现统计：")
    stats = manager.get_performance_stats()
    for model, stat in stats.items():
        print(f"{model}:")
        print(f"  平均得分: {stat['avg_score']:.2f}")
        print(f"  最高得分: {stat['max_score']:.2f}")
        print()
