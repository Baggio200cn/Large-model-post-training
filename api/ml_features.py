"""
机器学习特征工程模块
提取彩票数据的统计特征
"""

import numpy as np
from collections import Counter
from datetime import datetime, timedelta

class LotteryFeatureExtractor:
    """彩票特征提取器"""
    
    def __init__(self, historical_data):
        """
        初始化特征提取器
        :param historical_data: 历史开奖数据列表
        """
        self.data = historical_data
        self.front_numbers = []
        self.back_numbers = []
        
        # 解析数据
        for record in historical_data:
            self.front_numbers.extend(record['front_zone'])
            self.back_numbers.extend(record['back_zone'])
    
    def calculate_frequency(self, zone='front', top_n=10):
        """
        计算号码出现频率
        :param zone: 'front' 或 'back'
        :param top_n: 返回前N个高频号码
        :return: 高频号码列表
        """
        numbers = self.front_numbers if zone == 'front' else self.back_numbers
        counter = Counter(numbers)
        return [num for num, count in counter.most_common(top_n)]
    
    def calculate_cold_numbers(self, zone='front', bottom_n=10):
        """
        计算冷号（低频号码）
        :param zone: 'front' 或 'back'
        :param bottom_n: 返回最冷的N个号码
        :return: 冷号列表
        """
        numbers = self.front_numbers if zone == 'front' else self.back_numbers
        max_num = 35 if zone == 'front' else 12
        
        counter = Counter(numbers)
        all_numbers = range(1, max_num + 1)
        
        # 按出现次数排序（从少到多）
        sorted_nums = sorted(all_numbers, key=lambda x: counter.get(x, 0))
        return sorted_nums[:bottom_n]
    
    def calculate_missing_values(self, zone='front', last_n=10):
        """
        计算遗漏值（多少期没出现）
        :param zone: 'front' 或 'back'
        :param last_n: 检查最近N期
        :return: {号码: 遗漏期数}
        """
        max_num = 35 if zone == 'front' else 12
        missing = {}
        
        # 获取最近N期数据
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        
        for num in range(1, max_num + 1):
            miss_count = 0
            for record in reversed(recent_data):
                zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
                if num in zone_data:
                    break
                miss_count += 1
            missing[num] = miss_count
        
        return missing
    
    def calculate_odd_even_ratio(self, zone='front', last_n=20):
        """
        计算奇偶比例趋势
        :param zone: 'front' 或 'back'
        :param last_n: 最近N期
        :return: 平均奇数比例
        """
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        odd_counts = []
        
        for record in recent_data:
            zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
            odd_count = sum(1 for num in zone_data if num % 2 == 1)
            odd_counts.append(odd_count / len(zone_data))
        
        return np.mean(odd_counts)
    
    def calculate_sum_value(self, zone='front', last_n=20):
        """
        计算号码和值趋势
        :param zone: 'front' 或 'back'
        :param last_n: 最近N期
        :return: 平均和值
        """
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        sum_values = []
        
        for record in recent_data:
            zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
            sum_values.append(sum(zone_data))
        
        return np.mean(sum_values), np.std(sum_values)
    
    def calculate_span(self, zone='front', last_n=20):
        """
        计算跨度（最大值-最小值）
        :param zone: 'front' 或 'back'
        :param last_n: 最近N期
        :return: 平均跨度
        """
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        spans = []
        
        for record in recent_data:
            zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
            spans.append(max(zone_data) - min(zone_data))
        
        return np.mean(spans), np.std(spans)
    
    def calculate_ac_value(self, numbers):
        """
        计算AC值（号码复杂度）
        AC值 = 号码差值的种类数 - (号码个数-1)
        :param numbers: 号码列表
        :return: AC值
        """
        if len(numbers) < 2:
            return 0
        
        sorted_nums = sorted(numbers)
        differences = set()
        
        for i in range(len(sorted_nums)):
            for j in range(i + 1, len(sorted_nums)):
                differences.add(abs(sorted_nums[i] - sorted_nums[j]))
        
        return len(differences) - (len(numbers) - 1)
    
    def extract_all_features(self):
        """
        提取所有特征
        :return: 特征字典
        """
        features = {
            'front_hot': self.calculate_frequency('front', 10),
            'front_cold': self.calculate_cold_numbers('front', 10),
            'back_hot': self.calculate_frequency('back', 5),
            'back_cold': self.calculate_cold_numbers('back', 5),
            'front_missing': self.calculate_missing_values('front', 10),
            'back_missing': self.calculate_missing_values('back', 5),
            'front_odd_ratio': self.calculate_odd_even_ratio('front'),
            'back_odd_ratio': self.calculate_odd_even_ratio('back'),
            'front_sum_mean': self.calculate_sum_value('front')[0],
            'front_sum_std': self.calculate_sum_value('front')[1],
            'back_sum_mean': self.calculate_sum_value('back')[0],
            'back_sum_std': self.calculate_sum_value('back')[1],
            'front_span_mean': self.calculate_span('front')[0],
            'front_span_std': self.calculate_span('front')[1],
            'back_span_mean': self.calculate_span('back')[0],
            'back_span_std': self.calculate_span('back')[1],
        }
        
        return features
