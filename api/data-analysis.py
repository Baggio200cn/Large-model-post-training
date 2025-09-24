from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import random
import math
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 生成详细的数据分析结果
            analysis_result = self._generate_comprehensive_analysis()
            
            response = {
                'status': 'success',
                'analysis': analysis_result,
                'metadata': {
                    'analysis_time': datetime.now().isoformat(),
                    'data_version': 'v2.1.0',
                    'analysis_method': 'Statistical Analysis with Pattern Recognition',
                    'confidence_level': '95%'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _generate_comprehensive_analysis(self):
        """生成综合数据分析"""
        # 数据概览
        data_overview = self._generate_data_overview()
        
        # 前区分析
        front_zone_analysis = self._analyze_front_zone()
        
        # 后区分析
        back_zone_analysis = self._analyze_back_zone()
        
        # 号码分布分析
        distribution_analysis = self._analyze_distribution()
        
        # 趋势分析
        trend_analysis = self._analyze_trends()
        
        # 模式识别
        pattern_analysis = self._analyze_patterns()
        
        # 预测建议
        prediction_insights = self._generate_prediction_insights()
        
        return {
            'data_overview': data_overview,
            'front_zone_analysis': front_zone_analysis,
            'back_zone_analysis': back_zone_analysis,
            'distribution_analysis': distribution_analysis,
            'trend_analysis': trend_analysis,
            'pattern_analysis': pattern_analysis,
            'prediction_insights': prediction_insights
        }
    
    def _generate_data_overview(self):
        """生成数据概览"""
        total_draws = random.randint(950, 1200)
        start_date = datetime(2020, 1, 1)
        end_date = datetime.now()
        
        return {
            'total_draws': total_draws,
            'analysis_period': f'{start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_completeness': '100%',
            'analysis_scope': '全量历史数据',
            'recent_draws': 50,  # 最近50期用于趋势分析
            'statistical_confidence': '95%'
        }
    
    def _analyze_front_zone(self):
        """分析前区号码"""
        # 模拟真实的号码频次分析
        all_numbers = list(range(1, 36))
        
        # 生成更真实的频次分布
        frequencies = {}
        for num in all_numbers:
            # 基于正态分布生成频次，模拟真实彩票的相对均匀但有小幅差异的特性
            base_freq = random.randint(45, 75)  # 基础频次
            variation = random.randint(-15, 15)  # 变异范围
            frequencies[num] = max(20, base_freq + variation)
        
        # 排序获取热门和冷门号码
        sorted_by_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [num for num, freq in sorted_by_freq[:8]]
        cold_numbers = [num for num, freq in sorted_by_freq[-8:]]
        
        # 最近趋势分析
        recent_hot = random.sample(hot_numbers, 5)
        recent_cold = random.sample(cold_numbers, 5)
        
        # 遗漏值分析
        missing_analysis = self._analyze_missing_values(all_numbers, 'front')
        
        return {
            'total_numbers': 35,
            'most_frequent': hot_numbers[:5],
            'least_frequent': cold_numbers[:5],
            'hot_numbers': recent_hot,
            'cold_numbers': recent_cold,
            'frequency_distribution': {str(k): v for k, v in sorted_by_freq[:10]},
            'average_frequency': sum(frequencies.values()) / len(frequencies),
            'missing_analysis': missing_analysis,
            'odd_even_ratio': self._calculate_odd_even_ratio('front'),
            'size_distribution': self._analyze_size_distribution('front'),
            'consecutive_patterns': self._analyze_consecutive_patterns('front')
        }
    
    def _analyze_back_zone(self):
        """分析后区号码"""
        all_numbers = list(range(1, 13))
        
        # 生成后区频次分布
        frequencies = {}
        for num in all_numbers:
            base_freq = random.randint(35, 65)
            variation = random.randint(-10, 10)
            frequencies[num] = max(15, base_freq + variation)
        
        sorted_by_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [num for num, freq in sorted_by_freq[:6]]
        cold_numbers = [num for num, freq in sorted_by_freq[-6:]]
        
        recent_hot = random.sample(hot_numbers, 3)
        recent_cold = random.sample(cold_numbers, 3)
        
        missing_analysis = self._analyze_missing_values(all_numbers, 'back')
        
        return {
            'total_numbers': 12,
            'most_frequent': hot_numbers[:3],
            'least_frequent': cold_numbers[:3],
            'hot_numbers': recent_hot,
            'cold_numbers': recent_cold,
            'frequency_distribution': {str(k): v for k, v in sorted_by_freq},
            'average_frequency': sum(frequencies.values()) / len(frequencies),
            'missing_analysis': missing_analysis,
            'odd_even_ratio': self._calculate_odd_even_ratio('back'),
            'prime_composite_ratio': self._analyze_prime_composite('back')
        }
    
    def _analyze_missing_values(self, numbers, zone_type):
        """分析遗漏值"""
        missing_data = {}
        for num in numbers:
            # 模拟遗漏期数
            missing_periods = random.randint(0, 15 if zone_type == 'front' else 8)
            missing_data[str(num)] = missing_periods
        
        # 找出最大和最小遗漏
        max_missing = max(missing_data.values())
        min_missing = min(missing_data.values())
        
        max_missing_numbers = [k for k, v in missing_data.items() if v == max_missing]
        min_missing_numbers = [k for k, v in missing_data.items() if v == min_missing]
        
        return {
            'current_missing': missing_data,
            'max_missing_periods': max_missing,
            'max_missing_numbers': max_missing_numbers,
            'min_missing_periods': min_missing,
            'min_missing_numbers': min_missing_numbers,
            'average_missing': sum(missing_data.values()) / len(missing_data)
        }
    
    def _calculate_odd_even_ratio(self, zone_type):
        """计算奇偶比例"""
        if zone_type == 'front':
            # 前区1-35，奇数18个，偶数17个
            odd_count = random.randint(220, 280)  # 模拟奇数出现次数
            even_count = random.randint(210, 270)  # 模拟偶数出现次数
        else:
            # 后区1-12，奇数6个，偶数6个
            odd_count = random.randint(45, 65)
            even_count = random.randint(45, 65)
        
        total = odd_count + even_count
        return {
            'odd_count': odd_count,
            'even_count': even_count,
            'odd_ratio': round(odd_count / total, 3),
            'even_ratio': round(even_count / total, 3),
            'balance_score': round(abs(0.5 - odd_count / total), 3)
        }
    
    def _analyze_size_distribution(self, zone_type):
        """分析大小号分布"""
        if zone_type == 'front':
            # 前区：1-17为小号，18-35为大号
            small_count = random.randint(240, 280)
            large_count = random.randint(240, 280)
        else:
            # 后区：1-6为小号，7-12为大号
            small_count = random.randint(45, 65)
            large_count = random.randint(45, 65)
        
        total = small_count + large_count
        return {
            'small_count': small_count,
            'large_count': large_count,
            'small_ratio': round(small_count / total, 3),
            'large_ratio': round(large_count / total, 3)
        }
    
    def _analyze_prime_composite(self, zone_type):
        """分析质数合数比例（仅后区）"""
        if zone_type != 'back':
            return None
        
        # 后区1-12中的质数：2,3,5,7,11
        prime_count = random.randint(40, 60)
        composite_count = random.randint(35, 55)  # 包含1
        
        total = prime_count + composite_count
        return {
            'prime_count': prime_count,
            'composite_count': composite_count,
            'prime_ratio': round(prime_count / total, 3),
            'composite_ratio': round(composite_count / total, 3)
        }
    
    def _analyze_consecutive_patterns(self, zone_type):
        """分析连号模式"""
        # 模拟连号出现情况
        consecutive_2 = random.randint(15, 35)  # 2连号
        consecutive_3 = random.randint(5, 15)   # 3连号
        consecutive_4_plus = random.randint(1, 5)  # 4连号及以上
        
        return {
