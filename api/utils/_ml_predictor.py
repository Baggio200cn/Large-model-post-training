"""ML预测模型 - 无numpy依赖版本"""
import random
import statistics
from _ml_features import LotteryFeatureExtractor

class MLPredictor:
    """ML预测器"""
    
    def __init__(self, historical_data):
        self.data = historical_data
        self.feature_extractor = LotteryFeatureExtractor(historical_data)
        self.features = self.feature_extractor.extract_all_features()
    
    def weighted_random_choice(self, numbers, weights, k):
        """加权随机选择"""
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]
        selected = []
        available_indices = list(range(len(numbers)))
        for _ in range(k):
            if not available_indices:
                break
            current_probs = [probabilities[i] for i in available_indices]
            current_total = sum(current_probs)
            current_probs = [p / current_total for p in current_probs]
            chosen_idx = random.choices(available_indices, weights=current_probs, k=1)[0]
            selected.append(numbers[chosen_idx])
            available_indices.remove(chosen_idx)
        return sorted(selected)
    
    def frequency_based_prediction(self, zone='front', count=5):
        """基于频率的预测"""
        max_num = 35 if zone == 'front' else 12
        hot_numbers = self.features[f'{zone}_hot']
        missing = self.features[f'{zone}_missing']
        weights = []
        numbers = list(range(1, max_num + 1))
        for num in numbers:
            base_weight = 10 if num in hot_numbers else 5
            missing_weight = missing.get(num, 0) * 0.5
            weights.append(base_weight + missing_weight)
        return self.weighted_random_choice(numbers, weights, count)
    
    def pattern_based_prediction(self, zone='front', count=5):
        """基于模式的预测"""
        max_num = 35 if zone == 'front' else 12
        numbers = list(range(1, max_num + 1))
        target_odd_ratio = self.features[f'{zone}_odd_ratio']
        target_odd_count = int(count * target_odd_ratio)
        odd_nums = [n for n in numbers if n % 2 == 1]
        even_nums = [n for n in numbers if n % 2 == 0]
        hot_odds = [n for n in self.features[f'{zone}_hot'] if n % 2 == 1]
        odd_weights = [2 if n in hot_odds else 1 for n in odd_nums]
        selected_odds = self.weighted_random_choice(odd_nums, odd_weights, target_odd_count)
        even_count = count - len(selected_odds)
        hot_evens = [n for n in self.features[f'{zone}_hot'] if n % 2 == 0]
        even_weights = [2 if n in hot_evens else 1 for n in even_nums]
        selected_evens = self.weighted_random_choice(even_nums, even_weights, even_count)
        return sorted(selected_odds + selected_evens)
    
    def missing_based_prediction(self, zone='front', count=5):
        """基于遗漏值的预测"""
        missing = self.features[f'{zone}_missing']
        sorted_by_missing = sorted(missing.items(), key=lambda x: x[1], reverse=True)
        candidates = [num for num, _ in sorted_by_missing[:count * 2]]
        weights = [missing[num] + 1 for num in candidates]
        return self.weighted_random_choice(candidates, weights, count)
    
    def balanced_prediction(self, zone='front', count=5):
        """平衡预测"""
        max_num = 35 if zone == 'front' else 12
        numbers = list(range(1, max_num + 1))
        hot_nums = set(self.features[f'{zone}_hot'])
        cold_nums = set(self.features[f'{zone}_cold'])
        missing = self.features[f'{zone}_missing']
        weights = []
        for num in numbers:
            weight = 5
            if num in hot_nums:
                weight += 3
            if num in cold_nums:
                weight += 1
            weight += missing.get(num, 0) * 0.3
            weights.append(weight)
        return self.weighted_random_choice(numbers, weights, count)
    
    def generate_predictions(self, num_groups=5):
        """生成多组预测"""
        strategies = [
            ('频率优先', self.frequency_based_prediction),
            ('模式匹配', self.pattern_based_prediction),
            ('遗漏补偿', self.missing_based_prediction),
            ('平衡策略', self.balanced_prediction),
            ('综合推荐', self.balanced_prediction),
        ]
        predictions = []
        for i, (strategy_name, strategy_func) in enumerate(strategies[:num_groups]):
            front = strategy_func('front', 5)
            back = strategy_func('back', 2)
            confidence = self.calculate_confidence(front, back, strategy_name)
            predictions.append({
                'group': i + 1,
                'strategy': strategy_name,
                'front_zone': front,
                'back_zone': back,
                'confidence': confidence
            })
        return predictions
    
    def calculate_confidence(self, front, back, strategy):
        """计算置信度"""
        confidence = 0.65
        front_hot_coverage = len(set(front) & set(self.features['front_hot'])) / 5
        back_hot_coverage = len(set(back) & set(self.features['back_hot'])) / 2
        confidence += front_hot_coverage * 0.1 + back_hot_coverage * 0.05
        front_odd_ratio = sum(1 for n in front if n % 2 == 1) / 5
        if abs(front_odd_ratio - self.features['front_odd_ratio']) < 0.2:
            confidence += 0.05
        front_sum = sum(front)
        if abs(front_sum - self.features['front_sum_mean']) < self.features['front_sum_std']:
            confidence += 0.05
        strategy_bonus = {'频率优先': 0.03, '平衡策略': 0.05, '综合推荐': 0.05}
        confidence += strategy_bonus.get(strategy, 0)
        return min(max(confidence, 0.60), 0.90)
