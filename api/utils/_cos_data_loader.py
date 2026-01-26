"""
从腾讯云COS加载数据和模型
支持：
- scikit-learn/xgboost 模型 (.pkl格式)
- ONNX 模型 (.onnx格式) - 用于LSTM/Transformer
提供缓存机制以减少COS请求次数
"""
import os
import sys
import pickle
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# 添加父目录到路径以导入utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.tencent_cos import get_cos_client


# 全局缓存
_cache = {
    'lottery_data': None,
    'lottery_data_timestamp': None,
    'models': {},
    'onnx_sessions': {},  # ONNX推理会话缓存
    'cache_ttl': 3600  # 缓存有效期：1小时
}


def get_lottery_data(force_refresh: bool = False) -> List[Dict]:
    """
    从COS获取彩票历史数据（带缓存）

    Args:
        force_refresh: 是否强制刷新缓存

    Returns:
        彩票历史数据列表
    """
    global _cache

    # 检查缓存
    if not force_refresh and _cache['lottery_data'] is not None:
        if _cache['lottery_data_timestamp'] is not None:
            cache_age = (datetime.now() - _cache['lottery_data_timestamp']).total_seconds()
            if cache_age < _cache['cache_ttl']:
                print(f"📦 使用缓存数据（缓存时间: {cache_age:.0f}秒）")
                return _cache['lottery_data']

    # 从COS加载
    print("📥 从腾讯云COS加载彩票数据...")

    try:
        # 首先尝试从COS加载
        client = get_cos_client()
        data_dict = client.download_json('data/lottery_history.json')

        lottery_data = data_dict.get('data', [])

        # 更新缓存
        _cache['lottery_data'] = lottery_data
        _cache['lottery_data_timestamp'] = datetime.now()

        print(f"✅ 成功加载 {len(lottery_data)} 期数据")

        return lottery_data

    except Exception as e:
        print(f"⚠️  从COS加载失败: {str(e)}")

        # 回退到本地数据
        print("📂 回退到本地数据...")
        from _lottery_data import LOTTERY_HISTORY

        lottery_data = []
        for record in LOTTERY_HISTORY:
            if len(record) < 9:
                continue

            lottery_data.append({
                'period': record[0],
                'front_zone': [record[1], record[2], record[3], record[4], record[5]],
                'back_zone': [record[6], record[7]],
                'date': record[8] if len(record) > 8 else ""
            })

        # 更新缓存
        _cache['lottery_data'] = lottery_data
        _cache['lottery_data_timestamp'] = datetime.now()

        print(f"✅ 使用本地数据：{len(lottery_data)} 期")

        return lottery_data


def load_onnx_model(model_name: str, force_refresh: bool = False) -> Any:
    """
    从COS加载ONNX模型（用于LSTM/Transformer）

    Args:
        model_name: 模型名称（如：lstm_front, transformer_back）
        force_refresh: 是否强制刷新缓存

    Returns:
        ONNX InferenceSession 对象
    """
    global _cache

    # 检查缓存
    if not force_refresh and model_name in _cache['onnx_sessions']:
        print(f"📦 使用缓存ONNX会话: {model_name}")
        return _cache['onnx_sessions'][model_name]

    print(f"📥 从腾讯云COS加载ONNX模型: {model_name}")

    try:
        import onnxruntime as ort
        import tempfile

        client = get_cos_client()
        cos_path = f'models/{model_name}.onnx'

        # 下载到临时文件
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            temp_path = f.name

        try:
            client.download_file(cos_path, temp_path)

            # 创建ONNX推理会话
            session = ort.InferenceSession(
                temp_path,
                providers=['CPUExecutionProvider']
            )

            # 更新缓存
            _cache['onnx_sessions'][model_name] = session

            print(f"✅ 成功加载ONNX模型: {model_name}")
            return session

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except ImportError:
        print("❌ onnxruntime 未安装")
        raise Exception("需要安装 onnxruntime: pip install onnxruntime")

    except Exception as e:
        print(f"❌ 从COS加载ONNX模型失败: {str(e)}")
        raise Exception(f"无法加载ONNX模型 {model_name}: {str(e)}")


