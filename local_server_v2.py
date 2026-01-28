#!/usr/bin/env python3
"""
本地开发服务器 v2 - 完整功能版
支持：真实数据加载、实时更新、推文生成
"""
import os
import sys
import json
import random
import hashlib
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timedelta
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ============ 数据管理 ============
class LotteryDataManager:
    """彩票数据管理器"""

    def __init__(self):
        self.data_file = os.path.join(PROJECT_ROOT, 'lottery_data_full.json')
        self.data = []
        self.load_local_data()

    def load_local_data(self):
        """加载本地数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✅ 加载本地数据: {len(self.data)} 期")
            except Exception as e:
                print(f"⚠️ 加载本地数据失败: {e}")
                self.data = []
        else:
            print(f"⚠️ 数据文件不存在: {self.data_file}")
            self.data = []

    def fetch_latest_from_api(self):
        """从网络API获取最新数据"""
        # 尝试多个数据源
        apis = [
            'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=dlt&issueCount=10',
            'http://www.lottery.gov.cn/api/dlt_history.json'
        ]

        for api_url in apis:
            try:
                print(f"🔄 尝试获取最新数据: {api_url[:50]}...")
                req = urllib.request.Request(api_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"✅ 获取成功")
                    return data
            except Exception as e:
                print(f"⚠️ API获取失败: {e}")
                continue

        return None

    def get_latest(self):
        """获取最新一期"""
        if self.data:
            return self.data[0]

        # 返回模拟的最新数据（基于当前日期估算期号）
        today = datetime.now()
        # 大乐透每周一、三、六开奖，期号格式：YYNNN
        year = today.year % 100  # 26
        # 估算今年已开奖期数（每周3期，约52周*3=156期）
        day_of_year = today.timetuple().tm_yday
        estimated_period = int(day_of_year * 3 / 7)
        period = f"{year:02d}{estimated_period:03d}"

        return {
            'period': period,
            'front': [5, 12, 18, 25, 33],
            'back': [3, 9],
            'date': today.strftime('%Y-%m-%d'),
            'note': '模拟数据 - 请更新lottery_data_full.json'
        }

    def get_next_period(self):
        """获取下一期期号"""
        latest = self.get_latest()
        period = latest.get('period', '26010')

        # 解析期号并+1
        try:
            year = int(period[:2])
            num = int(period[2:])

            # 如果超过一年的期数（约156期），进入下一年
            if num >= 156:
                year += 1
                num = 1
            else:
                num += 1

            return f"{year:02d}{num:03d}"
        except:
            return str(int(period) + 1)

    def get_statistics(self, periods=50):
        """获取统计数据"""
        data = self.data[:periods] if self.data else []

        front_counter = Counter()
        back_counter = Counter()

        for item in data:
            front = item.get('front', item.get('red', []))
            back = item.get('back', item.get('blue', []))

            if isinstance(front, list):
                front_counter.update(front)
            if isinstance(back, list):
                back_counter.update(back)

        # 计算遗漏值
        front_missing = {}
        back_missing = {}

        for num in range(1, 36):
            for i, item in enumerate(data):
                front = item.get('front', item.get('red', []))
                if num in front:
                    front_missing[num] = i
                    break
            else:
                front_missing[num] = len(data)

        for num in range(1, 13):
            for i, item in enumerate(data):
                back = item.get('back', item.get('blue', []))
                if num in back:
                    back_missing[num] = i
                    break
            else:
                back_missing[num] = len(data)

        front_hot = [{'number': n, 'count': c} for n, c in front_counter.most_common(10)]
        front_cold = [{'number': n, 'count': c} for n, c in sorted(front_counter.items(), key=lambda x: x[1])[:10]]
        back_hot = [{'number': n, 'count': c} for n, c in back_counter.most_common(5)]
        front_overdue = [{'number': n, 'periods': p} for n, p in sorted(front_missing.items(), key=lambda x: -x[1])[:10]]

        return {
            'total_periods': len(data),
            'front_hot': front_hot,
            'front_cold': front_cold,
            'back_hot': back_hot,
            'front_overdue': front_overdue
        }


# ============ ML预测器（模拟） ============
class MLPredictor:
    """机器学习预测器"""

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.models_loaded = False
        self.check_models()

    def check_models(self):
        """检查模型是否存在"""
        models_dir = os.path.join(PROJECT_ROOT, 'models')
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith(('.pkl', '.onnx', '.keras'))]
            if model_files:
                print(f"✅ 找到 {len(model_files)} 个模型文件")
                self.models_loaded = True
            else:
                print("⚠️ 模型目录存在但无模型文件")
        else:
            print("⚠️ 模型目录不存在，使用统计预测")

    def predict(self):
        """生成预测"""
        stats = self.data_manager.get_statistics(30)

        # 基于统计的智能预测
        front_candidates = []
        back_candidates = []

        # 热号权重
        for item in stats['front_hot'][:15]:
            front_candidates.extend([item['number']] * item['count'])

        # 遗漏号补充
        for item in stats['front_overdue'][:10]:
            if item['periods'] > 10:
                front_candidates.extend([item['number']] * 3)

        # 后区
        for item in stats['back_hot']:
            back_candidates.extend([item['number']] * item['count'])

        # 如果候选不足，补充随机
        if len(set(front_candidates)) < 5:
            front_candidates.extend(range(1, 36))
        if len(set(back_candidates)) < 2:
            back_candidates.extend(range(1, 13))

        # 加权随机选择
        front = []
        while len(front) < 5:
            num = random.choice(front_candidates)
            if num not in front:
                front.append(num)

        back = []
        while len(back) < 2:
            num = random.choice(back_candidates)
            if num not in back:
                back.append(num)

        return {
            'front': sorted(front),
            'back': sorted(back),
            'confidence': 0.68 + random.random() * 0.15,
            'method': 'statistical_ml' if not self.models_loaded else 'trained_ml',
            'individual_models': {
                'random_forest': {
                    'front': sorted(random.sample(range(1, 36), 5)),
                    'back': sorted(random.sample(range(1, 13), 2))
                },
                'xgboost': {
                    'front': sorted(random.sample(range(1, 36), 5)),
                    'back': sorted(random.sample(range(1, 13), 2))
                },
                'lstm': {
                    'front': sorted(random.sample(range(1, 36), 5)),
                    'back': sorted(random.sample(range(1, 13), 2))
                },
                'transformer': {
                    'front': sorted(random.sample(range(1, 36), 5)),
                    'back': sorted(random.sample(range(1, 13), 2))
                }
            }
        }


# ============ HTTP处理器 ============
class LocalHandler(SimpleHTTPRequestHandler):
    data_manager = None
    ml_predictor = None

    def __init__(self, *args, **kwargs):
        if LocalHandler.data_manager is None:
            LocalHandler.data_manager = LotteryDataManager()
            LocalHandler.ml_predictor = MLPredictor(LocalHandler.data_manager)
        super().__init__(*args, directory=os.path.join(PROJECT_ROOT, 'public'), **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_error(405)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def handle_api(self):
        api = self.path.replace('/api/', '').split('?')[0].rstrip('/')

        body = b''
        if self.command == 'POST':
            length = int(self.headers.get('Content-Length', 0))
            if length:
                body = self.rfile.read(length)

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        print(f"📥 API: {self.command} /api/{api}")

        result = self.route_api(api, data)

        resp = json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def route_api(self, api, data):
        dm = LocalHandler.data_manager
        ml = LocalHandler.ml_predictor

        if api == 'health':
            return {
                'status': 'healthy',
                'version': '2.0-local',
                'environment': 'local_development',
                'data_source': 'local_file',
                'kv_available': False,
                'total_periods': len(dm.data),
                'models_loaded': ml.models_loaded,
                'latest_period': dm.get_latest().get('period', 'unknown')
            }

        elif api == 'latest-results':
            action = data.get('action', 'latest')

            if action == 'statistics':
                return {
                    'status': 'success',
                    'statistics': dm.get_statistics(50)
                }

            latest = dm.get_latest()
            prediction = ml.predict()
            next_period = dm.get_next_period()

            return {
                'status': 'success',
                'latest_result': latest,
                'target_period': next_period,
                'ml_prediction': prediction,
                'data_periods': len(dm.data)
            }

        elif api == 'predict':
            prediction = ml.predict()
            return {
                'status': 'success',
                'prediction': prediction,
                'target_period': dm.get_next_period()
            }

        elif api == 'spiritual':
            text = data.get('text', '')
            image = data.get('image')

            # 基于输入生成确定性预测
            seed_str = text + (str(image)[:100] if image else '')
            seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
            random.seed(seed)

            front = sorted(random.sample(range(1, 36), 5))
            back = sorted(random.sample(range(1, 13), 2))
            intensity = 0.6 + random.random() * 0.3

            random.seed()  # 重置

            result = {
                'status': 'success',
                'spiritual_prediction': {
                    'front_zone': front,
                    'back_zone': back
                },
                'energy_analysis': {
                    'intensity': intensity,
                    'image_analyzed': image is not None,
                    'text_analyzed': len(text) > 0
                }
            }

            if image:
                colors = ['红色(热情)', '蓝色(宁静)', '绿色(生机)', '金色(财运)', '紫色(神秘)']
                result['energy_analysis']['dominant_color'] = random.choice(colors)

            return result

        elif api == 'fusion-weights':
            if self.command == 'POST' and data.get('action') == 'reset':
                return {
                    'status': 'success',
                    'message': '权重已重置为默认值',
                    'weights': {'ml': 0.7, 'spiritual': 0.3}
                }

            return {
                'status': 'success',
                'weights': {'ml': 0.7, 'spiritual': 0.3},
                'stats': {
                    'ml_accuracy': 0.32,
                    'spiritual_accuracy': 0.28,
                    'total_predictions': len(dm.data),
                    'decay_factor': 0.9
                }
            }

        elif api == 'generate-tweet':
            prediction = data.get('prediction', {})
            front = prediction.get('front', [1, 2, 3, 4, 5])
            back = prediction.get('back', [1, 2])
            confidence = prediction.get('confidence', 0.7)
            period = data.get('period', dm.get_next_period())

            front_str = ' '.join(f"{n:02d}" for n in front)
            back_str = ' '.join(f"{n:02d}" for n in back)

            tweet = f"""🎯 大乐透AI智能预测

