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
    获取合并后的彩票数据（用户数据 + 固定数据）

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
    try:
        # 导入固定数据
        from utils._lottery_data import lottery_data

        # 加载用户数据
        user_data = load_user_data()

        # 合并：用户数据在前，固定数据在后
        combined = user_data + lottery_data

        return combined

    except Exception as e:
        print(f"⚠️  加载合并数据失败: {str(e)}")
        # 回退到只返回固定数据
        try:
            from utils._lottery_data import lottery_data
            return lottery_data
        except:
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
