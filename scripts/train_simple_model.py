"""
简化的模型训练脚本
使用基于频率的统计方法
"""

import json
import pickle
import os
from collections import Counter
from datetime import datetime
from typing import Dict, List


class SimpleLotteryPredictor:
    """简化的彩票预测器"""
    
    def __init__(self):
        self.model = None
        
    def train_frequency_model(self, history_data: List[Dict], window_size: int = 100):
        """
        训练基于频率的模型
        
        这不是真正的机器学习，而是统计分析
        """
        print(f"\n🎓 开始训练模型（统计方法）")
        print(f"   使用最近 {window_size} 期数据")
        
        # 统计红球频率
        red_freq = Counter()
        blue_freq = Counter()
        
        # 只看最近的数据
        recent_data = history_data[:window_size]
        
        for record in recent_data:
            red_freq.update(record['red_balls'])
            blue_freq.update(record['blue_balls'])
        
        # 转化为概率
        total_red = sum(red_freq.values())
        total_blue = sum(blue_freq.values())
        
        red_prob = {num: count/total_red for num, count in red_freq.items()}
        blue_prob = {num: count/total_blue for num, count in blue_freq.items()}
        
        # 填充未出现的号码（设置最小概率）
        min_prob_red = 0.001
        min_prob_blue = 0.01
        
        for num in range(1, 36):  # 红球1-35
            if num not in red_prob:
                red_prob[num] = min_prob_red
        
        for num in range(1, 13):  # 蓝球1-12
            if num not in blue_prob:
                blue_prob[num] = min_prob_blue
        
        self.model = {
            'red_probabilities': red_prob,
            'blue_probabilities': blue_prob,
            'window_size': window_size,
            'trained_at': datetime.now().isoformat(),
            'data_range': {
                'start': recent_data[-1]['period'],
                'end': recent_data[0]['period']
            }
        }
        
        print(f"✅ 模型训练完成")
        return self.model
    
    def predict(self, model: Dict = None, top_n_red: int = 10, top_n_blue: int = 6) -> Dict:
        """
        进行预测
        
        Args:
            model: 训练好的模型（如果None则使用self.model）
            top_n_red: 返回前N个红球
            top_n_blue: 返回前N个蓝球
        """
        if model is None:
            model = self.model
        
        if model is None:
            raise ValueError("没有可用的模型，请先训练模型")
        
        # 按概率排序
        red_sorted = sorted(
            model['red_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        blue_sorted = sorted(
            model['blue_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        predictions = {
            'red': [
                {
                    'number': num,
                    'probability': prob,
                    'reason': self._get_reason(prob, 'red'),
                    'rank': i + 1
                }
                for i, (num, prob) in enumerate(red_sorted[:top_n_red])
            ],
            'blue': [
                {
                    'number': num,
                    'probability': prob,
                    'reason': self._get_reason(prob, 'blue'),
                    'rank': i + 1
                }
                for i, (num, prob) in enumerate(blue_sorted[:top_n_blue])
            ],
            'model_info': {
                'window_size': model['window_size'],
                'trained_at': model['trained_at']
            }
        }
        
        return predictions
    
    def _get_reason(self, probability: float, ball_type: str) -> str:
        """根据概率给出推荐理由"""
        if ball_type == 'red':
            if probability > 0.025:
                return "高频热号"
            elif probability > 0.02:
                return "中频温号"
            else:
                return "低频冷号"
        else:  # blue
            if probability > 0.1:
                return "高频热号"
            elif probability > 0.08:
                return "中频温号"
            else:
                return "低频冷号"
    
    def save_model(self, filepath: str, model: Dict = None):
        """保存模型"""
        if model is None:
            model = self.model
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"✅ 模型已保存到: {filepath}")
    
    def load_model(self, filepath: str) -> Dict:
        """加载模型"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"✅ 模型已加载: {filepath}")
        return self.model
    
    def evaluate_model(self, model: Dict, test_data: List[Dict]) -> Dict:
        """
        评估模型（娱乐性质）
        
        Args:
            model: 训练好的模型
            test_data: 测试数据集
        """
        print("\n📊 模型评估（仅供参考）")
        
        hits = {
            'red_exact': 0,  # 精确命中（号码和位置都对）
            'red_number': 0,  # 号码命中（不考虑位置）
            'blue_exact': 0,
            'blue_number': 0
        }
        
        for record in test_data[:10]:  # 只评估最近10期
            prediction = self.predict(model, top_n_red=5, top_n_blue=2)
            
            pred_red = [p['number'] for p in prediction['red'][:5]]
            pred_blue = [p['number'] for p in prediction['blue'][:2]]
            
            actual_red = record['red_balls']
            actual_blue = record['blue_balls']
            
            # 统计命中
            hits['red_number'] += len(set(pred_red) & set(actual_red))
            hits['blue_number'] += len(set(pred_blue) & set(actual_blue))
        
        print(f"   测试期数: {len(test_data[:10])}")
        print(f"   红球命中: {hits['red_number']}/{len(test_data[:10])*5} ({hits['red_number']/(len(test_data[:10])*5)*100:.1f}%)")
        print(f"   蓝球命中: {hits['blue_number']}/{len(test_data[:10])*2} ({hits['blue_number']/(len(test_data[:10])*2)*100:.1f}%)")
        print(f"   ⚠️  注意：命中率接近随机水平是正常的")
        
        return hits


def main():
    """主函数"""
    print("="*50)
    print("🤖 大乐透AI模型训练")
    print("="*50)
    
    # 读取历史数据
    data_file = 'data/raw/history.json'
    
    if not os.path.exists(data_file):
        print(f"\n❌ 数据文件不存在: {data_file}")
        print("   请先运行: python scripts/collect_data.py")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    print(f"\n📚 加载了 {len(history)} 期历史数据")
    
    # 创建预测器
    predictor = SimpleLotteryPredictor()
    
    # 训练模型
    model = predictor.train_frequency_model(history, window_size=100)
    
    # 保存模型
    model_file = 'data/models/frequency_model.pkl'
    predictor.save_model(model_file, model)
    
    # 同时保存为JSON格式（方便查看）
    json_file = 'data/models/model_info.json'
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'window_size': model['window_size'],
            'trained_at': model['trained_at'],
            'data_range': model['data_range']
        }, f, ensure_ascii=False, indent=2)
    
    # 进行预测
    print("\n🔮 生成预测...")
    predictions = predictor.predict(model)
    
    print("\n" + "="*50)
    print("推荐号码（基于最近100期频率）")
    print("="*50)
    
    print("\n🔴 红球推荐（前10）:")
    for pred in predictions['red']:
        print(f"   {pred['rank']:2d}. 号码 {pred['number']:02d} - {pred['reason']:8s} (概率: {pred['probability']:.4f})")
    
    print("\n🔵 蓝球推荐（前6）:")
    for pred in predictions['blue']:
        print(f"   {pred['rank']:2d}. 号码 {pred['number']:02d} - {pred['reason']:8s} (概率: {pred['probability']:.4f})")
    
    # 保存预测结果
    pred_file = 'data/predictions/latest_prediction.json'
    os.makedirs(os.path.dirname(pred_file), exist_ok=True)
    with open(pred_file, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 预测结果已保存到: {pred_file}")
    
    # 评估模型
    if len(history) > 10:
        test_data = history[:10]
        predictor.evaluate_model(model, test_data)
    
    print("\n" + "="*50)
    print("⚠️  免责声明")
    print("="*50)
    print("本预测仅基于历史频率统计，不能提高中奖概率。")
    print("彩票是随机事件，请理性购买。")
    print("本项目仅用于AI技术学习和科普。")


if __name__ == '__main__':
    main()
