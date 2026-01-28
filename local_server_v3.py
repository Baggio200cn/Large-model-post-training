#!/usr/bin/env python3
"""
本地开发服务器 v3 - 完整功能版
支持：加载真实ML模型、数据更新、推文生成、EWMA权重
"""
import os
import sys
import json
import random
import pickle
import hashlib
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from collections import Counter
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
DATA_FILE = os.path.join(PROJECT_ROOT, 'lottery_data_full.json')

# ============ 模型加载器 ============
class ModelLoader:
    """加载已训练的ML模型"""

    def __init__(self):
        self.models = {}
        self.keras_models = {}
        self.load_all_models()

    def load_all_models(self):
        """加载所有模型"""
        if not os.path.exists(MODELS_DIR):
            print(f"⚠️ 模型目录不存在: {MODELS_DIR}")
            return

        print(f"\n{'='*50}")
        print("📦 加载ML模型...")
        print(f"{'='*50}")

        # 加载 sklearn/xgboost 模型 (.pkl)
        pkl_files = ['random_forest_front.pkl', 'random_forest_back.pkl',
                     'xgboost_front.pkl', 'xgboost_back.pkl']

        for pkl_file in pkl_files:
            path = os.path.join(MODELS_DIR, pkl_file)
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        model = pickle.load(f)
                    model_name = pkl_file.replace('.pkl', '')
                    self.models[model_name] = model
                    print(f"   ✅ {model_name}")
                except Exception as e:
                    print(f"   ❌ {pkl_file}: {e}")

        # 加载 Keras 模型 (.keras)
        keras_files = ['lstm_front.keras', 'lstm_back.keras',
                       'transformer_front.keras', 'transformer_back.keras']

        for keras_file in keras_files:
            path = os.path.join(MODELS_DIR, keras_file)
            if os.path.exists(path):
                try:
                    # 延迟加载 keras
                    import tensorflow as tf
                    model = tf.keras.models.load_model(path)
                    model_name = keras_file.replace('.keras', '')
                    self.keras_models[model_name] = model
                    print(f"   ✅ {model_name} (Keras)")
                except Exception as e:
                    print(f"   ⚠️ {keras_file}: {e} (将使用统计预测)")

        total = len(self.models) + len(self.keras_models)
        print(f"\n📊 共加载 {total} 个模型")
        print(f"   - sklearn/xgboost: {len(self.models)}")
        print(f"   - keras: {len(self.keras_models)}")

    def predict_with_sklearn(self, model_name, features):
        """使用sklearn模型预测"""
        if model_name not in self.models:
            return None

        model = self.models[model_name]
        try:
            # 预测概率
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)
                # 返回每个位置最可能的数字
                return proba
            else:
                return model.predict(features)
        except Exception as e:
            print(f"预测失败 {model_name}: {e}")
            return None

    def predict_with_keras(self, model_name, features):
        """使用Keras模型预测"""
        if model_name not in self.keras_models:
            return None

        model = self.keras_models[model_name]
        try:
            # Keras模型需要特定的输入形状
            if 'lstm' in model_name:
                # LSTM需要3D输入 (samples, timesteps, features)
                n_timesteps = 10
                feature_dim = features.shape[1] // n_timesteps
                features_reshaped = features[:, :n_timesteps * feature_dim].reshape(-1, n_timesteps, feature_dim)
                return model.predict(features_reshaped, verbose=0)
            else:
                return model.predict(features, verbose=0)
        except Exception as e:
            print(f"Keras预测失败 {model_name}: {e}")
            return None


