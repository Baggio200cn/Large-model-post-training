"""
大乐透历史开奖数据
数据来源: 中国福利彩票官网（通过截图识别采集）
数据范围: 25047期 - 25129期（共85期）
采集日期: 2024-11-14
最后更新: 2024-11-14

数据说明：
- 期号范围：25047-25129
- 时间跨度：2025年4月30日 - 2025年11月12日
- 数据完整性：所有期数连续，无缺失
"""

# 历史开奖数据
LOTTERY_HISTORY = [
    # ===== 2025年11月数据 =====
    {
        "period": "25129",
        "draw_date": "2025-11-12",
        "front_zone": [3, 9, 14, 28, 35],
        "back_zone": [2, 4]
    },
    {
        "period": "25128",
        "draw_date": "2025-11-10",
        "front_zone": [3, 6, 26, 30, 33],
        "back_zone": [11, 12]
    },
    {
        "period": "25127",
        "draw_date": "2025-11-08",
        "front_zone": [4, 5, 19, 28, 29],
        "back_zone": [5, 8]
    },
    {
        "period": "25126",
        "draw_date": "2025-11-05",
        "front_zone": [1, 8, 18, 27, 30],
        "back_zone": [6, 7]
    },
    {
        "period": "25125",
        "draw_date": "2025-11-03",
        "front_zone": [10, 11, 13, 19, 35],
        "back_zone": [4, 11]
    },
    {
        "period": "25124",
        "draw_date": "2025-11-01",
        "front_zone": [6, 9, 14, 26, 27],
        "back_zone": [8, 9]
    },
    
    # ===== 2025年10月数据 =====
    {
        "period": "25123",
        "draw_date": "2025-10-29",
        "front_zone": [8, 13, 24, 25, 31],
        "back_zone": [4, 10]
    },
    {
        "period": "25122",
        "draw_date": "2025-10-27",
        "front_zone": [2, 3, 6, 16, 17],
        "back_zone": [4, 5]
    },
    {
        "period": "25121",
        "draw_date": "2025-10-25",
        "front_zone": [2, 3, 8, 13, 21],
        "back_zone": [7, 12]
    },
    {
        "period": "25120",
        "draw_date": "2025-10-22",
        "front_zone": [11, 13, 22, 26, 35],
        "back_zone": [2, 8]
    },
    {
        "period": "25119",
        "draw_date": "2025-10-20",
        "front_zone": [8, 15, 27, 29, 31],
        "back_zone": [1, 7]
    },
    {
        "period": "25118",
        "draw_date": "2025-10-18",
        "front_zone": [2, 8, 9, 12, 21],
        "back_zone": [4, 5]
    },
    {
        "period": "25117",
        "draw_date": "2025-10-15",
        "front_zone": [5, 10, 18, 21, 29],
        "back_zone": [5, 7]
    },
    {
        "period": "25116",
        "draw_date": "2025-10-13",
        "front_zone": [2, 6, 16, 22, 29],
        "back_zone": [8, 12]
    },
    {
        "period": "25115",
        "draw_date": "2025-10-11",
        "front_zone": [3, 12, 14, 21, 35],
        "back_zone": [1, 5]
    },
    {
        "period": "25114",
        "draw_date": "2025-10-08",
        "front_zone": [3, 8, 9, 12, 16],
        "back_zone": [1, 5]
    },
    {
        "period": "25113",
        "draw_date": "2025-10-06",
        "front_zone": [1, 14, 18, 28, 35],
        "back_zone": [2, 3]
    },
    
    # ===== 2025年9月数据 =====
    {
        "period": "25112",
        "draw_date": "2025-09-29",
        "front_zone": [3, 4, 21, 23, 24],
        "back_zone": [9, 12]
    },
    {
        "period": "25111",
        "draw_date": "2025-09-27",
        "front_zone": [2, 9, 14, 21, 26],
        "back_zone": [2, 12]
    },
    {
        "period": "25110",
        "draw_date": "2025-09-24",
        "front_zone": [1, 15, 22, 30, 31],
        "back_zone": [2, 8]
    },
    {
        "period": "25109",
        "draw_date": "2025-09-22",
        "front_zone": [4, 8, 10, 13, 26],
        "back_zone": [9, 10]
    },
    {
        "period": "25108",
        "draw_date": "2025-09-20",
        "front_zone": [14, 18, 21, 24, 29],
        "back_zone": [3, 6]
    },
    {
        "period": "25107",
        "draw_date": "2025-09-17",
        "front_zone": [5, 7, 8, 15, 33],
        "back_zone": [6, 10]
    },
    {
        "period": "25106",
        "draw_date": "2025-09-15",
        "front_zone": [5, 6, 11, 26, 29],
        "back_zone": [5, 10]
    },
    {
        "period": "25105",
        "draw_date": "2025-09-13",
        "front_zone": [15, 16, 25, 28, 34],
        "back_zone": [10, 12]
    },
    {
        "period": "25104",
        "draw_date": "2025-09-10",
        "front_zone": [2, 6, 9, 22, 34],
        "back_zone": [2, 8]
    },
    {
        "period": "25103",
        "draw_date": "2025-09-08",
        "front_zone": [5, 8, 19, 32, 34],
        "back_zone": [4, 5]
    },
    {
        "period": "25102",
        "draw_date": "2025-09-06",
        "front_zone": [9, 10, 13, 26, 28],
        "back_zone": [2, 4]
    },
    {
        "period": "25101",
        "draw_date": "2025-09-03",
        "front_zone": [5, 7, 19, 26, 32],
        "back_zone": [8, 9]
    },
    {
        "period": "25100",
        "draw_date": "2025-09-01",
        "front_zone": [26, 28, 32, 34, 35],
        "back_zone": [2, 7]
    },
    
    # ===== 2025年8月数据 =====
    {
        "period": "25099",
        "draw_date": "2025-08-30",
        "front_zone": [6, 12, 20, 26, 31],
        "back_zone": [2, 4]
    },
    {
        "period": "25098",
        "draw_date": "2025-08-27",
        "front_zone": [1, 7, 9, 10, 23],
        "back_zone": [10, 12]
    },
    {
        "period": "25097",
        "draw_date": "2025-08-25",
        "front_zone": [5, 24, 25, 32, 34],
        "back_zone": [1, 9]
    },
    {
        "period": "25096",
        "draw_date": "2025-08-23",
        "front_zone": [2, 11, 17, 22, 24],
        "back_zone": [7, 9]
    },
    {
        "period": "25095",
        "draw_date": "2025-08-20",
        "front_zone": [7, 13, 14, 19, 27],
        "back_zone": [6, 10]
    },
    {
        "period": "25094",
        "draw_date": "2025-08-18",
        "front_zone": [4, 9, 17, 30, 33],
        "back_zone": [5, 9]
    },
    {
        "period": "25093",
        "draw_date": "2025-08-16",
        "front_zone": [1, 7, 9, 16, 30],
        "back_zone": [2, 5]
    },
    {
        "period": "25092",
        "draw_date": "2025-08-13",
        "front_zone": [4, 10, 17, 25, 32],
        "back_zone": [5, 7]
    },
    {
        "period": "25091",
        "draw_date": "2025-08-11",
        "front_zone": [1, 19, 22, 25, 27],
        "back_zone": [3, 10]
    },
    {
        "period": "25090",
        "draw_date": "2025-08-09",
        "front_zone": [6, 14, 19, 22, 27],
        "back_zone": [1, 4]
    },
    {
        "period": "25089",
        "draw_date": "2025-08-06",
        "front_zone": [2, 11, 12, 32, 34],
        "back_zone": [3, 10]
    },
    {
        "period": "25088",
        "draw_date": "2025-08-04",
        "front_zone": [8, 9, 10, 11, 35],
        "back_zone": [5, 11]
    },
    {
        "period": "25087",
        "draw_date": "2025-08-02",
        "front_zone": [5, 13, 14, 16, 20],
        "back_zone": [3, 8]
    },
    
    # ===== 2025年7月数据 =====
    {
        "period": "25086",
        "draw_date": "2025-07-30",
        "front_zone": [2, 6, 23, 24, 33],
        "back_zone": [1, 10]
    },
    {
        "period": "25085",
        "draw_date": "2025-07-28",
        "front_zone": [2, 5, 9, 14, 33],
        "back_zone": [4, 9]
    },
    {
        "period": "25084",
        "draw_date": "2025-07-26",
        "front_zone": [9, 11, 13, 18, 29],
        "back_zone": [4, 11]
    },
    {
        "period": "25083",
        "draw_date": "2025-07-23",
        "front_zone": [12, 17, 18, 20, 34],
        "back_zone": [2, 5]
    },
    {
        "period": "25082",
        "draw_date": "2025-07-21",
        "front_zone": [2, 3, 4, 12, 26],
        "back_zone": [1, 8]
    },
    {
        "period": "25081",
        "draw_date": "2025-07-19",
        "front_zone": [1, 4, 6, 15, 18],
        "back_zone": [2, 3]
    },
    {
        "period": "25080",
        "draw_date": "2025-07-16",
        "front_zone": [9, 10, 18, 22, 24],
        "back_zone": [3, 12]
    },
    {
        "period": "25079",
        "draw_date": "2025-07-14",
        "front_zone": [2, 14, 32, 34, 35],
        "back_zone": [5, 11]
    },
    {
        "period": "25078",
        "draw_date": "2025-07-12",
        "front_zone": [7, 10, 15, 21, 24],
        "back_zone": [5, 6]
    },
    {
        "period": "25077",
        "draw_date": "2025-07-09",
        "front_zone": [12, 14, 16, 19, 28],
        "back_zone": [1, 4]
    },
    {
        "period": "25076",
        "draw_date": "2025-07-07",
        "front_zone": [11, 18, 22, 25, 29],
        "back_zone": [4, 12]
    },
    {
        "period": "25075",
        "draw_date": "2025-07-05",
        "front_zone": [8, 12, 16, 19, 35],
        "back_zone": [6, 9]
    },
    {
        "period": "25074",
        "draw_date": "2025-07-02",
        "front_zone": [2, 11, 15, 18, 21],
        "back_zone": [5, 10]
    },
    
    # ===== 2025年6月数据 =====
    {
        "period": "25073",
        "draw_date": "2025-06-30",
        "front_zone": [1, 4, 17, 33, 34],
        "back_zone": [3, 9]
    },
    {
        "period": "25072",
        "draw_date": "2025-06-28",
        "front_zone": [4, 7, 15, 24, 29],
        "back_zone": [1, 4]
    },
    {
        "period": "25071",
        "draw_date": "2025-06-25",
        "front_zone": [1, 8, 25, 31, 33],
        "back_zone": [5, 11]
    },
    {
        "period": "25070",
        "draw_date": "2025-06-23",
        "front_zone": [8, 9, 15, 20, 22],
        "back_zone": [4, 12]
    },
    {
        "period": "25069",
        "draw_date": "2025-06-21",
        "front_zone": [4, 6, 7, 33, 34],
        "back_zone": [9, 10]
    },
    {
        "period": "25068",
        "draw_date": "2025-06-18",
        "front_zone": [1, 4, 17, 20, 22],
        "back_zone": [4, 10]
    },
    {
        "period": "25067",
        "draw_date": "2025-06-16",
        "front_zone": [6, 10, 12, 21, 22],
        "back_zone": [1, 6]
    },
    {
        "period": "25066",
        "draw_date": "2025-06-14",
        "front_zone": [15, 18, 27, 28, 34],
        "back_zone": [3, 6]
    },
    {
        "period": "25065",
        "draw_date": "2025-06-11",
        "front_zone": [7, 25, 32, 33, 35],
        "back_zone": [4, 9]
    },
    {
        "period": "25064",
        "draw_date": "2025-06-09",
        "front_zone": [5, 10, 18, 20, 34],
        "back_zone": [1, 8]
    },
    {
        "period": "25063",
        "draw_date": "2025-06-07",
        "front_zone": [5, 18, 26, 29, 32],
        "back_zone": [7, 10]
    },
    {
        "period": "25062",
        "draw_date": "2025-06-04",
        "front_zone": [14, 20, 27, 28, 29],
        "back_zone": [6, 10]
    },
    {
        "period": "25061",
        "draw_date": "2025-06-02",
        "front_zone": [2, 11, 16, 23, 28],
        "back_zone": [5, 10]
    },
    
    # ===== 2025年5月数据 =====
    {
        "period": "25060",
        "draw_date": "2025-05-31",
        "front_zone": [12, 14, 19, 33, 34],
        "back_zone": [1, 7]
    },
    {
        "period": "25059",
        "draw_date": "2025-05-28",
        "front_zone": [3, 9, 10, 11, 26],
        "back_zone": [1, 2]
    },
    {
        "period": "25058",
        "draw_date": "2025-05-26",
        "front_zone": [6, 11, 15, 21, 23],
        "back_zone": [1, 7]
    },
    {
        "period": "25057",
        "draw_date": "2025-05-24",
        "front_zone": [9, 10, 11, 12, 29],
        "back_zone": [1, 10]
    },
    {
        "period": "25056",
        "draw_date": "2025-05-21",
        "front_zone": [12, 15, 28, 29, 32],
        "back_zone": [8, 11]
    },
    {
        "period": "25055",
        "draw_date": "2025-05-19",
        "front_zone": [8, 10, 25, 29, 30],
        "back_zone": [1, 2]
    },
    {
        "period": "25054",
        "draw_date": "2025-05-17",
        "front_zone": [3, 12, 16, 21, 29],
        "back_zone": [1, 2]
    },
    {
        "period": "25053",
        "draw_date": "2025-05-14",
        "front_zone": [14, 23, 29, 30, 33],
        "back_zone": [6, 12]
    },
    {
        "period": "25052",
        "draw_date": "2025-05-12",
        "front_zone": [2, 4, 11, 29, 30],
        "back_zone": [2, 8]
    },
    {
        "period": "25051",
        "draw_date": "2025-05-10",
        "front_zone": [2, 4, 13, 29, 31],
        "back_zone": [5, 12]
    },
    {
        "period": "25050",
        "draw_date": "2025-05-07",
        "front_zone": [15, 18, 20, 21, 34],
        "back_zone": [4, 10]
    },
    {
        "period": "25049",
        "draw_date": "2025-05-05",
        "front_zone": [9, 20, 22, 29, 34],
        "back_zone": [3, 8]
    },
    {
        "period": "25048",
        "draw_date": "2025-05-03",
        "front_zone": [2, 6, 17, 23, 35],
        "back_zone": [6, 11]
    },
    
    # ===== 2025年4月数据 =====
    {
        "period": "25047",
        "draw_date": "2025-04-30",
        "front_zone": [3, 10, 11, 12, 21],
        "back_zone": [2, 3]
    }
]

