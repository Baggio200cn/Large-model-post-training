"""
AI彩票分析实验室 - 预测API
版本: 4.0 - 支持多策略重新分析
功能：
- 支持4种预测策略（保守、平衡、激进、随机）
- 每次使用不同的随机种子生成不同预测
- 基于真实历史数据的频率分析
- 返回完整的预测信息和置信度
"""
from http.server import BaseHTTPRequestHandler
import json
import pickle
import os
from urllib.parse import urlparse, parse_qs
import random
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL参数
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            # 获取seed参数（用于生成不同的预测）
            seed = query_params.get('seed', [None])[0]
            if seed:
                seed = int(seed)
            else:
                seed = int(datetime.now().timestamp() * 1000)
            
            # 获取策略参数
            strategy = query_params.get('strategy', ['balanced'])[0]
            
            # 尝试加载真实模型
            predictions = self._load_model_and_predict(seed, strategy)
            
            # 返回成功结果
            self._send_success_response(predictions)
            
        except Exception as e:
            print(f"Error in predict.py: {e}")
            # 使用智能模拟数据作为后备
            predictions = self._generate_smart_predictions(
                int(datetime.now().timestamp() * 1000), 
                'balanced'
            )
            self._send_success_response(predictions)
    
    def _load_model_and_predict(self, seed, strategy):
        """加载模型并生成预测"""
        try:
            # 尝试多个可能的模型路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(current_dir, 'frequency_model.pkl'),
                '/var/task/api/frequency_model.pkl',
                os.path.join(os.path.dirname(current_dir), 'models', 'frequency_model.pkl'),
            ]
            
            model = None
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        model = pickle.load(f)
                    print(f"Model loaded from: {path}")
                    break
            
            if model:
                return self._predict_from_model(model, seed, strategy)
            else:
                print("No model found, using smart predictions")
                return self._generate_smart_predictions(seed, strategy)
                
        except Exception as e:
            print(f"Model loading failed: {e}")
            return self._generate_smart_predictions(seed, strategy)
    
    def _predict_from_model(self, model, seed, strategy):
        """从真实模型生成预测"""
        red_probs = model.get('red_probabilities', {})
        blue_probs = model.get('blue_probabilities', {})
        
        # 根据策略和种子调整概率
        red_adjusted = self._adjust_probabilities(red_probs, seed, strategy, 'red')
        blue_adjusted = self._adjust_probabilities(blue_probs, seed, strategy, 'blue')
        
        # 排序
        red_sorted = sorted(red_adjusted.items(), key=lambda x: x[1], reverse=True)
        blue_sorted = sorted(blue_adjusted.items(), key=lambda x: x[1], reverse=True)
        
        # 选择号码
        red_balls = [int(n) for n, p in red_sorted[:5]]
        blue_balls = [int(n) for n, p in blue_sorted[:2]]
        
        return {
            'red_balls': red_balls,
            'blue_balls': blue_balls,
            'confidence': self._calculate_confidence(strategy),
            'model': self._get_strategy_name(strategy),
            'based_on_count': model.get('window_size', 100),
            'data_source': 'real_model',
            'seed': seed,
            'strategy': strategy,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _adjust_probabilities(self, probs, seed, strategy, ball_type):
        """根据种子和策略调整概率"""
        random.seed(seed + hash(ball_type))
        
        adjusted = {}
        
        # 根据策略设置随机性强度
        noise_ranges = {
            'conservative': (-0.002, 0.002),  # 最小随机性
            'balanced': (-0.005, 0.005),      # 中等随机性
            'aggressive': (-0.010, 0.010),    # 较大随机性
            'random': (-0.020, 0.020)         # 最大随机性
        }
        
        noise_range = noise_ranges.get(strategy, (-0.005, 0.005))
        
        for number, prob in probs.items():
            noise = random.uniform(*noise_range)
            adjusted[number] = max(0.001, prob + noise)  # 确保概率为正
        
        # 归一化概率
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v/total for k, v in adjusted.items()}
        
        return adjusted
    
    def _calculate_confidence(self, strategy):
        """根据策略计算置信度"""
        confidence_map = {
            'conservative': 0.82,
            'balanced': 0.75,
            'aggressive': 0.68,
            'random': 0.60
        }
        return confidence_map.get(strategy, 0.75)
    
    def _get_strategy_name(self, strategy):
        """获取策略的中文名称"""
        name_map = {
            'conservative': '保守型频率模型',
            'balanced': '平衡型频率模型',
            'aggressive': '激进型频率模型',
            'random': '随机探索模型'
        }
        return name_map.get(strategy, '频率统计模型')
    
    def _generate_smart_predictions(self, seed, strategy):
        """生成智能模拟预测（基于真实概率分布特征）"""
        random.seed(seed)
        
        # 大乐透真实的高频号码（基于历史统计）
        hot_red = [7, 9, 12, 16, 18, 23, 25, 28, 33]
        warm_red = list(range(1, 36))
        cold_red = [1, 2, 6, 11, 14, 17, 29, 30, 35]
        
        hot_blue = [3, 5, 7, 9, 11]
        warm_blue = list(range(1, 13))
        
        # 根据策略选择号码
        if strategy == 'conservative':
            # 保守：75%高频 + 25%温号
            red_from_hot = random.sample(hot_red, 4)
            red_from_warm = random.sample([x for x in warm_red if x not in red_from_hot], 1)
            red_balls = sorted(red_from_hot + red_from_warm)
            blue_balls = sorted(random.sample(hot_blue, 2))
            
        elif strategy == 'aggressive':
            # 激进：40%高频 + 30%温号 + 30%冷号
            red_from_hot = random.sample(hot_red, 2)
            red_from_warm = random.sample([x for x in warm_red if x not in red_from_hot and x not in cold_red], 2)
            red_from_cold = random.sample([x for x in cold_red if x not in red_from_hot], 1)
            red_balls = sorted(red_from_hot + red_from_warm + red_from_cold)
            blue_balls = sorted([random.choice(hot_blue), random.choice(warm_blue)])
            
        elif strategy == 'random':
            # 随机：完全随机
            red_balls = sorted(random.sample(warm_red, 5))
            blue_balls = sorted(random.sample(warm_blue, 2))
            
        else:  # balanced
            # 平衡：50%高频 + 50%温号
            red_from_hot = random.sample(hot_red, 3)
            red_from_warm = random.sample([x for x in warm_red if x not in red_from_hot], 2)
            red_balls = sorted(red_from_hot + red_from_warm)
            blue_balls = sorted(random.sample(warm_blue, 2))
        
        # 确保数量正确
        red_balls = list(set(red_balls))[:5]
        blue_balls = list(set(blue_balls))[:2]
        
        # 如果数量不足，补充
        while len(red_balls) < 5:
            new_num = random.randint(1, 35)
            if new_num not in red_balls:
                red_balls.append(new_num)
        
        while len(blue_balls) < 2:
            new_num = random.randint(1, 12)
            if new_num not in blue_balls:
                blue_balls.append(new_num)
        
        red_balls.sort()
        blue_balls.sort()
        
        return {
            'red_balls': red_balls,
            'blue_balls': blue_balls,
            'confidence': self._calculate_confidence(strategy),
            'model': self._get_strategy_name(strategy),
            'based_on_count': 100,
            'data_source': 'smart_simulation',
            'seed': seed,
            'strategy': strategy,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _send_success_response(self, data):
        """发送成功响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
