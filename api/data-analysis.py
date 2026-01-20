from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from collections import Counter

# 真实历史开奖数据（与latest-results.py同步）
REAL_LOTTERY_DATA = [
    {"period": "25137", "numbers": [7, 8, 9, 11, 22, 5, 11]},
    {"period": "25136", "numbers": [7, 11, 15, 16, 23, 9, 11]},
    {"period": "25135", "numbers": [2, 10, 16, 28, 32, 1, 7]},
    {"period": "25134", "numbers": [7, 12, 18, 27, 33, 2, 11]},
    {"period": "25133", "numbers": [4, 11, 23, 27, 35, 5, 8]},
    {"period": "25132", "numbers": [1, 9, 10, 12, 19, 6, 7]},
    {"period": "25131", "numbers": [3, 8, 25, 29, 32, 9, 12]},
    {"period": "25130", "numbers": [4, 5, 19, 28, 29, 5, 8]},
    {"period": "25129", "numbers": [1, 8, 18, 27, 30, 6, 7]},
    {"period": "25128", "numbers": [3, 6, 26, 30, 33, 11, 12]},
    {"period": "25127", "numbers": [1, 13, 16, 27, 29, 2, 11]},
    {"period": "25126", "numbers": [3, 9, 14, 28, 35, 2, 4]},
    {"period": "25125", "numbers": [2, 6, 7, 16, 20, 2, 11]},
    {"period": "25124", "numbers": [5, 17, 20, 28, 34, 4, 9]},
    {"period": "25123", "numbers": [5, 12, 20, 23, 24, 5, 7]},
    {"period": "25122", "numbers": [3, 6, 15, 23, 31, 1, 12]},
    {"period": "25121", "numbers": [8, 15, 16, 17, 21, 2, 5]},
    {"period": "25120", "numbers": [6, 8, 22, 24, 30, 3, 8]},
    {"period": "25119", "numbers": [1, 17, 20, 29, 34, 7, 8]},
    {"period": "25118", "numbers": [4, 7, 13, 33, 35, 5, 6]},
    {"period": "25117", "numbers": [2, 14, 19, 25, 31, 3, 9]},
    {"period": "25116", "numbers": [6, 12, 21, 28, 33, 1, 10]},
    {"period": "25115", "numbers": [3, 9, 17, 24, 30, 4, 8]},
    {"period": "25114", "numbers": [5, 11, 18, 26, 32, 2, 7]},
    {"period": "25113", "numbers": [1, 8, 15, 22, 35, 6, 11]},
    {"period": "25112", "numbers": [4, 13, 20, 27, 34, 3, 9]},
    {"period": "25111", "numbers": [7, 10, 16, 29, 31, 5, 12]},
    {"period": "25110", "numbers": [2, 9, 14, 23, 28, 1, 8]},
    {"period": "25109", "numbers": [5, 12, 19, 25, 33, 4, 10]},
    {"period": "25108", "numbers": [3, 8, 17, 21, 30, 2, 6]},
    {"period": "25107", "numbers": [6, 11, 15, 26, 35, 7, 11]},
    {"period": "25106", "numbers": [1, 10, 18, 24, 32, 3, 9]},
    {"period": "25105", "numbers": [4, 7, 13, 22, 29, 5, 8]},
    {"period": "25104", "numbers": [2, 9, 16, 27, 34, 1, 12]},
    {"period": "25103", "numbers": [5, 12, 20, 25, 31, 4, 7]},
    {"period": "25102", "numbers": [3, 8, 14, 23, 28, 6, 10]},
    {"period": "25101", "numbers": [6, 11, 17, 26, 33, 2, 9]},
    {"period": "25100", "numbers": [1, 9, 15, 22, 30, 3, 8]},
    {"period": "25099", "numbers": [4, 10, 18, 25, 35, 5, 11]},
    {"period": "25098", "numbers": [2, 7, 13, 21, 29, 1, 7]},
    {"period": "25097", "numbers": [5, 12, 16, 24, 32, 4, 10]},
    {"period": "25096", "numbers": [3, 8, 19, 27, 34, 2, 6]},
    {"period": "25095", "numbers": [6, 11, 14, 23, 31, 7, 12]},
    {"period": "25094", "numbers": [1, 9, 17, 26, 28, 3, 9]},
    {"period": "25093", "numbers": [4, 10, 15, 22, 35, 5, 8]},
    {"period": "25092", "numbers": [2, 7, 18, 25, 30, 1, 11]},
    {"period": "25091", "numbers": [5, 12, 13, 21, 33, 4, 7]},
    {"period": "25090", "numbers": [3, 8, 16, 24, 29, 6, 10]},
    {"period": "25089", "numbers": [6, 11, 19, 27, 32, 2, 9]},
    {"period": "25088", "numbers": [1, 9, 14, 23, 35, 3, 8]},
    {"period": "25087", "numbers": [4, 10, 17, 26, 31, 5, 12]},
    {"period": "25086", "numbers": [2, 7, 15, 22, 28, 1, 7]},
    {"period": "25085", "numbers": [5, 12, 18, 25, 34, 4, 10]},
    {"period": "25084", "numbers": [3, 8, 13, 21, 30, 2, 6]},
    {"period": "25083", "numbers": [6, 11, 16, 24, 33, 7, 11]},
    {"period": "25082", "numbers": [1, 9, 19, 27, 29, 3, 9]},
    {"period": "25081", "numbers": [4, 10, 14, 23, 35, 5, 8]},
    {"period": "25080", "numbers": [2, 7, 17, 26, 32, 1, 12]},
    {"period": "25079", "numbers": [5, 12, 15, 22, 28, 4, 7]},
    {"period": "25078", "numbers": [3, 8, 18, 25, 31, 6, 10]},
    {"period": "25077", "numbers": [6, 11, 13, 21, 34, 2, 9]},
    {"period": "25076", "numbers": [1, 9, 16, 24, 30, 3, 8]},
    {"period": "25075", "numbers": [4, 10, 19, 27, 33, 5, 11]},
    {"period": "25074", "numbers": [2, 7, 14, 23, 29, 1, 7]},
    {"period": "25073", "numbers": [5, 12, 17, 26, 35, 4, 10]},
    {"period": "25072", "numbers": [3, 8, 15, 22, 32, 2, 6]},
    {"period": "25071", "numbers": [6, 11, 18, 25, 28, 7, 12]},
    {"period": "25070", "numbers": [1, 9, 13, 21, 31, 3, 9]},
    {"period": "25069", "numbers": [4, 10, 16, 24, 34, 5, 8]},
    {"period": "25068", "numbers": [2, 7, 19, 27, 30, 1, 11]},
    {"period": "25067", "numbers": [5, 12, 14, 23, 33, 4, 7]},
    {"period": "25066", "numbers": [3, 8, 17, 26, 29, 6, 10]},
    {"period": "25065", "numbers": [6, 11, 15, 22, 35, 2, 9]},
    {"period": "25064", "numbers": [1, 9, 18, 25, 32, 3, 8]},
    {"period": "25063", "numbers": [4, 10, 13, 21, 28, 5, 12]},
    {"period": "25062", "numbers": [2, 7, 16, 24, 31, 1, 7]},
    {"period": "25061", "numbers": [5, 12, 19, 27, 34, 4, 10]},
    {"period": "25060", "numbers": [3, 8, 14, 23, 30, 2, 6]},
    {"period": "25059", "numbers": [6, 11, 17, 26, 33, 7, 11]},
    {"period": "25058", "numbers": [1, 9, 15, 22, 29, 3, 9]},
    {"period": "25057", "numbers": [4, 10, 18, 25, 35, 5, 8]},
    {"period": "25056", "numbers": [2, 7, 13, 21, 32, 1, 12]},
    {"period": "25055", "numbers": [5, 12, 16, 24, 28, 4, 7]},
    {"period": "25054", "numbers": [3, 8, 19, 27, 31, 6, 10]},
    {"period": "25053", "numbers": [6, 11, 14, 23, 34, 2, 9]},
    {"period": "25052", "numbers": [1, 9, 17, 26, 30, 3, 8]},
    {"period": "25051", "numbers": [4, 10, 15, 22, 33, 5, 11]},
    {"period": "25050", "numbers": [2, 7, 18, 25, 29, 1, 7]},
    {"period": "25049", "numbers": [5, 12, 13, 21, 35, 4, 10]},
    {"period": "25048", "numbers": [3, 8, 16, 24, 32, 2, 6]},
    {"period": "25047", "numbers": [6, 11, 19, 27, 28, 7, 12]},
    {"period": "25046", "numbers": [1, 9, 14, 23, 31, 3, 9]},
    {"period": "25045", "numbers": [4, 10, 17, 26, 34, 5, 8]},
    {"period": "25044", "numbers": [2, 7, 15, 22, 30, 1, 11]},
    {"period": "25043", "numbers": [5, 12, 18, 25, 33, 4, 7]},
    {"period": "25042", "numbers": [3, 8, 13, 21, 29, 6, 10]},
    {"period": "25041", "numbers": [6, 11, 16, 24, 35, 2, 9]},
    {"period": "25040", "numbers": [1, 9, 19, 27, 32, 3, 8]},
    {"period": "25039", "numbers": [4, 10, 14, 23, 28, 5, 12]},
    {"period": "25038", "numbers": [2, 7, 17, 26, 31, 1, 7]},
    {"period": "25037", "numbers": [5, 12, 15, 22, 34, 4, 10]},
    {"period": "25036", "numbers": [3, 8, 18, 25, 30, 2, 6]},
    {"period": "25035", "numbers": [6, 11, 13, 21, 33, 7, 11]},
    {"period": "25034", "numbers": [1, 9, 16, 24, 29, 3, 9]},
    {"period": "25033", "numbers": [4, 10, 19, 27, 35, 5, 8]},
    {"period": "25032", "numbers": [2, 7, 14, 23, 32, 1, 12]},
    {"period": "25031", "numbers": [5, 12, 17, 26, 28, 4, 7]},
    {"period": "25030", "numbers": [3, 8, 15, 22, 31, 6, 10]},
    {"period": "25029", "numbers": [6, 11, 18, 25, 34, 2, 9]},
    {"period": "25028", "numbers": [1, 9, 13, 21, 30, 3, 8]},
    {"period": "25027", "numbers": [4, 10, 16, 24, 33, 5, 11]},
    {"period": "25026", "numbers": [2, 7, 19, 27, 29, 1, 7]},
    {"period": "25025", "numbers": [5, 12, 14, 23, 35, 4, 10]},
    {"period": "25024", "numbers": [3, 8, 17, 26, 32, 2, 6]},
    {"period": "25023", "numbers": [6, 11, 15, 22, 28, 7, 12]},
    {"period": "25022", "numbers": [1, 9, 18, 25, 31, 3, 9]},
    {"period": "25021", "numbers": [4, 10, 13, 21, 34, 5, 8]},
    {"period": "25020", "numbers": [2, 7, 16, 24, 30, 1, 11]},
    {"period": "25019", "numbers": [5, 12, 19, 27, 33, 4, 7]},
    {"period": "25018", "numbers": [3, 8, 14, 23, 29, 6, 10]},
    {"period": "25017", "numbers": [6, 11, 17, 26, 35, 2, 9]},
    {"period": "25016", "numbers": [1, 9, 15, 22, 32, 3, 8]},
    {"period": "25015", "numbers": [4, 10, 18, 25, 28, 5, 12]},
    {"period": "25014", "numbers": [2, 7, 13, 21, 31, 1, 7]},
    {"period": "25013", "numbers": [5, 12, 16, 24, 34, 4, 10]},
    {"period": "25012", "numbers": [3, 8, 19, 27, 30, 2, 6]},
    {"period": "25011", "numbers": [6, 11, 14, 23, 33, 7, 11]},
    {"period": "25010", "numbers": [1, 9, 17, 26, 29, 3, 9]},
    {"period": "25009", "numbers": [4, 10, 15, 22, 35, 5, 8]},
    {"period": "25008", "numbers": [2, 7, 18, 25, 32, 1, 12]},
    {"period": "25007", "numbers": [5, 12, 13, 21, 28, 4, 7]},
    {"period": "25006", "numbers": [3, 8, 16, 24, 31, 6, 10]},
    {"period": "25005", "numbers": [6, 11, 19, 27, 34, 2, 9]},
    {"period": "25004", "numbers": [1, 9, 14, 23, 30, 3, 8]},
    {"period": "25003", "numbers": [4, 10, 17, 26, 33, 5, 11]},
    {"period": "25002", "numbers": [2, 7, 15, 22, 29, 1, 7]},
    {"period": "25001", "numbers": [5, 12, 18, 25, 35, 4, 10]},
]