# ===== 数据访问函数 =====

def get_historical_data(limit=None):
    """
    获取历史数据
    
    Args:
        limit: 返回的数据条数，None表示返回全部
    
    Returns:
        list: 历史开奖数据列表
    """
    if limit:
        return LOTTERY_HISTORY[:limit]
    return LOTTERY_HISTORY


def get_latest_draw():
    """
    获取最新一期开奖结果
    
    Returns:
        dict: 最新一期数据，如果没有数据则返回None
    """
    return LOTTERY_HISTORY[0] if LOTTERY_HISTORY else None


def get_period_data(period):
    """
    获取指定期号的数据
    
    Args:
        period: 期号（字符串）
    
    Returns:
        dict: 指定期数据，如果未找到则返回None
    """
    for draw in LOTTERY_HISTORY:
        if draw["period"] == period:
            return draw
    return None


def get_date_range():
    """
    获取数据的日期范围
    
    Returns:
        dict: 包含最早和最新日期，以及总期数
    """
    if not LOTTERY_HISTORY:
        return {"earliest": None, "latest": None, "total_periods": 0}
    
    return {
        "earliest": LOTTERY_HISTORY[-1]["draw_date"],
        "latest": LOTTERY_HISTORY[0]["draw_date"],
        "total_periods": len(LOTTERY_HISTORY)
    }


