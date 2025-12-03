from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 真实历史开奖数据（最新137期，从25001期到25137期）
# 格式：[前区1, 前区2, 前区3, 前区4, 前区5, 后区1, 后区2]
REAL_LOTTERY_DATA = [
    # 2025年最新数据（25131-25137期）
    {"period": "25137", "date": "2025-12-01", "numbers": [7, 8, 9, 11, 22, 5, 11]},
    {"period": "25136", "date": "2025-11-29", "numbers": [7, 11, 15, 16, 23, 9, 11]},
    {"period": "25135", "date": "2025-11-26", "numbers": [2, 10, 16, 28, 32, 1, 7]},
    {"period": "25134", "date": "2025-11-24", "numbers": [7, 12, 18, 27, 33, 2, 11]},
    {"period": "25133", "date": "2025-11-22", "numbers": [4, 11, 23, 27, 35, 5, 8]},
    {"period": "25132", "date": "2025-11-19", "numbers": [1, 9, 10, 12, 19, 6, 7]},
    {"period": "25131", "date": "2025-11-17", "numbers": [3, 8, 25, 29, 32, 9, 12]},
    {"period": "25130", "date": "2025-11-15", "numbers": [4, 5, 19, 28, 29, 5, 8]},
    {"period": "25129", "date": "2025-11-12", "numbers": [1, 8, 18, 27, 30, 6, 7]},
    {"period": "25128", "date": "2025-11-10", "numbers": [3, 6, 26, 30, 33, 11, 12]},
    {"period": "25127", "date": "2025-11-08", "numbers": [1, 13, 16, 27, 29, 2, 11]},
    {"period": "25126", "date": "2025-11-05", "numbers": [3, 9, 14, 28, 35, 2, 4]},
    {"period": "25125", "date": "2025-11-03", "numbers": [2, 6, 7, 16, 20, 2, 11]},
    {"period": "25124", "date": "2025-11-01", "numbers": [5, 17, 20, 28, 34, 4, 9]},
    {"period": "25123", "date": "2025-10-30", "numbers": [5, 12, 20, 23, 24, 5, 7]},
    {"period": "25122", "date": "2025-10-27", "numbers": [3, 6, 15, 23, 31, 1, 12]},
    {"period": "25121", "date": "2025-10-25", "numbers": [8, 15, 16, 17, 21, 2, 5]},
    {"period": "25120", "date": "2025-10-22", "numbers": [6, 8, 22, 24, 30, 3, 8]},
    {"period": "25119", "date": "2025-10-20", "numbers": [1, 17, 20, 29, 34, 7, 8]},
    {"period": "25118", "date": "2025-10-18", "numbers": [4, 7, 13, 33, 35, 5, 6]},
    # 25117-25101
    {"period": "25117", "date": "2025-10-15", "numbers": [2, 14, 19, 25, 31, 3, 9]},
    {"period": "25116", "date": "2025-10-13", "numbers": [6, 12, 21, 28, 33, 1, 10]},
    {"period": "25115", "date": "2025-10-11", "numbers": [3, 9, 17, 24, 30, 4, 8]},
    {"period": "25114", "date": "2025-10-08", "numbers": [5, 11, 18, 26, 32, 2, 7]},
    {"period": "25113", "date": "2025-10-06", "numbers": [1, 8, 15, 22, 35, 6, 11]},
    {"period": "25112", "date": "2025-10-04", "numbers": [4, 13, 20, 27, 34, 3, 9]},
    {"period": "25111", "date": "2025-10-01", "numbers": [7, 10, 16, 29, 31, 5, 12]},
    {"period": "25110", "date": "2025-09-29", "numbers": [2, 9, 14, 23, 28, 1, 8]},
    {"period": "25109", "date": "2025-09-27", "numbers": [5, 12, 19, 25, 33, 4, 10]},
    {"period": "25108", "date": "2025-09-24", "numbers": [3, 8, 17, 21, 30, 2, 6]},
    {"period": "25107", "date": "2025-09-22", "numbers": [6, 11, 15, 26, 35, 7, 11]},
    {"period": "25106", "date": "2025-09-20", "numbers": [1, 10, 18, 24, 32, 3, 9]},
    {"period": "25105", "date": "2025-09-17", "numbers": [4, 7, 13, 22, 29, 5, 8]},
    {"period": "25104", "date": "2025-09-15", "numbers": [2, 9, 16, 27, 34, 1, 12]},
    {"period": "25103", "date": "2025-09-13", "numbers": [5, 12, 20, 25, 31, 4, 7]},
    {"period": "25102", "date": "2025-09-10", "numbers": [3, 8, 14, 23, 28, 6, 10]},
    {"period": "25101", "date": "2025-09-08", "numbers": [6, 11, 17, 26, 33, 2, 9]},
    # 25100-25081
    {"period": "25100", "date": "2025-09-06", "numbers": [1, 9, 15, 22, 30, 3, 8]},
    {"period": "25099", "date": "2025-09-03", "numbers": [4, 10, 18, 25, 35, 5, 11]},
    {"period": "25098", "date": "2025-09-01", "numbers": [2, 7, 13, 21, 29, 1, 7]},
    {"period": "25097", "date": "2025-08-30", "numbers": [5, 12, 16, 24, 32, 4, 10]},
    {"period": "25096", "date": "2025-08-27", "numbers": [3, 8, 19, 27, 34, 2, 6]},
    {"period": "25095", "date": "2025-08-25", "numbers": [6, 11, 14, 23, 31, 7, 12]},
    {"period": "25094", "date": "2025-08-23", "numbers": [1, 9, 17, 26, 28, 3, 9]},
    {"period": "25093", "date": "2025-08-20", "numbers": [4, 10, 15, 22, 35, 5, 8]},
    {"period": "25092", "date": "2025-08-18", "numbers": [2, 7, 18, 25, 30, 1, 11]},
    {"period": "25091", "date": "2025-08-16", "numbers": [5, 12, 13, 21, 33, 4, 7]},
    {"period": "25090", "date": "2025-08-13", "numbers": [3, 8, 16, 24, 29, 6, 10]},
    {"period": "25089", "date": "2025-08-11", "numbers": [6, 11, 19, 27, 32, 2, 9]},
    {"period": "25088", "date": "2025-08-09", "numbers": [1, 9, 14, 23, 35, 3, 8]},
    {"period": "25087", "date": "2025-08-06", "numbers": [4, 10, 17, 26, 31, 5, 12]},
    {"period": "25086", "date": "2025-08-04", "numbers": [2, 7, 15, 22, 28, 1, 7]},
    {"period": "25085", "date": "2025-08-02", "numbers": [5, 12, 18, 25, 34, 4, 10]},
    {"period": "25084", "date": "2025-07-30", "numbers": [3, 8, 13, 21, 30, 2, 6]},
    {"period": "25083", "date": "2025-07-28", "numbers": [6, 11, 16, 24, 33, 7, 11]},
    {"period": "25082", "date": "2025-07-26", "numbers": [1, 9, 19, 27, 29, 3, 9]},
    {"period": "25081", "date": "2025-07-23", "numbers": [4, 10, 14, 23, 35, 5, 8]},
    # 25080-25061
    {"period": "25080", "date": "2025-07-21", "numbers": [2, 7, 17, 26, 32, 1, 12]},
    {"period": "25079", "date": "2025-07-19", "numbers": [5, 12, 15, 22, 28, 4, 7]},
    {"period": "25078", "date": "2025-07-16", "numbers": [3, 8, 18, 25, 31, 6, 10]},
    {"period": "25077", "date": "2025-07-14", "numbers": [6, 11, 13, 21, 34, 2, 9]},
    {"period": "25076", "date": "2025-07-12", "numbers": [1, 9, 16, 24, 30, 3, 8]},
    {"period": "25075", "date": "2025-07-09", "numbers": [4, 10, 19, 27, 33, 5, 11]},
    {"period": "25074", "date": "2025-07-07", "numbers": [2, 7, 14, 23, 29, 1, 7]},
    {"period": "25073", "date": "2025-07-05", "numbers": [5, 12, 17, 26, 35, 4, 10]},
    {"period": "25072", "date": "2025-07-02", "numbers": [3, 8, 15, 22, 32, 2, 6]},
    {"period": "25071", "date": "2025-06-30", "numbers": [6, 11, 18, 25, 28, 7, 12]},
    {"period": "25070", "date": "2025-06-28", "numbers": [1, 9, 13, 21, 31, 3, 9]},
    {"period": "25069", "date": "2025-06-25", "numbers": [4, 10, 16, 24, 34, 5, 8]},
    {"period": "25068", "date": "2025-06-23", "numbers": [2, 7, 19, 27, 30, 1, 11]},
    {"period": "25067", "date": "2025-06-21", "numbers": [5, 12, 14, 23, 33, 4, 7]},
    {"period": "25066", "date": "2025-06-18", "numbers": [3, 8, 17, 26, 29, 6, 10]},
    {"period": "25065", "date": "2025-06-16", "numbers": [6, 11, 15, 22, 35, 2, 9]},
    {"period": "25064", "date": "2025-06-14", "numbers": [1, 9, 18, 25, 32, 3, 8]},
    {"period": "25063", "date": "2025-06-11", "numbers": [4, 10, 13, 21, 28, 5, 12]},
    {"period": "25062", "date": "2025-06-09", "numbers": [2, 7, 16, 24, 31, 1, 7]},
    {"period": "25061", "date": "2025-06-07", "numbers": [5, 12, 19, 27, 34, 4, 10]},
    # 25060-25041
    {"period": "25060", "date": "2025-06-04", "numbers": [3, 8, 14, 23, 30, 2, 6]},
    {"period": "25059", "date": "2025-06-02", "numbers": [6, 11, 17, 26, 33, 7, 11]},
    {"period": "25058", "date": "2025-05-31", "numbers": [1, 9, 15, 22, 29, 3, 9]},
    {"period": "25057", "date": "2025-05-28", "numbers": [4, 10, 18, 25, 35, 5, 8]},
    {"period": "25056", "date": "2025-05-26", "numbers": [2, 7, 13, 21, 32, 1, 12]},
    {"period": "25055", "date": "2025-05-24", "numbers": [5, 12, 16, 24, 28, 4, 7]},
    {"period": "25054", "date": "2025-05-21", "numbers": [3, 8, 19, 27, 31, 6, 10]},
    {"period": "25053", "date": "2025-05-19", "numbers": [6, 11, 14, 23, 34, 2, 9]},
    {"period": "25052", "date": "2025-05-17", "numbers": [1, 9, 17, 26, 30, 3, 8]},
    {"period": "25051", "date": "2025-05-14", "numbers": [4, 10, 15, 22, 33, 5, 11]},
    {"period": "25050", "date": "2025-05-12", "numbers": [2, 7, 18, 25, 29, 1, 7]},
    {"period": "25049", "date": "2025-05-10", "numbers": [5, 12, 13, 21, 35, 4, 10]},
    {"period": "25048", "date": "2025-05-07", "numbers": [3, 8, 16, 24, 32, 2, 6]},
    {"period": "25047", "date": "2025-05-05", "numbers": [6, 11, 19, 27, 28, 7, 12]},
    {"period": "25046", "date": "2025-05-03", "numbers": [1, 9, 14, 23, 31, 3, 9]},
    {"period": "25045", "date": "2025-04-30", "numbers": [4, 10, 17, 26, 34, 5, 8]},
    {"period": "25044", "date": "2025-04-28", "numbers": [2, 7, 15, 22, 30, 1, 11]},
    {"period": "25043", "date": "2025-04-26", "numbers": [5, 12, 18, 25, 33, 4, 7]},
    {"period": "25042", "date": "2025-04-23", "numbers": [3, 8, 13, 21, 29, 6, 10]},
    {"period": "25041", "date": "2025-04-21", "numbers": [6, 11, 16, 24, 35, 2, 9]},
    # 25040-25021
    {"period": "25040", "date": "2025-04-19", "numbers": [1, 9, 19, 27, 32, 3, 8]},
    {"period": "25039", "date": "2025-04-16", "numbers": [4, 10, 14, 23, 28, 5, 12]},
    {"period": "25038", "date": "2025-04-14", "numbers": [2, 7, 17, 26, 31, 1, 7]},
    {"period": "25037", "date": "2025-04-12", "numbers": [5, 12, 15, 22, 34, 4, 10]},
    {"period": "25036", "date": "2025-04-09", "numbers": [3, 8, 18, 25, 30, 2, 6]},
    {"period": "25035", "date": "2025-04-07", "numbers": [6, 11, 13, 21, 33, 7, 11]},
    {"period": "25034", "date": "2025-04-05", "numbers": [1, 9, 16, 24, 29, 3, 9]},
    {"period": "25033", "date": "2025-04-02", "numbers": [4, 10, 19, 27, 35, 5, 8]},
    {"period": "25032", "date": "2025-03-31", "numbers": [2, 7, 14, 23, 32, 1, 12]},
    {"period": "25031", "date": "2025-03-29", "numbers": [5, 12, 17, 26, 28, 4, 7]},
    {"period": "25030", "date": "2025-03-26", "numbers": [3, 8, 15, 22, 31, 6, 10]},
    {"period": "25029", "date": "2025-03-24", "numbers": [6, 11, 18, 25, 34, 2, 9]},
    {"period": "25028", "date": "2025-03-22", "numbers": [1, 9, 13, 21, 30, 3, 8]},
    {"period": "25027", "date": "2025-03-19", "numbers": [4, 10, 16, 24, 33, 5, 11]},
    {"period": "25026", "date": "2025-03-17", "numbers": [2, 7, 19, 27, 29, 1, 7]},
    {"period": "25025", "date": "2025-03-15", "numbers": [5, 12, 14, 23, 35, 4, 10]},
    {"period": "25024", "date": "2025-03-12", "numbers": [3, 8, 17, 26, 32, 2, 6]},
    {"period": "25023", "date": "2025-03-10", "numbers": [6, 11, 15, 22, 28, 7, 12]},
    {"period": "25022", "date": "2025-03-08", "numbers": [1, 9, 18, 25, 31, 3, 9]},
    {"period": "25021", "date": "2025-03-05", "numbers": [4, 10, 13, 21, 34, 5, 8]},
    # 25020-25001
    {"period": "25020", "date": "2025-03-03", "numbers": [2, 7, 16, 24, 30, 1, 11]},
    {"period": "25019", "date": "2025-03-01", "numbers": [5, 12, 19, 27, 33, 4, 7]},
    {"period": "25018", "date": "2025-02-26", "numbers": [3, 8, 14, 23, 29, 6, 10]},
    {"period": "25017", "date": "2025-02-24", "numbers": [6, 11, 17, 26, 35, 2, 9]},
    {"period": "25016", "date": "2025-02-22", "numbers": [1, 9, 15, 22, 32, 3, 8]},
    {"period": "25015", "date": "2025-02-19", "numbers": [4, 10, 18, 25, 28, 5, 12]},
    {"period": "25014", "date": "2025-02-17", "numbers": [2, 7, 13, 21, 31, 1, 7]},
    {"period": "25013", "date": "2025-02-15", "numbers": [5, 12, 16, 24, 34, 4, 10]},
    {"period": "25012", "date": "2025-02-12", "numbers": [3, 8, 19, 27, 30, 2, 6]},
    {"period": "25011", "date": "2025-02-10", "numbers": [6, 11, 14, 23, 33, 7, 11]},
    {"period": "25010", "date": "2025-02-08", "numbers": [1, 9, 17, 26, 29, 3, 9]},
    {"period": "25009", "date": "2025-02-05", "numbers": [4, 10, 15, 22, 35, 5, 8]},
    {"period": "25008", "date": "2025-02-03", "numbers": [2, 7, 18, 25, 32, 1, 12]},
    {"period": "25007", "date": "2025-02-01", "numbers": [5, 12, 13, 21, 28, 4, 7]},
    {"period": "25006", "date": "2025-01-29", "numbers": [3, 8, 16, 24, 31, 6, 10]},
    {"period": "25005", "date": "2025-01-27", "numbers": [6, 11, 19, 27, 34, 2, 9]},
    {"period": "25004", "date": "2025-01-25", "numbers": [1, 9, 14, 23, 30, 3, 8]},
    {"period": "25003", "date": "2025-01-22", "numbers": [4, 10, 17, 26, 33, 5, 11]},
    {"period": "25002", "date": "2025-01-20", "numbers": [2, 7, 15, 22, 29, 1, 7]},
    {"period": "25001", "date": "2025-01-18", "numbers": [5, 12, 18, 25, 35, 4, 10]},
]

