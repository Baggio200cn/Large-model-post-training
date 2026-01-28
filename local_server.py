#!/usr/bin/env python3
"""
本地开发服务器 - 用于测试和调试
无需Vercel，本地即可运行完整功能
"""
import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import importlib.util

# 设置项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'api'))

# API处理器映射
API_HANDLERS = {}

def load_api_handler(api_name):
    """动态加载API处理器"""
    if api_name in API_HANDLERS:
        return API_HANDLERS[api_name]

    # 尝试加载API模块
    api_file = os.path.join(PROJECT_ROOT, 'api', f'{api_name}.py')
    if not os.path.exists(api_file):
        return None

    try:
        spec = importlib.util.spec_from_file_location(api_name, api_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找handler类
        if hasattr(module, 'handler'):
            API_HANDLERS[api_name] = module.handler
            return module.handler
    except Exception as e:
        print(f"加载API模块失败 {api_name}: {e}")

    return None


class LocalDevHandler(SimpleHTTPRequestHandler):
    """本地开发服务器处理器"""

    def __init__(self, *args, **kwargs):
        # 设置静态文件目录
        self.directory = os.path.join(PROJECT_ROOT, 'public')
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        # API请求
        if path.startswith('/api/'):
            self.handle_api_request('GET')
            return

        # 静态文件
        if path == '/':
            self.path = '/index.html'

        super().do_GET()

    def do_POST(self):
        """处理POST请求"""
        if self.path.startswith('/api/'):
            self.handle_api_request('POST')
        else:
            self.send_error(405, 'Method Not Allowed')

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def handle_api_request(self, method):
        """处理API请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        # 提取API名称 /api/predict -> predict
        api_name = path.replace('/api/', '').replace('/', '-').rstrip('-')
        if not api_name:
            api_name = 'index'

        print(f"\n{'='*50}")
        print(f"📥 API请求: {method} {path}")
        print(f"   处理器: {api_name}.py")

        # 读取请求体
        body = b''
        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                print(f"   请求体: {body.decode('utf-8', errors='ignore')[:200]}...")

        # 创建模拟的请求/响应对象
        class MockRequest:
            def __init__(self, handler, method, body):
                self.method = method
                self.path = handler.path
                self.headers = handler.headers
                self.body = body

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.headers = {'Content-Type': 'application/json'}
                self.body = b''

            def set_status(self, code):
                self.status_code = code

            def set_header(self, key, value):
                self.headers[key] = value

            def write(self, data):
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self.body = data

        # 尝试直接调用API处理函数
        response_data = None
        try:
            response_data = self.call_api_directly(api_name, method, body)
        except Exception as e:
            print(f"   ❌ 调用失败: {e}")
            import traceback
            traceback.print_exc()
            response_data = {'error': str(e), 'status': 'error'}

        # 发送响应
        response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
        response_bytes = response_json.encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(response_bytes))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

        print(f"   ✅ 响应: {len(response_bytes)} bytes")

    def call_api_directly(self, api_name, method, body):
        """直接调用API处理逻辑"""
        # 解析请求体
        request_data = {}
        if body:
            try:
                request_data = json.loads(body.decode('utf-8'))
            except:
                pass

        # 根据API名称调用相应的处理函数
        if api_name == 'health':
            return self.handle_health()
        elif api_name == 'hello':
            return self.handle_hello()
        elif api_name == 'predict':
            return self.handle_predict(request_data)
        elif api_name == 'latest-results':
            return self.handle_latest_results(request_data)
        elif api_name == 'spiritual':
            return self.handle_spiritual(request_data)
        elif api_name == 'fusion-weights':
            return self.handle_fusion_weights(request_data, method)
        elif api_name == 'generate-tweet':
            return self.handle_generate_tweet(request_data)
        else:
            return {'error': f'Unknown API: {api_name}', 'status': 'error'}

    def handle_health(self):
        """健康检查"""
        return {
            'status': 'healthy',
            'version': '2.0.0-local',
            'environment': 'local',
            'data_source': 'local',
            'kv_available': False,
            'total_periods': 100,
            'message': '本地开发服务器运行正常'
        }

    def handle_hello(self):
        """Hello测试"""
        return {'message': 'Hello from local server!', 'status': 'success'}

    def handle_predict(self, data):
        """ML预测"""
        try:
            # 尝试导入真正的预测模块
            from utils._real_ml_predictor import RealMLPredictor
            predictor = RealMLPredictor()
            result = predictor.ensemble_predict()
            return {
                'status': 'success',
                'prediction': result,
                'source': 'local_ml'
            }
        except ImportError as e:
            print(f"   导入预测模块失败: {e}")
            # 返回模拟数据
            import random
            front = sorted(random.sample(range(1, 36), 5))
            back = sorted(random.sample(range(1, 13), 2))
            return {
                'status': 'success',
                'prediction': {
                    'front': front,
                    'back': back,
                    'confidence': 0.75,
                    'model': 'fallback'
                },
                'source': 'local_fallback',
                'note': 'ML模块未加载，使用随机预测'
            }

    def handle_latest_results(self, data):
        """最新结果和统计"""
        action = data.get('action', 'latest')

        # 加载本地数据
        data_file = os.path.join(PROJECT_ROOT, 'lottery_data_full.json')
        lottery_data = []
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                lottery_data = json.load(f)

        if action == 'latest' or action == 'ml_predict':
            latest = lottery_data[0] if lottery_data else None

            # 生成预测
            import random
            front = sorted(random.sample(range(1, 36), 5))
            back = sorted(random.sample(range(1, 13), 2))

            return {
                'status': 'success',
                'latest_result': latest,
                'target_period': str(int(latest['period']) + 1) if latest else '25142',
                'ml_prediction': {
                    'front': front,
                    'back': back,
                    'confidence': 0.72,
                    'individual_models': {
                        'random_forest': {'front': sorted(random.sample(range(1, 36), 5)), 'back': sorted(random.sample(range(1, 13), 2))},
                        'xgboost': {'front': sorted(random.sample(range(1, 36), 5)), 'back': sorted(random.sample(range(1, 13), 2))},
                        'lstm': {'front': sorted(random.sample(range(1, 36), 5)), 'back': sorted(random.sample(range(1, 13), 2))},
                        'transformer': {'front': sorted(random.sample(range(1, 36), 5)), 'back': sorted(random.sample(range(1, 13), 2))}
                    }
                }
            }

        elif action == 'statistics':
            # 统计分析
            from collections import Counter
            front_counter = Counter()
            back_counter = Counter()

            for item in lottery_data[:50]:
                if 'front' in item:
                    front_counter.update(item['front'])
                if 'back' in item:
                    back_counter.update(item['back'])

            front_hot = [{'number': n, 'count': c} for n, c in front_counter.most_common(5)]
            front_cold = [{'number': n, 'count': c} for n, c in front_counter.most_common()[-5:]]
            back_hot = [{'number': n, 'count': c} for n, c in back_counter.most_common(3)]

            return {
                'status': 'success',
                'statistics': {
                    'total_periods': len(lottery_data),
                    'front_hot': front_hot,
                    'front_cold': front_cold,
                    'back_hot': back_hot,
                    'front_overdue': []
                }
            }

        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def handle_spiritual(self, data):
        """灵修预测"""
        text = data.get('text', '')
        image = data.get('image')

        import random
        import hashlib

        # 基于输入生成确定性的随机数
        seed_str = text + str(image)[:100] if image else text
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        front = sorted(random.sample(range(1, 36), 5))
        back = sorted(random.sample(range(1, 13), 2))
        intensity = 0.6 + random.random() * 0.3

        response = {
            'status': 'success',
            'spiritual_prediction': {
                'front_zone': front,
                'back_zone': back
            },
            'energy_analysis': {
                'intensity': intensity,
                'image_analyzed': image is not None
            }
        }

        if image:
            response['energy_analysis']['dominant_color'] = random.choice(['红', '蓝', '绿', '金', '紫'])

        # 重置随机种子
        random.seed()

        return response

    def handle_fusion_weights(self, data, method):
        """融合权重管理"""
        if method == 'GET':
            return {
                'status': 'success',
                'weights': {
                    'ml': 0.7,
                    'spiritual': 0.3
                },
                'stats': {
                    'ml_accuracy': 0.35,
                    'spiritual_accuracy': 0.28,
                    'total_predictions': 50,
                    'decay_factor': 0.9
                },
                'note': '本地开发模式 - 使用默认权重'
            }
        elif method == 'POST':
            action = data.get('action')
            if action == 'reset':
                return {
                    'status': 'success',
                    'message': '权重已重置',
                    'weights': {'ml': 0.7, 'spiritual': 0.3}
                }
        return {'status': 'error', 'message': 'Invalid request'}

    def handle_generate_tweet(self, data):
        """生成推文"""
        prediction = data.get('prediction', {})
        front = prediction.get('front', [1, 2, 3, 4, 5])
        back = prediction.get('back', [1, 2])

        tweet = f"""🎯 大乐透AI预测

📊 第25142期预测号码：
前区：{' '.join(str(n).zfill(2) for n in front)}
后区：{' '.join(str(n).zfill(2) for n in back)}

🤖 预测来源：ML机器学习 + 灵修直觉融合
📈 综合置信度：72.5%

⚠️ 仅供参考，理性投注
#大乐透 #AI预测 #机器学习"""

        return {
            'status': 'success',
            'tweet': tweet
        }

    def log_message(self, format, *args):
        """自定义日志格式"""
        if '/api/' in args[0] if args else False:
            return  # API请求已有自定义日志
        print(f"📁 {args[0]}")


def main():
    """启动本地开发服务器"""
    port = int(os.environ.get('PORT', 3000))

    print("=" * 60)
    print("🚀 大乐透AI预测系统 - 本地开发服务器")
    print("=" * 60)
    print(f"\n📍 服务地址: http://localhost:{port}")
    print(f"📁 静态文件: {os.path.join(PROJECT_ROOT, 'public')}")
    print(f"🔌 API目录: {os.path.join(PROJECT_ROOT, 'api')}")
    print("\n可用API端点:")
    print("  - GET  /api/health         - 健康检查")
    print("  - GET  /api/hello          - Hello测试")
    print("  - POST /api/predict        - ML预测")
    print("  - POST /api/latest-results - 最新结果")
    print("  - POST /api/spiritual      - 灵修预测")
    print("  - GET  /api/fusion-weights - 获取权重")
    print("  - POST /api/generate-tweet - 生成推文")
    print("\n" + "=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")

    server = HTTPServer(('0.0.0.0', port), LocalDevHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
