"""
大乐透历史开奖数据
数据来源: 中国福利彩票官网（通过截图识别采集）
数据范围: 25047期 - 25131期（共85期）
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
    {"period": "25131", "draw_date": "2025-11-17", "front_zone": [3, 8, 25, 29, 32], "back_zone": [9, 12]},
    {"period": "25130", "draw_date": "2025-11-15", "front_zone": [1, 13, 16, 27, 29], "back_zone": [2, 11]},
    {"period": "25129", "draw_date": "2025-11-12", "front_zone": [3, 9, 14, 28, 35], "back_zone": [2, 4]},
    {"period": "25128", "draw_date": "2025-11-10", "front_zone": [3, 6, 26, 30, 33], "back_zone": [11, 12]},
    {"period": "25127", "draw_date": "2025-11-08", "front_zone": [4, 5, 19, 28, 29], "back_zone": [5, 8]},
    {"period": "25126", "draw_date": "2025-11-05", "front_zone": [1, 8, 18, 27, 30], "back_zone": [6, 7]},
    {"period": "25125", "draw_date": "2025-11-03", "front_zone": [10, 11, 13, 19, 35], "back_zone": [4, 11]},
    {"period": "25124", "draw_date": "2025-11-01", "front_zone": [6, 9, 14, 26, 27], "back_zone": [8, 9]},
    
    # ===== 2025年10月数据 =====
    {"period": "25123", "draw_date": "2025-10-29", "front_zone": [8, 13, 24, 25, 31], "back_zone": [4, 10]},
    {"period": "25122", "draw_date": "2025-10-27", "front_zone": [2, 3, 6, 16, 17], "back_zone": [4, 5]},
    {"period": "25121", "draw_date": "2025-10-25", "front_zone": [2, 3, 8, 13, 21], "back_zone": [7, 12]},
    {"period": "25120", "draw_date": "2025-10-22", "front_zone": [11, 13, 22, 26, 35], "back_zone": [2, 8]},
    {"period": "25119", "draw_date": "2025-10-20", "front_zone": [8, 15, 27, 29, 31], "back_zone": [1, 7]},
    {"period": "25118", "draw_date": "2025-10-18", "front_zone": [2, 8, 9, 12, 21], "back_zone": [4, 5]},
    {"period": "25117", "draw_date": "2025-10-15", "front_zone": [5, 10, 18, 21, 29], "back_zone": [5, 7]},
    {"period": "25116", "draw_date": "2025-10-13", "front_zone": [2, 6, 16, 22, 29], "back_zone": [8, 12]},
    {"period": "25115", "draw_date": "2025-10-11", "front_zone": [3, 12, 14, 21, 35], "back_zone": [1, 5]},
    {"period": "25114", "draw_date": "2025-10-08", "front_zone": [3, 8, 9, 12, 16], "back_zone": [1, 5]},
    {"period": "25113", "draw_date": "2025-10-06", "front_zone": [1, 14, 18, 28, 35], "back_zone": [2, 3]},
    
    # ===== 2025年9月数据 =====
    {"period": "25112", "draw_date": "2025-09-29", "front_zone": [3, 4, 21, 23, 24], "back_zone": [9, 12]},
    {"period": "25111", "draw_date": "2025-09-27", "front_zone": [2, 9, 14, 21, 26], "back_zone": [2, 12]},
    {"period": "25110", "draw_date": "2025-09-24", "front_zone": [1, 15, 22, 30, 31], "back_zone": [2, 8]},
    {"period": "25109", "draw_date": "2025-09-22", "front_zone": [4, 8, 10, 13, 26], "back_zone": [9, 10]},
    {"period": "25108", "draw_date": "2025-09-20", "front_zone": [14, 18, 21, 24, 29], "back_zone": [3, 6]},
    {"period": "25107", "draw_date": "2025-09-17", "front_zone": [5, 7, 8, 15, 33], "back_zone": [6, 10]},
    {"period": "25106", "draw_date": "2025-09-15", "front_zone": [5, 6, 11, 26, 29], "back_zone": [5, 10]},
    {"period": "25105", "draw_date": "2025-09-13", "front_zone": [15, 16, 25, 28, 34], "back_zone": [10, 12]},
    {"period": "25104", "draw_date": "2025-09-10", "front_zone": [2, 6, 9, 22, 34], "back_zone": [2, 8]},
    {"period": "25103", "draw_date": "2025-09-08", "front_zone": [5, 8, 19, 32, 34], "back_zone": [4, 5]},
    {"period": "25102", "draw_date": "2025-09-06", "front_zone": [9, 10, 13, 26, 28], "back_zone": [2, 4]},
    {"period": "25101", "draw_date": "2025-09-03", "front_zone": [5, 7, 19, 26, 32], "back_zone": [8, 9]},
    {"period": "25100", "draw_date": "2025-09-01", "front_zone": [26, 28, 32, 34, 35], "back_zone": [2, 7]},
    
    # ===== 2025年8月数据 =====
    {"period": "25099", "draw_date": "2025-08-30", "front_zone": [6, 12, 20, 26, 31], "back_zone": [2, 4]},
    {"period": "25098", "draw_date": "2025-08-27", "front_zone": [1, 7, 9, 10, 23], "back_zone": [10, 12]},
    {"period": "25097", "draw_date": "2025-08-25", "front_zone": [5, 24, 25, 32, 34], "back_zone": [1, 9]},
    {"period": "25096", "draw_date": "2025-08-23", "front_zone": [2, 11, 17, 22, 24], "back_zone": [7, 9]},
    {"period": "25095", "draw_date": "2025-08-20", "front_zone": [7, 13, 14, 19, 27], "back_zone": [6, 10]},
    {"period": "25094", "draw_date": "2025-08-18", "front_zone": [4, 9, 17, 30, 33], "back_zone": [5, 9]},
    {"period": "25093", "draw_date": "2025-08-16", "front_zone": [1, 7, 9, 16, 30], "back_zone": [2, 5]},
    {"period": "25092", "draw_date": "2025-08-13", "front_zone": [4, 10, 17, 25, 32], "back_zone": [5, 7]},
    {"period": "25091", "draw_date": "2025-08-11", "front_zone": [1, 19, 22, 25, 27], "back_zone": [3, 10]},
    {"period": "25090", "draw_date": "2025-08-09", "front_zone": [6, 14, 19, 22, 27], "back_zone": [1, 4]},
    {"period": "25089", "draw_date": "2025-08-06", "front_zone": [2, 11, 12, 32, 34], "back_zone": [3, 10]},
    {"period": "25088", "draw_date": "2025-08-04", "front_zone": [8, 9, 10, 11, 35], "back_zone": [5, 11]},
    {"period": "25087", "draw_date": "2025-08-02", "front_zone": [5, 13, 14, 16, 20], "back_zone": [3, 8]},
    
    # ===== 2025年7月数据 =====
    {"period": "25086", "draw_date": "2025-07-30", "front_zone": [2, 6, 23, 24, 33], "back_zone": [1, 10]},
    {"period": "25085", "draw_date": "2025-07-28", "front_zone": [2, 5, 9, 14, 33], "back_zone": [4, 9]},
    {"period": "25084", "draw_date": "2025-07-26", "front_zone": [9, 11, 13, 18, 29], "back_zone": [4, 11]},
    {"period": "25083", "draw_date": "2025-07-23", "front_zone": [12, 17, 18, 20, 34], "back_zone": [2, 5]},
    {"period": "25082", "draw_date": "2025-07-21", "front_zone": [2, 3, 4, 12, 26], "back_zone": [1, 8]},
    {"period": "25081", "draw_date": "2025-07-19", "front_zone": [1, 4, 6, 15, 18], "back_zone": [2, 3]},
    {"period": "25080", "draw_date": "2025-07-16", "front_zone": [9, 10, 18, 22, 24], "back_zone": [3, 12]},
    {"period": "25079", "draw_date": "2025-07-14", "front_zone": [2, 14, 32, 34, 35], "back_zone": [5, 11]},
    {"period": "25078", "draw_date": "2025-07-12", "front_zone": [7, 10, 15, 21, 24], "back_zone": [5, 6]},
    {"period": "25077", "draw_date": "2025-07-09", "front_zone": [12, 14, 16, 19, 28], "back_zone": [1, 4]},
    {"period": "25076", "draw_date": "2025-07-07", "front_zone": [11, 18, 22, 25, 29], "back_zone": [4, 12]},
    {"period": "25075", "draw_date": "2025-07-05", "front_zone": [8, 12, 16, 19, 35], "back_zone": [6, 9]},
    {"period": "25074", "draw_date": "2025-07-02", "front_zone": [2, 11, 15, 18, 21], "back_zone": [5, 10]},
    
    # ===== 2025年6月数据 =====
    {"period": "25073", "draw_date": "2025-06-30", "front_zone": [1, 4, 17, 33, 34], "back_zone": [3, 9]},
    {"period": "25072", "draw_date": "2025-06-28", "front_zone": [4, 7, 15, 24, 29], "back_zone": [1, 4]},
    {"period": "25071", "draw_date": "2025-06-25", "front_zone": [1, 8, 25, 31, 33], "back_zone": [5, 11]},
    {"period": "25070", "draw_date": "2025-06-23", "front_zone": [8, 9, 15, 20, 22], "back_zone": [4, 12]},
    {"period": "25069", "draw_date": "2025-06-21", "front_zone": [4, 6, 7, 33, 34], "back_zone": [9, 10]},
    {"period": "25068", "draw_date": "2025-06-18", "front_zone": [1, 4, 17, 20, 22], "back_zone": [4, 10]},
    {"period": "25067", "draw_date": "2025-06-16", "front_zone": [6, 10, 12, 21, 22], "back_zone": [1, 6]},
    {"period": "25066", "draw_date": "2025-06-14", "front_zone": [15, 18, 27, 28, 34], "back_zone": [3, 6]},
    {"period": "25065", "draw_date": "2025-06-11", "front_zone": [7, 25, 32, 33, 35], "back_zone": [4, 9]},
    {"period": "25064", "draw_date": "2025-06-09", "front_zone": [5, 10, 18, 20, 34], "back_zone": [1, 8]},
    {"period": "25063", "draw_date": "2025-06-07", "front_zone": [5, 18, 26, 29, 32], "back_zone": [7, 10]},
    {"period": "25062", "draw_date": "2025-06-04", "front_zone": [14, 20, 27, 28, 29], "back_zone": [6, 10]},
    {"period": "25061", "draw_date": "2025-06-02", "front_zone": [2, 11, 16, 23, 28], "back_zone": [5, 10]},
    
    # ===== 2025年5月数据 =====
    {"period": "25060", "draw_date": "2025-05-31", "front_zone": [12, 14, 19, 33, 34], "back_zone": [1, 7]},
    {"period": "25059", "draw_date": "2025-05-28", "front_zone": [3, 9, 10, 11, 26], "back_zone": [1, 2]},
    {"period": "25058", "draw_date": "2025-05-26", "front_zone": [6, 11, 15, 21, 23], "back_zone": [1, 7]},
    {"period": "25057", "draw_date": "2025-05-24", "front_zone": [9, 10, 11, 12, 29], "back_zone": [1, 10]},
    {"period": "25056", "draw_date": "2025-05-21", "front_zone": [12, 15, 28, 29, 32], "back_zone": [8, 11]},
    {"period": "25055", "draw_date": "2025-05-19", "front_zone": [8, 10, 25, 29, 30], "back_zone": [1, 2]},
    {"period": "25054", "draw_date": "2025-05-17", "front_zone": [3, 12, 16, 21, 29], "back_zone": [1, 2]},
    {"period": "25053", "draw_date": "2025-05-14", "front_zone": [14, 23, 29, 30, 33], "back_zone": [6, 12]},
    {"period": "25052", "draw_date": "2025-05-12", "front_zone": [2, 4, 11, 29, 30], "back_zone": [2, 8]},
    {"period": "25051", "draw_date": "2025-05-10", "front_zone": [2, 4, 13, 29, 31], "back_zone": [5, 12]},
    {"period": "25050", "draw_date": "2025-05-07", "front_zone": [15, 18, 20, 21, 34], "back_zone": [4, 10]},
    {"period": "25049", "draw_date": "2025-05-05", "front_zone": [9, 20, 22, 29, 34], "back_zone": [3, 8]},
    {"period": "25048", "draw_date": "2025-05-03", "front_zone": [2, 6, 17, 23, 35], "back_zone": [6, 11]},
    
    # ===== 2025年4月数据 =====
    {"period": "25047", "draw_date": "2025-04-30", "front_zone": [3, 10, 11, 12, 21], "back_zone": [2, 3]}
]

# ===== 数据访问函数 =====

def get_historical_data(limit=None):
    """获取历史数据"""
    if limit:
        return LOTTERY_HISTORY[:limit]
    return LOTTERY_HISTORY

def get_latest_draw():
    """获取最新一期开奖结果"""
    return LOTTERY_HISTORY[0] if LOTTERY_HISTORY else None

def get_period_data(period):
    """获取指定期号的数据"""
    for draw in LOTTERY_HISTORY:
        if draw["period"] == period:
            return draw
    return None

def get_number_frequency(zone='front'):
    """计算号码出现频率"""
    from collections import Counter
    all_numbers = []
    zone_key = 'front_zone' if zone == 'front' else 'back_zone'
    for draw in LOTTERY_HISTORY:
        all_numbers.extend(draw[zone_key])
    return dict(Counter(all_numbers))

def get_hot_and_cold_numbers(zone='front', top_n=10):
    """获取热号和冷号"""
    frequency = get_number_frequency(zone)
    sorted_numbers = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    hot = [num for num, _ in sorted_numbers[:top_n]]
    cold = [num for num, _ in sorted_numbers[-top_n:]]
    return {'hot': hot, 'cold': cold}