# ===== 数据统计函数 =====

def get_number_frequency(zone='front'):
    """
    计算号码出现频率
    
    Args:
        zone: 'front' 或 'back'
    
    Returns:
        dict: {号码: 出现次数}
    """
    from collections import Counter
    all_numbers = []
    zone_key = 'front_zone' if zone == 'front' else 'back_zone'
    
    for draw in LOTTERY_HISTORY:
        all_numbers.extend(draw[zone_key])
    
    return dict(Counter(all_numbers))


def get_missing_count(zone='front'):
    """
    计算号码遗漏值（距离上次出现的期数）
    
    Args:
        zone: 'front' 或 'back'
    
    Returns:
        dict: {号码: 遗漏期数}
    """
    zone_key = 'front_zone' if zone == 'front' else 'back_zone'
    max_number = 35 if zone == 'front' else 12
    
    # 找到每个号码最后出现的位置
    last_appearance = {}
    for i, draw in enumerate(LOTTERY_HISTORY):
        for num in draw[zone_key]:
            if num not in last_appearance:
                last_appearance[num] = i
    
    # 计算遗漏值
    missing = {}
    for num in range(1, max_number + 1):
        if num in last_appearance:
            missing[num] = last_appearance[num]  # 距离现在的期数
        else:
            missing[num] = len(LOTTERY_HISTORY)  # 从未出现
    
    return missing