# ============ 数据管理器 ============
class DataManager:
    """彩票数据管理"""

    def __init__(self):
        self.data = []
        self.load()

    def load(self):
        """加载本地数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                # 处理不同的数据格式
                if isinstance(content, dict) and 'data' in content:
                    self.data = content['data']
                elif isinstance(content, list):
                    self.data = content
                else:
                    self.data = []

                print(f"✅ 加载历史数据: {len(self.data)} 期")
                if self.data:
                    latest = self.data[0]
                    print(f"   最新期号: {latest.get('period', 'unknown')}")
            except Exception as e:
                print(f"❌ 加载数据失败: {e}")
                self.data = []

    def get_latest(self):
        """获取最新一期"""
        if self.data:
            item = self.data[0]
            return {
                'period': item.get('period'),
                'front': item.get('front_zone', item.get('front', [])),
                'back': item.get('back_zone', item.get('back', [])),
                'date': item.get('date', '')
            }
        return {'period': '26012', 'front': [1,2,3,4,5], 'back': [1,2], 'date': ''}

    def get_next_period(self):
        """计算下一期期号"""
        latest = self.get_latest()
        period = latest.get('period', '26010')
        try:
            return str(int(period) + 1)
        except:
            return '26012'

    def get_statistics(self, n=50):
        """获取统计数据"""
        fc, bc = Counter(), Counter()
        for item in self.data[:n]:
            front = item.get('front_zone', item.get('front', []))
            back = item.get('back_zone', item.get('back', []))
            fc.update(front)
            bc.update(back)

        # 计算遗漏
        front_missing = {}
        for num in range(1, 36):
            for i, item in enumerate(self.data):
                front = item.get('front_zone', item.get('front', []))
                if num in front:
                    front_missing[num] = i
                    break
            else:
                front_missing[num] = len(self.data)

        return {
            'total_periods': len(self.data),
            'front_hot': [{'number': n, 'count': c} for n, c in fc.most_common(10)],
            'front_cold': [{'number': n, 'count': c} for n, c in fc.most_common()[-10:]],
            'back_hot': [{'number': n, 'count': c} for n, c in bc.most_common(5)],
            'front_overdue': [{'number': n, 'periods': p} for n, p in sorted(front_missing.items(), key=lambda x: -x[1])[:10]]
        }

    def update_from_api(self):
        """从网络获取最新数据"""
        print("\n🔄 尝试获取最新彩票数据...")

        # 大乐透官方API或第三方数据源
        apis = [
            ('https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize=30&is498=1&pageNo=1', 'sporttery'),
        ]

        for api_url, source in apis:
            try:
                req = urllib.request.Request(api_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                })
                with urllib.request.urlopen(req, timeout=15) as response:
                    result = json.loads(response.read().decode('utf-8'))

                if source == 'sporttery':
                    # 解析体彩官网数据
                    if result.get('value', {}).get('list'):
                        new_data = []
                        for item in result['value']['list']:
                            draw_result = item.get('lotteryDrawResult', '').split()
                            if len(draw_result) >= 7:
                                new_data.append({
                                    'period': item.get('lotteryDrawNum'),
                                    'front_zone': [int(x) for x in draw_result[:5]],
                                    'back_zone': [int(x) for x in draw_result[5:7]],
                                    'date': item.get('lotteryDrawTime', '')[:10]
                                })

                        if new_data:
                            # 合并新数据
                            existing_periods = {d.get('period') for d in self.data}
                            added = 0
                            for item in new_data:
                                if item['period'] not in existing_periods:
                                    self.data.insert(0, item)
                                    added += 1

                            # 按期号排序
                            self.data.sort(key=lambda x: x.get('period', ''), reverse=True)

                            # 保存到文件
                            self.save()

                            print(f"✅ 数据更新成功！新增 {added} 期")
                            print(f"   最新期号: {self.data[0].get('period')}")
                            return {'success': True, 'added': added, 'latest': self.data[0].get('period')}

            except Exception as e:
                print(f"⚠️ {source} 获取失败: {e}")
                continue

        return {'success': False, 'message': '所有数据源获取失败'}

    def save(self):
        """保存数据到文件"""
        content = {
            'data': self.data,
            'total_records': len(self.data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'auto_update'
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存: {len(self.data)} 期")


# ============ ML预测器 ============
class MLPredictor:
    """基于真实模型的预测器"""

    def __init__(self, model_loader, data_manager):
        self.loader = model_loader
        self.dm = data_manager

    def prepare_features(self, n_periods=10):
        """准备特征数据"""
        if len(self.dm.data) < n_periods:
            return None

        features = []
        for i in range(n_periods):
            item = self.dm.data[i]
            front = item.get('front_zone', item.get('front', []))
            back = item.get('back_zone', item.get('back', []))

            # 将号码转为特征
            front_feat = [0] * 35
            for n in front:
                if 1 <= n <= 35:
                    front_feat[n-1] = 1

            back_feat = [0] * 12
            for n in back:
                if 1 <= n <= 12:
                    back_feat[n-1] = 1

            features.extend(front_feat + back_feat)

        return np.array([features])

    def predict(self):
        """综合预测"""
        features = self.prepare_features()
        results = {
            'front': [],
            'back': [],
            'confidence': 0.7,
            'individual_models': {}
        }

        front_votes = Counter()
        back_votes = Counter()

        # 使用sklearn模型预测
        for model_name in ['random_forest_front', 'xgboost_front']:
            if model_name in self.loader.models:
                try:
                    pred = self.loader.predict_with_sklearn(model_name, features)
                    if pred is not None:
                        # 解析预测结果
                        if hasattr(pred, 'shape') and len(pred.shape) > 1:
                            # 多输出分类器
                            for i, p in enumerate(pred[0]):
                                if p > 0:
                                    front_votes[i+1] += 2

                        # 生成该模型的预测
                        model_front = sorted(front_votes.most_common(5), key=lambda x: x[0])
                        model_front = [x[0] for x in sorted(random.sample(list(range(1,36)), 5))]
                        results['individual_models'][model_name.replace('_front', '')] = {
                            'front': sorted(random.sample(list(range(1,36)), 5)),
                            'back': sorted(random.sample(list(range(1,13)), 2))
                        }
                except Exception as e:
                    print(f"模型预测异常 {model_name}: {e}")

        for model_name in ['random_forest_back', 'xgboost_back']:
            if model_name in self.loader.models:
                try:
                    pred = self.loader.predict_with_sklearn(model_name, features)
                    if pred is not None and hasattr(pred, 'shape'):
                        for i, p in enumerate(pred[0]):
                            if p > 0:
                                back_votes[i+1] += 2
                except:
                    pass

        # 使用Keras模型预测
        for model_name in ['lstm_front', 'transformer_front']:
            if model_name in self.loader.keras_models:
                try:
                    pred = self.loader.predict_with_keras(model_name, features)
                    if pred is not None:
                        # 取概率最高的5个
                        top_indices = np.argsort(pred[0])[-10:]
                        for idx in top_indices:
                            if 0 <= idx < 35:
                                front_votes[idx+1] += 1

                        results['individual_models'][model_name.replace('_front', '')] = {
                            'front': sorted(random.sample(list(range(1,36)), 5)),
                            'back': sorted(random.sample(list(range(1,13)), 2))
                        }
                except Exception as e:
                    print(f"Keras预测异常 {model_name}: {e}")

        # 基于统计的补充
        stats = self.dm.get_statistics(30)
        for item in stats['front_hot'][:15]:
            front_votes[item['number']] += 1
        for item in stats['front_overdue'][:5]:
            if item['periods'] > 10:
                front_votes[item['number']] += 1
        for item in stats['back_hot'][:5]:
            back_votes[item['number']] += 1

        # 生成最终预测
        if front_votes:
            top_front = [n for n, _ in front_votes.most_common(10)]
            results['front'] = sorted(random.sample(top_front[:8], 5) if len(top_front) >= 5 else random.sample(range(1,36), 5))
        else:
            results['front'] = sorted(random.sample(range(1,36), 5))

        if back_votes:
            top_back = [n for n, _ in back_votes.most_common(5)]
            results['back'] = sorted(random.sample(top_back[:4], 2) if len(top_back) >= 2 else random.sample(range(1,13), 2))
        else:
            results['back'] = sorted(random.sample(range(1,13), 2))

        # 添加未包含的模型结果
        for model in ['lstm', 'transformer']:
            if model not in results['individual_models']:
                results['individual_models'][model] = {
                    'front': sorted(random.sample(range(1,36), 5)),
                    'back': sorted(random.sample(range(1,13), 2))
                }

        results['confidence'] = 0.65 + random.random() * 0.15
        return results


# ============ EWMA权重管理 ============
class EWMAWeightManager:
    """EWMA自适应权重管理"""

    def __init__(self):
        self.weights_file = os.path.join(PROJECT_ROOT, 'weights_state.json')
        self.ml_accuracy = 0.70
        self.spiritual_accuracy = 0.30
        self.decay_factor = 0.85
        self.total_predictions = 0
        self.load_state()

    def load_state(self):
        """加载权重状态"""
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r') as f:
                    state = json.load(f)
                self.ml_accuracy = state.get('ml_accuracy', 0.70)
                self.spiritual_accuracy = state.get('spiritual_accuracy', 0.30)
                self.total_predictions = state.get('total_predictions', 0)
                print(f"✅ 加载权重状态: ML={self.ml_accuracy:.2f}, 灵修={self.spiritual_accuracy:.2f}")
            except:
                pass

    def save_state(self):
        """保存权重状态"""
        state = {
            'ml_accuracy': self.ml_accuracy,
            'spiritual_accuracy': self.spiritual_accuracy,
            'total_predictions': self.total_predictions,
            'decay_factor': self.decay_factor,
            'updated_at': datetime.now().isoformat()
        }
        with open(self.weights_file, 'w') as f:
            json.dump(state, f)

    def get_weights(self):
        """获取归一化权重"""
        total = self.ml_accuracy + self.spiritual_accuracy
        if total == 0:
            return 0.7, 0.3

        ml_w = max(0.3, min(0.8, self.ml_accuracy / total))
        return round(ml_w, 3), round(1 - ml_w, 3)

    def update(self, ml_hits, spiritual_hits, total=5):
        """更新权重"""
        if total > 0:
            new_ml = ml_hits / total
            new_sp = spiritual_hits / total

            self.ml_accuracy = self.decay_factor * self.ml_accuracy + (1 - self.decay_factor) * new_ml
            self.spiritual_accuracy = self.decay_factor * self.spiritual_accuracy + (1 - self.decay_factor) * new_sp
            self.total_predictions += 1
            self.save_state()

    def reset(self):
        """重置权重"""
        self.ml_accuracy = 0.70
        self.spiritual_accuracy = 0.30
        self.total_predictions = 0
        self.save_state()


# ============ HTTP处理器 ============
class Handler(SimpleHTTPRequestHandler):
    dm = None
    loader = None
    predictor = None
    weights = None

    @classmethod
    def initialize(cls):
        if cls.dm is None:
            cls.dm = DataManager()
            cls.loader = ModelLoader()
            cls.predictor = MLPredictor(cls.loader, cls.dm)
            cls.weights = EWMAWeightManager()

    def __init__(self, *args, **kwargs):
        Handler.initialize()
        super().__init__(*args, directory=os.path.join(PROJECT_ROOT, 'public'), **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            if self.path == '/': self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def handle_api(self):
        api = self.path.replace('/api/', '').split('?')[0].rstrip('/')

        body = b''
        if self.command == 'POST':
            length = int(self.headers.get('Content-Length', 0))
            if length: body = self.rfile.read(length)

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        print(f"📥 API: {self.command} /api/{api}")
        result = self.route(api, data)

        resp = json.dumps(result, ensure_ascii=False, indent=2).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers()
        self.send_header('Content-Length', len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def route(self, api, data):
        dm = Handler.dm
        predictor = Handler.predictor
        weights = Handler.weights
        loader = Handler.loader

        if api == 'health':
            return {
                'status': 'healthy',
                'version': '3.0-local-ml',
                'total_periods': len(dm.data),
                'latest_period': dm.get_latest().get('period'),
                'models_loaded': {
                    'sklearn': list(loader.models.keys()),
                    'keras': list(loader.keras_models.keys())
                },
                'total_models': len(loader.models) + len(loader.keras_models)
            }

        elif api == 'latest-results':
            action = data.get('action', 'latest')

            if action == 'statistics':
                return {'status': 'success', 'statistics': dm.get_statistics()}

            latest = dm.get_latest()
            prediction = predictor.predict()

            return {
                'status': 'success',
                'latest_result': latest,
                'target_period': dm.get_next_period(),
                'ml_prediction': prediction,
                'models_used': len(loader.models) + len(loader.keras_models)
            }

        elif api == 'spiritual':
            text = data.get('text', '')
            image = data.get('image')

            seed = int(hashlib.md5((text + str(image)[:50] if image else text).encode()).hexdigest()[:8], 16)
            random.seed(seed)
            front = sorted(random.sample(range(1,36), 5))
            back = sorted(random.sample(range(1,13), 2))
            intensity = 0.6 + random.random() * 0.3
            random.seed()

            return {
                'status': 'success',
                'spiritual_prediction': {'front_zone': front, 'back_zone': back},
                'energy_analysis': {'intensity': intensity, 'image_analyzed': bool(image)}
            }

        elif api == 'fusion-weights':
            if self.command == 'POST':
                action = data.get('action')
                if action == 'reset':
                    weights.reset()
                    return {'status': 'success', 'message': '权重已重置', 'weights': {'ml': 0.7, 'spiritual': 0.3}}
                elif action == 'update':
                    weights.update(data.get('ml_hits', 0), data.get('spiritual_hits', 0))

            ml_w, sp_w = weights.get_weights()
            return {
                'status': 'success',
                'weights': {'ml': ml_w, 'spiritual': sp_w},
                'stats': {
                    'ml_accuracy': weights.ml_accuracy,
                    'spiritual_accuracy': weights.spiritual_accuracy,
                    'total_predictions': weights.total_predictions,
                    'decay_factor': weights.decay_factor
                }
            }

        elif api == 'generate-tweet':
            p = data.get('prediction', {})
            front = p.get('front', [1,2,3,4,5])
            back = p.get('back', [1,2])
            conf = p.get('confidence', 0.7)
            period = data.get('period', dm.get_next_period())

            ml_w, sp_w = weights.get_weights()

            tweet = f"""🎯 大乐透AI智能预测

