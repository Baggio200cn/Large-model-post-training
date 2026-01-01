"""ML特征工程模块 - 无numpy依赖版本"""
import statistics
from collections import Counter

class LotteryFeatureExtractor:
    """彩票特征提取器"""
    
    def __init__(self, historical_data):
        self.data = historical_data
        self.front_numbers = []
        self.back_numbers = []
        for record in historical_data:
            self.front_numbers.extend(record['front_zone'])
            self.back_numbers.extend(record['back_zone'])
    
    def calculate_frequency(self, zone='front', top_n=10):
        """计算号码出现频率"""
        numbers = self.front_numbers if zone == 'front' else self.back_numbers
        counter = Counter(numbers)
        return [num for num, count in counter.most_common(top_n)]
    
    def calculate_cold_numbers(self, zone='front', bottom_n=10):
        """计算冷号"""
        numbers = self.front_numbers if zone == 'front' else self.back_numbers
        max_num = 35 if zone == 'front' else 12
        counter = Counter(numbers)
        all_numbers = range(1, max_num + 1)
        sorted_nums = sorted(all_numbers, key=lambda x: counter.get(x, 0))
        return sorted_nums[:bottom_n]
    
    def calculate_missing_values(self, zone='front', last_n=10):
        """计算遗漏值"""
        max_num = 35 if zone == 'front' else 12
        missing = {}
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
        """计算奇偶比例"""
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        odd_counts = []
        for record in recent_data:
            zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
            odd_count = sum(1 for num in zone_data if num % 2 == 1)
            odd_counts.append(odd_count / len(zone_data))
        return statistics.mean(odd_counts) if odd_counts else 0.5
    
    def calculate_sum_value(self, zone='front', last_n=20):
        """计算和值"""
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        sum_values = [sum(record['front_zone'] if zone == 'front' else record['back_zone']) for record in recent_data]
        if len(sum_values) < 2:
            return (sum(sum_values) if sum_values else 0, 0)
        return statistics.mean(sum_values), statistics.stdev(sum_values)
    
    def calculate_span(self, zone='front', last_n=20):
        """计算跨度"""
        recent_data = self.data[-last_n:] if len(self.data) >= last_n else self.data
        spans = []
        for record in recent_data:
            zone_data = record['front_zone'] if zone == 'front' else record['back_zone']
            spans.append(max(zone_data) - min(zone_data))
        if len(spans) < 2:
            return (statistics.mean(spans) if spans else 0, 0)
        return statistics.mean(spans), statistics.stdev(spans)
    
    def extract_all_features(self):
        """提取所有特征"""
        return {
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
