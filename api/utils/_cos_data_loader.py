"""
从腾讯云COS加载数据和模型
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


def load_model_from_cos(model_name: str, force_refresh: bool = False) -> Any:
    """
    从COS加载机器学习模型（带缓存）

    Args:
        model_name: 模型名称（如：random_forest_front）
        force_refresh: 是否强制刷新缓存

    Returns:
        加载的模型对象
    """
    global _cache

    # 检查缓存
    if not force_refresh and model_name in _cache['models']:
        print(f"📦 使用缓存模型: {model_name}")
        return _cache['models'][model_name]

    # 从COS加载
    print(f"📥 从腾讯云COS加载模型: {model_name}")

    try:
        client = get_cos_client()

        # 判断文件类型
        if 'lstm' in model_name.lower() or 'transformer' in model_name.lower():
            # Keras模型（.h5格式）
            cos_path = f'models/{model_name}.h5'

            # 下载到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
                temp_path = f.name

            try:
                client.download_file(cos_path, temp_path)

                # 加载Keras模型 - Vercel不支持tensorflow，使用轻量级替代方案
                try:
                    import tensorflow as tf
                    model = tf.keras.models.load_model(temp_path)
                except ImportError:
                    # Vercel环境不支持tensorflow，返回None让调用方使用统计方法
                    print("⚠️  tensorflow未安装，跳过深度学习模型加载")
                    raise Exception("深度学习模型需要tensorflow，Vercel不支持。请使用统计预测方法。")

                # 更新缓存
                _cache['models'][model_name] = model

                print(f"✅ 成功加载Keras模型: {model_name}")
                return model

            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        else:
            # sklearn/xgboost模型（.pkl格式）
            cos_path = f'models/{model_name}.pkl'

            model = client.download_pickle(cos_path)

            # 更新缓存
            _cache['models'][model_name] = model

            print(f"✅ 成功加载模型: {model_name}")
            return model

    except Exception as e:
        print(f"❌ 从COS加载模型失败: {str(e)}")
        raise Exception(f"无法加载模型 {model_name}: {str(e)}")


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
        return {}


def clear_cache():
    """清除所有缓存"""
    global _cache

    _cache['lottery_data'] = None
    _cache['lottery_data_timestamp'] = None
    _cache['models'].clear()

    print("🗑️  缓存已清除")


def get_cache_status() -> Dict[str, Any]:
    """获取缓存状态"""
    global _cache

    status = {
        'lottery_data_cached': _cache['lottery_data'] is not None,
        'models_cached': list(_cache['models'].keys()),
        'cache_ttl': _cache['cache_ttl']
    }

    if _cache['lottery_data_timestamp']:
        cache_age = (datetime.now() - _cache['lottery_data_timestamp']).total_seconds()
        status['lottery_data_cache_age'] = cache_age

    return status


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("测试从COS加载数据")
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

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
