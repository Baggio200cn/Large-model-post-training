"""
准备机器学习训练数据
从历史开奖数据中提取特征和标签
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import json
import pickle
import numpy as np
from datetime import datetime
from _lottery_data import LOTTERY_HISTORY


def parse_lottery_data():
    """解析彩票历史数据"""
    data = []
    for record in LOTTERY_HISTORY:
        if len(record) < 9:
            continue

        period = record[0]
        front_zone = [record[1], record[2], record[3], record[4], record[5]]
        back_zone = [record[6], record[7]]
        date = record[8] if len(record) > 8 else ""

        data.append({
            'period': period,
            'front_zone': sorted(front_zone),
            'back_zone': sorted(back_zone),
            'date': date
        })

    return data


def extract_features(data, window_size=10):
    """
    提取机器学习特征

    特征包括：
    - 最近N期的号码出现频率
    - 号码遗漏期数
    - 奇偶比例
    - 大小比例
    - 和值统计
    - AC值（离散度）
    """
    features = []
    labels_front = []
    labels_back = []

    for i in range(window_size, len(data)):
        # 获取历史窗口数据
        window = data[i-window_size:i]
        target = data[i]

        # 提取前区特征
        front_freq = np.zeros(35)  # 1-35号频率
        front_missing = np.zeros(35)  # 遗漏期数

        for j, record in enumerate(reversed(window)):
            for num in record['front_zone']:
                front_freq[num-1] += 1
                if front_missing[num-1] == 0:
                    front_missing[num-1] = j

        # 未出现号码的遗漏设为window_size
        front_missing[front_missing == 0] = window_size

        # 提取后区特征
        back_freq = np.zeros(12)  # 1-12号频率
        back_missing = np.zeros(12)

        for j, record in enumerate(reversed(window)):
            for num in record['back_zone']:
                back_freq[num-1] += 1
                if back_missing[num-1] == 0:
                    back_missing[num-1] = j

        back_missing[back_missing == 0] = window_size

        # 统计特征
        recent_front = [num for record in window for num in record['front_zone']]
        recent_back = [num for record in window for num in record['back_zone']]

        # 奇偶比例
        odd_ratio_front = sum(1 for n in recent_front if n % 2 == 1) / len(recent_front)
        odd_ratio_back = sum(1 for n in recent_back if n % 2 == 1) / len(recent_back)

        # 大小比例（前区：18以上为大，后区：7以上为大）
        big_ratio_front = sum(1 for n in recent_front if n > 18) / len(recent_front)
        big_ratio_back = sum(1 for n in recent_back if n > 6) / len(recent_back)

        # 和值统计
        sum_values_front = [sum(record['front_zone']) for record in window]
        sum_mean_front = np.mean(sum_values_front)
        sum_std_front = np.std(sum_values_front)

        sum_values_back = [sum(record['back_zone']) for record in window]
        sum_mean_back = np.mean(sum_values_back)
        sum_std_back = np.std(sum_values_back)

        # 组合所有特征
        feature_vector = np.concatenate([
            front_freq / window_size,  # 归一化频率 (35维)
            front_missing / window_size,  # 归一化遗漏 (35维)
            back_freq / window_size,  # 归一化频率 (12维)
            back_missing / window_size,  # 归一化遗漏 (12维)
            [odd_ratio_front, odd_ratio_back],  # 奇偶比例 (2维)
            [big_ratio_front, big_ratio_back],  # 大小比例 (2维)
            [sum_mean_front / 180, sum_std_front / 50],  # 前区和值统计 (2维)
            [sum_mean_back / 24, sum_std_back / 10],  # 后区和值统计 (2维)
        ])

        features.append(feature_vector)

        # 标签：转换为multi-hot编码
        front_label = np.zeros(35)
        for num in target['front_zone']:
            front_label[num-1] = 1

        back_label = np.zeros(12)
        for num in target['back_zone']:
            back_label[num-1] = 1

        labels_front.append(front_label)
        labels_back.append(back_label)

    return np.array(features), np.array(labels_front), np.array(labels_back)


def save_training_data(features, labels_front, labels_back, output_dir='data/training'):
    """保存训练数据"""
    os.makedirs(output_dir, exist_ok=True)

    # 分割训练集和测试集（80/20）
    split_idx = int(len(features) * 0.8)

    train_data = {
        'X_train': features[:split_idx],
        'y_front_train': labels_front[:split_idx],
        'y_back_train': labels_back[:split_idx],
        'X_test': features[split_idx:],
        'y_front_test': labels_front[split_idx:],
        'y_back_test': labels_back[split_idx:],
        'feature_dim': features.shape[1],
        'created_at': datetime.now().isoformat()
    }

    # 保存为pickle
    with open(f'{output_dir}/training_data.pkl', 'wb') as f:
        pickle.dump(train_data, f)

    # 保存元数据
    metadata = {
        'total_samples': len(features),
        'train_samples': split_idx,
        'test_samples': len(features) - split_idx,
        'feature_dim': features.shape[1],
        'front_zone_classes': 35,
        'back_zone_classes': 12,
        'created_at': train_data['created_at']
    }

    with open(f'{output_dir}/metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return train_data, metadata


def main():
    print("=" * 60)
    print("准备机器学习训练数据")
    print("=" * 60)

    # 解析数据
    print("\n📚 解析历史开奖数据...")
    data = parse_lottery_data()
    print(f"   共 {len(data)} 期历史数据")

    # 提取特征
    print("\n🔧 提取机器学习特征...")
    features, labels_front, labels_back = extract_features(data, window_size=10)
    print(f"   特征维度: {features.shape}")
    print(f"   前区标签维度: {labels_front.shape}")
    print(f"   后区标签维度: {labels_back.shape}")

    # 保存数据
    print("\n💾 保存训练数据...")
    train_data, metadata = save_training_data(features, labels_front, labels_back)

    print("\n✅ 数据准备完成！")
    print(f"   训练样本: {metadata['train_samples']}")
    print(f"   测试样本: {metadata['test_samples']}")
    print(f"   特征维度: {metadata['feature_dim']}")
    print(f"   数据保存在: data/training/")

    return train_data, metadata


if __name__ == '__main__':
    main()
