# -*- coding: utf-8 -*-
"""
共享数据加载模块
用于在所有API之间共享数据加载逻辑
"""
import os
import json
from typing import List, Dict, Any


# 用户数据文件路径
USER_DATA_FILE = '/tmp/user_lottery_data.json'


def load_user_data() -> List[Dict[str, Any]]:
    """加载用户添加的数据"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def get_combined_lottery_data() -> List[Dict[str, Any]]:
    """
    获取合并后的彩票数据（优先级：COS云存储 > 本地用户数据 > 固定数据）

    Returns:
        合并后的数据列表，格式：
        [
            {
                'period': '26010',
                'date': '2026-01-24',
                'front_zone': [26, 3, 13, 18, 2],
                'back_zone': [2, 9]
            },
            ...
        ]
    """
    # 优先级1: 尝试从腾讯云COS加载（最新且持久化的数据）
    try:
        from utils._cos_data_loader import get_lottery_data
        cos_data = get_lottery_data()
        if cos_data and isinstance(cos_data, list) and len(cos_data) > 0:
            print(f"✅ 使用COS云端数据: {len(cos_data)} 期")
            return cos_data
    except Exception as e:
        print(f"⚠️  COS加载失败: {str(e)}，尝试本地数据")

    # 优先级2: 使用本地数据（用户数据 + 固定数据）
    try:
        # 导入固定数据
        from utils._lottery_data import lottery_data

        # 加载用户数据（可能存在于/tmp，但在Serverless环境下不可靠）
        user_data = load_user_data()

        # 合并：用户数据在前，固定数据在后
        combined = user_data + lottery_data

        print(f"ℹ️  使用本地合并数据: {len(combined)} 期 (用户:{len(user_data)}, 固定:{len(lottery_data)})")
        return combined

    except Exception as e:
        print(f"⚠️  加载合并数据失败: {str(e)}")
        # 优先级3: 回退到只返回固定数据
        try:
            from utils._lottery_data import lottery_data
            print(f"⚠️  使用备份固定数据: {len(lottery_data)} 期")
            return lottery_data
        except:
            print("❌ 所有数据源都失败")
            return []


def save_user_data(data: List[Dict[str, Any]]) -> bool:
    """保存用户添加的数据"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存用户数据失败: {str(e)}")
        return False
