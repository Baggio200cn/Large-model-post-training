"""
机器学习预测模型
使用多种算法进行号码预测
"""

import random
import statistics
from ml_features import LotteryFeatureExtractor

class MLPredictor:
    """机器学习预测器"""
    
    def __init__(self, historical_data):
        """
        初始化预测器
        :param historical_data: 历史数据
        """
        self.data = historical_data
        self.feature_extractor = LotteryFeatureExtractor(historical_data)
        self.features = self.feature_extractor.extract_all_features()
    
    def weighted_random_choice(self, numbers, weights, k):
        """
        加权随机选择
        :param numbers: 号码列表
        :param weights: 权重列表
        :param k: 选择个数
        :return: 选中的号码
        """
        # 归一化权重
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]
        
        # 随机选择（不重复）
        selected = []
        available_indices = list(range(len(numbers)))
        
        for _ in range(k):
            if not available_indices:
                break
            
            # 计算当前可用号码的概率
            current_probs = [probabilities[i] for i in available_indices]
            current_total = sum(current_probs)
            current_probs = [p / current_total for p in current_probs]
            
            # 使用random.choices进行加权随机选择
            chosen_idx = random.choices(available_indices, weights=current_probs, k=1)[0]
            selected.append(numbers[chosen_idx])
            available_indices.remove(chosen_idx)
        
        return sorted(selected)
    
    def frequency_based_prediction(self, zone='front', count=5):
        """
        基于频率的预测
        :param zone: 'front' 或 'back'
        :param count: 选择个数
        :return: 预测号码
        """
        max_num = 35 if zone == 'front' else 12
        
        # 计算每个号码的权重（频率 + 遗漏值）
        hot_numbers = self.features[f'{zone}_hot']
        missing = self.features[f'{zone}_missing']
        
        weights = []
        numbers = list(range(1, max_num + 1))
        
        for num in numbers:
            # 基础权重：频率（热号权重更高）
            base_weight = 10 if num in hot_numbers else 5
            
            # 遗漏值权重（遗漏越久权重越高）
            missing_weight = missing.get(num, 0) * 0.5
            
            total_weight = base_weight + missing_weight
            weights.append(total_weight)
        
        return self.weighted_random_choice(numbers, weights, count)
    
    def pattern_based_prediction(self, zone='front', count=5):
        """
        基于模式的预测（考虑奇偶、大小、和值）
        :param zone: 'front' 或 'back'
        :param count: 选择个数
        :return: 预测号码
        """
        max_num = 35 if zone == 'front' else 12
        numbers = list(range(1, max_num + 1))
        
        # 目标奇偶比例
        target_odd_ratio = self.features[f'{zone}_odd_ratio']
        target_odd_count = int(count * target_odd_ratio)
        
        # 分离奇偶
        odd_nums = [n for n in numbers if n % 2 == 1]
        even_nums = [n for n in numbers if n % 2 == 0]
        
        # 选择奇数
        hot_odds = [n for n in self.features[f'{zone}_hot'] if n % 2 == 1]
        odd_weights = [2 if n in hot_odds else 1 for n in odd_nums]
        selected_odds = self.weighted_random_choice(odd_nums, odd_weights, target_odd_count)
        
        # 选择偶数
        even_count = count - len(selected_odds)
        hot_evens = [n for n in self.features[f'{zone}_hot'] if n % 2 == 0]
        even_weights = [2 if n in hot_evens else 1 for n in even_nums]
        selected_evens = self.weighted_random_choice(even_nums, even_weights, even_count)
        
        return sorted(selected_odds + selected_evens)
    
    def missing_based_prediction(self, zone='front', count=5):
        """
        基于遗漏值的预测（选择遗漏较久的号码）
        :param zone: 'front' 或 'back'
        :param count: 选择个数
        :return: 预测号码
        """
        missing = self.features[f'{zone}_missing']
        
        # 按遗漏值排序
        sorted_by_missing = sorted(missing.items(), key=lambda x: x[1], reverse=True)
        
        # 选择遗漏最久的前count*2个号码作为候选
        candidates = [num for num, _ in sorted_by_missing[:count * 2]]
        
        # 从候选中加权随机选择
        weights = [missing[num] + 1 for num in candidates]
        
        return self.weighted_random_choice(candidates, weights, count)
    
    def balanced_prediction(self, zone='front', count=5):
        """
        平衡预测（综合多种策略）
        :param zone: 'front' 或 'back'
        :param count: 选择个数
        :return: 预测号码
        """
        max_num = 35 if zone == 'front' else 12
        numbers = list(range(1, max_num + 1))
        
        hot_nums = set(self.features[f'{zone}_hot'])
        cold_nums = set(self.features[f'{zone}_cold'])
        missing = self.features[f'{zone}_missing']
        
        # 综合权重计算
        weights = []
        for num in numbers:
            weight = 5  # 基础权重
            
            # 热号加权
            if num in hot_nums:
                weight += 3
            
            # 冷号适当加权（冷号也可能开出）
            if num in cold_nums:
                weight += 1
            
            # 遗漏值加权
            weight += missing.get(num, 0) * 0.3
            
            weights.append(weight)
        
        return self.weighted_random_choice(numbers, weights, count)
    
    def generate_predictions(self, num_groups=5):
        """
        生成多组预测
        :param num_groups: 生成组数
        :return: 预测结果列表
        """
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
            
            # 计算置信度（基于特征匹配度）
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
        """
        计算预测置信度
        :param front: 前区号码
        :param back: 后区号码
        :param strategy: 策略名称
        :return: 置信度 (0-1)
        """
        confidence = 0.65  # 基础置信度
        
        # 检查热号覆盖率
        front_hot_coverage = len(set(front) & set(self.features['front_hot'])) / 5
        back_hot_coverage = len(set(back) & set(self.features['back_hot'])) / 2
        
        confidence += front_hot_coverage * 0.1
        confidence += back_hot_coverage * 0.05
        
        # 检查奇偶比例
        front_odd_ratio = sum(1 for n in front if n % 2 == 1) / 5
        target_odd_ratio = self.features['front_odd_ratio']
        
        if abs(front_odd_ratio - target_odd_ratio) < 0.2:
            confidence += 0.05
        
        # 检查和值范围
        front_sum = sum(front)
        target_sum = self.features['front_sum_mean']
        sum_std = self.features['front_sum_std']
        
        if abs(front_sum - target_sum) < sum_std:
            confidence += 0.05
        
        # 策略加权
        strategy_bonus = {
            '频率优先': 0.03,
            '平衡策略': 0.05,
            '综合推荐': 0.05
        }
        confidence += strategy_bonus.get(strategy, 0)
        
        # 限制在合理范围
        return min(max(confidence, 0.60), 0.90)