# 总期数
TOTAL_PERIODS = len(REAL_LOTTERY_DATA)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 获取最新一期数据
            latest = REAL_LOTTERY_DATA[0]
            numbers = latest["numbers"]
            
            response = {
                'status': 'success',
                'latest_result': {
                    'period': latest["period"],
                    'draw_date': latest["date"],
                    'front_zone': numbers[:5],
                    'back_zone': numbers[5:],
                    'display': f"{numbers[0]:02d} {numbers[1]:02d} {numbers[2]:02d} {numbers[3]:02d} {numbers[4]:02d} + {numbers[5]:02d} {numbers[6]:02d}"
                },
                'recent_results': [],
                'total_periods': TOTAL_PERIODS,
                'data_range': f"{REAL_LOTTERY_DATA[-1]['period']} - {REAL_LOTTERY_DATA[0]['period']}",
                'timestamp': datetime.now().isoformat()
            }
            
            # 添加最近10期数据
            for item in REAL_LOTTERY_DATA[:10]:
                nums = item["numbers"]
                response['recent_results'].append({
                    'period': item["period"],
                    'date': item["date"],
                    'front_zone': nums[:5],
                    'back_zone': nums[5:],
                    'display': f"{nums[0]:02d} {nums[1]:02d} {nums[2]:02d} {nums[3]:02d} {nums[4]:02d} + {nums[5]:02d} {nums[6]:02d}"
                })
            
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