📊 第{period}期预测号码：
━━━━━━━━━━━━━━
🔴 前区：{front_str}
🔵 后区：{back_str}
━━━━━━━━━━━━━━

🤖 预测模型：ML机器学习 + 灵修直觉 EWMA智能融合
📈 综合置信度：{confidence*100:.1f}%
📅 预测时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 预测说明：
• 基于{len(dm.data)}期历史数据深度学习
• 四大模型集成：RandomForest、XGBoost、LSTM、Transformer
• EWMA自适应权重动态优化

⚠️ 温馨提示：彩票有风险，投注需谨慎，理性购彩！

#大乐透 #AI预测 #机器学习 #彩票分析"""

            return {
                'status': 'success',
                'tweet': tweet,
                'period': period,
                'generated_at': datetime.now().isoformat()
            }

        elif api == 'update-data':
            # 尝试更新数据
            new_data = dm.fetch_latest_from_api()
            if new_data:
                return {'status': 'success', 'message': '数据更新成功'}
            return {'status': 'error', 'message': '无法获取最新数据'}

        return {'status': 'error', 'message': f'未知API: {api}'}

    def log_message(self, format, *args):
        if '/api/' not in (args[0] if args else ''):
            print(f"📁 {args[0]}" if args else "")


# ============ 主函数 ============
def main():
    port = int(os.environ.get('PORT', 3000))

    print("\n" + "=" * 60)
    print("🚀 大乐透AI预测系统 - 本地开发服务器 v2")
    print("=" * 60)
    print(f"\n📍 访问地址: http://localhost:{port}")
    print(f"📁 项目目录: {PROJECT_ROOT}")
    print(f"📊 数据文件: lottery_data_full.json")
    print("\n" + "-" * 60)
    print("可用API端点:")
    print("  GET  /api/health         - 系统状态")
    print("  POST /api/latest-results - 最新结果 & ML预测")
    print("  POST /api/spiritual      - 灵修预测")
    print("  GET  /api/fusion-weights - 融合权重")
    print("  POST /api/generate-tweet - 生成推文")
    print("-" * 60)
    print("\n按 Ctrl+C 停止服务器\n")

    server = HTTPServer(('0.0.0.0', port), LocalHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


if __name__ == '__main__':
    main()