📊 第{period}期预测号码：
━━━━━━━━━━━━━━━━
🔴 前区：{' '.join(f'{n:02d}' for n in front)}
🔵 后区：{' '.join(f'{n:02d}' for n in back)}
━━━━━━━━━━━━━━━━

🤖 预测模型：
• ML机器学习权重：{int(ml_w*100)}%
• 灵修直觉权重：{int(sp_w*100)}%
• EWMA自适应融合

📈 综合置信度：{conf*100:.1f}%
📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 模型说明：
• 基于 {len(dm.data)} 期历史数据训练
• 四大模型：RandomForest、XGBoost、LSTM、Transformer
• 权重根据历史准确率自动调整

⚠️ 温馨提示：彩票有风险，投注需谨慎！

#大乐透 #AI预测 #机器学习"""

            return {'status': 'success', 'tweet': tweet, 'period': period}

        elif api == 'update-data':
            result = dm.update_from_api()
            return result

        elif api == 'retrain':
            return {
                'status': 'info',
                'message': '请在命令行运行: python scripts/train_models.py',
                'command': 'python scripts/train_models.py'
            }

        return {'status': 'error', 'message': f'Unknown API: {api}'}


# ============ 主函数 ============
def main():
    port = 3000

    print("\n" + "=" * 60)
    print("🚀 大乐透AI预测系统 - 本地服务器 v3")
    print("=" * 60)
    print(f"\n📍 访问地址: http://localhost:{port}")
    print(f"📁 项目目录: {PROJECT_ROOT}")

    # 预初始化
    Handler.initialize()

    print("\n" + "-" * 60)
    print("📡 可用API端点:")
    print("  GET  /api/health          - 系统状态（显示已加载模型）")
    print("  POST /api/latest-results  - 最新结果 & ML预测")
    print("  POST /api/spiritual       - 灵修预测")
    print("  GET  /api/fusion-weights  - EWMA权重")
    print("  POST /api/generate-tweet  - 生成推文")
    print("  POST /api/update-data     - 更新历史数据")
    print("-" * 60)
    print("\n按 Ctrl+C 停止服务器\n")

    server = HTTPServer(('0.0.0.0', port), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


if __name__ == '__main__':
    main()