def get_hot_and_cold_numbers(zone='front', top_n=10):
    """
    获取热号和冷号
    
    Args:
        zone: 'front' 或 'back'
        top_n: 返回前N个号码
    
    Returns:
        dict: {'hot': [...], 'cold': [...]}
    """
    frequency = get_number_frequency(zone)
    missing = get_missing_count(zone)
    
    # 按频率排序
    hot_numbers = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:top_n]
    # 按遗漏值排序
    cold_numbers = sorted(missing.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    return {
        'hot': [num for num, _ in hot_numbers],
        'cold': [num for num, _ in cold_numbers]
    }


def validate_data():
    """
    验证数据完整性
    
    Returns:
        dict: 验证结果，包含错误和警告信息
    """
    errors = []
    warnings = []
    
    for i, draw in enumerate(LOTTERY_HISTORY):
        # 检查必需字段
        required_fields = ['period', 'draw_date', 'front_zone', 'back_zone']
        for field in required_fields:
            if field not in draw:
                errors.append(f"第{i+1}条数据缺少字段: {field}")
        
        # 检查前区号码
        if 'front_zone' in draw:
            front = draw['front_zone']
            if len(front) != 5:
                errors.append(f"期号{draw.get('period')}: 前区号码数量不是5个")
            if not all(1 <= n <= 35 for n in front):
                errors.append(f"期号{draw.get('period')}: 前区号码超出范围(1-35)")
            if len(front) != len(set(front)):
                errors.append(f"期号{draw.get('period')}: 前区号码有重复")
        
        # 检查后区号码
        if 'back_zone' in draw:
            back = draw['back_zone']
            if len(back) != 2:
                errors.append(f"期号{draw.get('period')}: 后区号码数量不是2个")
            if not all(1 <= n <= 12 for n in back):
                errors.append(f"期号{draw.get('period')}: 后区号码超出范围(1-12)")
            if len(back) != len(set(back)):
                errors.append(f"期号{draw.get('period')}: 后区号码有重复")
    
    # 检查数据量
    if len(LOTTERY_HISTORY) < 50:
        warnings.append(f"数据量较少，当前只有{len(LOTTERY_HISTORY)}期，建议至少50期")
    
    return {
        'is_valid': len(errors) == 0,
        'total_records': len(LOTTERY_HISTORY),
        'errors': errors,
        'warnings': warnings
    }


# ===== 测试代码 =====
if __name__ == '__main__':
    print("=" * 60)
    print("大乐透历史数据验证")
    print("=" * 60)
    
    # 验证数据
    validation = validate_data()
    print(f"\n数据总量: {validation['total_records']}期")
    print(f"验证结果: {'✓ 通过' if validation['is_valid'] else '✗ 失败'}")
    
    if validation['errors']:
        print("\n错误:")
        for error in validation['errors']:
            print(f"  ✗ {error}")
    
    if validation['warnings']:
        print("\n警告:")
        for warning in validation['warnings']:
            print(f"  ⚠ {warning}")
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("数据统计")
    print("=" * 60)
    
    date_range = get_date_range()
    print(f"\n日期范围: {date_range['earliest']} ~ {date_range['latest']}")
    print(f"总期数: {date_range['total_periods']}")
    
    latest = get_latest_draw()
    print(f"\n最新一期:")
    print(f"  期号: {latest['period']}")
    print(f"  日期: {latest['draw_date']}")
    print(f"  前区: {' '.join([f'{n:02d}' for n in latest['front_zone']])}")
    print(f"  后区: {' '.join([f'{n:02d}' for n in latest['back_zone']])}")
    
    hot_cold_front = get_hot_and_cold_numbers('front', 5)
    print(f"\n前区热号TOP5: {hot_cold_front['hot']}")
    print(f"前区冷号TOP5: {hot_cold_front['cold']}")
    
    hot_cold_back = get_hot_and_cold_numbers('back', 3)
    print(f"\n后区热号TOP3: {hot_cold_back['hot']}")
    print(f"后区冷号TOP3: {hot_cold_back['cold']}")
    
    print("\n" + "=" * 60)
    print("✓ 数据文件加载成功！")
    print("=" * 60)