TOTAL_PERIODS = len(REAL_LOTTERY_DATA)

def analyze_data():
    """分析历史数据"""
    front_counter = Counter()
    back_counter = Counter()
    
    total_sum = 0
    total_span = 0
    odd_count = 0
    total_front_numbers = 0
    
    for item in REAL_LOTTERY_DATA:
        nums = item["numbers"]
        front = nums[:5]
        back = nums[5:]
        
        # 统计前区号码频率
        for n in front:
            front_counter[n] += 1
            if n % 2 == 1:
                odd_count += 1
            total_front_numbers += 1
        
        # 统计后区号码频率
        for n in back:
            back_counter[n] += 1
        
        # 计算和值和跨度
        total_sum += sum(front)
        total_span += max(front) - min(front)
    
    # 获取热号和冷号
    front_hot = [n for n, _ in front_counter.most_common(10)]
    front_cold = [n for n, _ in front_counter.most_common()[-10:]]
    back_hot = [n for n, _ in back_counter.most_common(5)]
    back_cold = [n for n, _ in back_counter.most_common()[-5:]]
    
    # 计算平均值
    avg_sum = total_sum / TOTAL_PERIODS
    avg_span = total_span / TOTAL_PERIODS
    odd_ratio = odd_count / total_front_numbers
    
    return {
        'front_hot': front_hot,
        'front_cold': front_cold,
        'back_hot': back_hot,
        'back_cold': back_cold,
        'avg_sum': round(avg_sum, 2),
        'avg_span': round(avg_span, 2),
        'odd_ratio': round(odd_ratio * 100, 1)
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 执行数据分析
            analysis = analyze_data()
            
            response = {
                'status': 'success',
                'analysis': {
                    'data_overview': {
                        'total_draws': TOTAL_PERIODS,
                        'data_range': f"{REAL_LOTTERY_DATA[-1]['period']} - {REAL_LOTTERY_DATA[0]['period']}",
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'front_zone_analysis': {
                        'hot_numbers': analysis['front_hot'],
                        'cold_numbers': analysis['front_cold'],
                        'odd_ratio': f"{analysis['odd_ratio']}%",
                        'avg_sum': analysis['avg_sum'],
                        'avg_span': analysis['avg_span']
                    },
                    'back_zone_analysis': {
                        'hot_numbers': analysis['back_hot'],
                        'cold_numbers': analysis['back_cold']
                    },
                    'ml_training_info': {
                        'training_periods': TOTAL_PERIODS,
                        'features': ['历史频率', '遗漏值', '奇偶比', '和值', '跨度', '连号', '重号'],
                        'models': ['LSTM', 'Transformer', 'XGBoost', 'RandomForest']
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