def load_sklearn_model(model_name: str, force_refresh: bool = False) -> Any:
    """
    从COS加载sklearn/xgboost模型（.pkl格式）

    Args:
        model_name: 模型名称（如：xgboost_front, random_forest_back）
        force_refresh: 是否强制刷新缓存

    Returns:
        加载的模型对象
    """
    global _cache

    # 检查缓存
    if not force_refresh and model_name in _cache['models']:
        print(f"📦 使用缓存模型: {model_name}")
        return _cache['models'][model_name]

    print(f"📥 从腾讯云COS加载sklearn模型: {model_name}")

    try:
        client = get_cos_client()
        cos_path = f'models/{model_name}.pkl'

        model = client.download_pickle(cos_path)

        # 更新缓存
        _cache['models'][model_name] = model

        print(f"✅ 成功加载sklearn模型: {model_name}")
        return model

    except Exception as e:
        print(f"❌ 从COS加载sklearn模型失败: {str(e)}")
        raise Exception(f"无法加载模型 {model_name}: {str(e)}")


def load_model_from_cos(model_name: str, force_refresh: bool = False) -> Any:
    """
    从COS加载机器学习模型（自动识别类型）

    Args:
        model_name: 模型名称
        force_refresh: 是否强制刷新缓存

    Returns:
        加载的模型对象或ONNX会话
    """
    # 根据模型名称判断类型
    if 'lstm' in model_name.lower() or 'transformer' in model_name.lower():
        return load_onnx_model(model_name, force_refresh)
    else:
        return load_sklearn_model(model_name, force_refresh)


def get_models_info() -> Dict[str, Any]:
    """
    获取所有可用模型的信息

    Returns:
        模型信息字典
    """
    try:
        client = get_cos_client()

        # 尝试加载模型信息文件
        models_info = client.download_json('models/models_info.json')
        return models_info

    except Exception as e:
        print(f"⚠️  无法加载模型信息: {str(e)}")
        # 返回默认模型配置
        return {
            'models': {
                'xgboost_front': {'type': 'sklearn', 'format': 'pkl', 'description': 'XGBoost前区预测'},
                'xgboost_back': {'type': 'sklearn', 'format': 'pkl', 'description': 'XGBoost后区预测'},
                'random_forest_front': {'type': 'sklearn', 'format': 'pkl', 'description': 'RandomForest前区预测'},
                'random_forest_back': {'type': 'sklearn', 'format': 'pkl', 'description': 'RandomForest后区预测'},
                'lstm_front': {'type': 'onnx', 'format': 'onnx', 'description': 'LSTM前区预测'},
                'lstm_back': {'type': 'onnx', 'format': 'onnx', 'description': 'LSTM后区预测'},
                'transformer_front': {'type': 'onnx', 'format': 'onnx', 'description': 'Transformer前区预测'},
                'transformer_back': {'type': 'onnx', 'format': 'onnx', 'description': 'Transformer后区预测'},
            },
            'version': '2.0.0',
            'updated': datetime.now().isoformat()
        }


def clear_cache():
    """清除所有缓存"""
    global _cache

    _cache['lottery_data'] = None
    _cache['lottery_data_timestamp'] = None
    _cache['models'].clear()
    _cache['onnx_sessions'].clear()

    print("🗑️  缓存已清除")


def get_cache_status() -> Dict[str, Any]:
    """获取缓存状态"""
    global _cache

    status = {
        'lottery_data_cached': _cache['lottery_data'] is not None,
        'sklearn_models_cached': list(_cache['models'].keys()),
        'onnx_models_cached': list(_cache['onnx_sessions'].keys()),
        'cache_ttl': _cache['cache_ttl']
    }

    if _cache['lottery_data_timestamp']:
        cache_age = (datetime.now() - _cache['lottery_data_timestamp']).total_seconds()
        status['lottery_data_cache_age'] = cache_age

    return status


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("测试从COS加载数据和模型")
    print("=" * 60)

    try:
        # 测试加载彩票数据
        data = get_lottery_data()
        print(f"\n✅ 成功加载 {len(data)} 期彩票数据")
        print(f"   最新一期: {data[0]['period']}")

        # 测试缓存状态
        status = get_cache_status()
        print(f"\n📊 缓存状态:")
        print(json.dumps(status, indent=2, ensure_ascii=False))

        # 测试模型信息
        models_info = get_models_info()
        print(f"\n📋 可用模型:")
        print(json.dumps(models_info, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
