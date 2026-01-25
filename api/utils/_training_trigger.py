# -*- coding: utf-8 -*-
"""
训练触发器模块
在后台异步执行ML模型训练任务
"""
import os
import sys
import json
import pickle
import threading
import subprocess
from datetime import datetime
from typing import List, Dict, Any

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)

# 训练状态文件
TRAINING_STATUS_FILE = '/tmp/training_status.json'
TRAINING_LOG_FILE = '/tmp/training_log.txt'


def get_training_status() -> Dict[str, Any]:
    """获取当前训练状态"""
    if os.path.exists(TRAINING_STATUS_FILE):
        try:
            with open(TRAINING_STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    return {
        'status': 'idle',
        'message': '未运行',
        'started_at': None,
        'completed_at': None
    }


def update_training_status(status: str, message: str, **kwargs):
    """更新训练状态"""
    status_data = {
        'status': status,
        'message': message,
        'updated_at': datetime.now().isoformat(),
        **kwargs
    }

    try:
        with open(TRAINING_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  更新状态失败: {str(e)}")


def prepare_training_data_from_combined(combined_data: List[Dict[str, Any]]) -> bool:
    """
    从合并的数据准备训练数据

    Args:
        combined_data: 合并后的完整数据

    Returns:
        是否成功
    """
    try:
        print("📚 准备训练数据...")

        # 确保目录存在
        training_dir = os.path.join(project_root, 'data', 'training')
        os.makedirs(training_dir, exist_ok=True)

        # 转换为训练格式（简化版特征提取）
        X_data = []
        y_front_data = []
        y_back_data = []

        # 使用滑动窗口提取特征（过去10期预测下一期）
        window_size = 10

        for i in range(len(combined_data) - window_size):
            # 提取过去window_size期的数据作为特征
            history_window = combined_data[i:i+window_size]

            # 简单特征：展平所有号码
            features = []
            for record in history_window:
                features.extend(record.get('front_zone', []))
                features.extend(record.get('back_zone', []))

            # 目标：下一期的号码（one-hot编码）
            next_record = combined_data[i + window_size]

            # 前区one-hot（35个号码）
            front_target = [0] * 35
            for num in next_record.get('front_zone', []):
                if 1 <= num <= 35:
                    front_target[num - 1] = 1

            # 后区one-hot（12个号码）
            back_target = [0] * 12
            for num in next_record.get('back_zone', []):
                if 1 <= num <= 12:
                    back_target[num - 1] = 1

            X_data.append(features)
            y_front_data.append(front_target)
            y_back_data.append(back_target)

        # 转换为numpy数组
        import numpy as np
        X = np.array(X_data)
        y_front = np.array(y_front_data)
        y_back = np.array(y_back_data)

        # 划分训练集和测试集（80/20）
        split_idx = int(len(X) * 0.8)

        training_data = {
            'X_train': X[:split_idx],
            'X_test': X[split_idx:],
            'y_front_train': y_front[:split_idx],
            'y_front_test': y_front[split_idx:],
            'y_back_train': y_back[:split_idx],
            'y_back_test': y_back[split_idx:],
            'created_at': datetime.now().isoformat(),
            'total_samples': len(X),
            'train_samples': split_idx,
            'test_samples': len(X) - split_idx
        }

        # 保存训练数据
        training_file = os.path.join(training_dir, 'training_data.pkl')
        with open(training_file, 'wb') as f:
            pickle.dump(training_data, f)

        # 保存元数据
        metadata = {
            'total_samples': training_data['total_samples'],
            'train_samples': training_data['train_samples'],
            'test_samples': training_data['test_samples'],
            'feature_dim': X.shape[1],
            'created_at': training_data['created_at'],
            'data_source': 'combined_user_and_fixed'
        }

        metadata_file = os.path.join(training_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 训练数据准备完成")
        print(f"   总样本数: {training_data['total_samples']}")
        print(f"   训练集: {training_data['train_samples']}")
        print(f"   测试集: {training_data['test_samples']}")

        return True

    except Exception as e:
        print(f"❌ 准备训练数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_training_script() -> bool:
    """
    运行训练脚本

    Returns:
        是否成功
    """
    try:
        print("🎯 开始训练模型...")

        # 训练脚本路径
        script_path = os.path.join(project_root, 'scripts', 'train_models.py')

        if not os.path.exists(script_path):
            print(f"❌ 训练脚本不存在: {script_path}")
            return False

        # 执行训练脚本，输出重定向到日志文件
        with open(TRAINING_LOG_FILE, 'w', encoding='utf-8') as log_file:
            log_file.write(f"训练开始时间: {datetime.now().isoformat()}\n")
            log_file.write("="*60 + "\n\n")

            result = subprocess.run(
                [sys.executable, script_path],
                cwd=project_root,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )

            log_file.write(f"\n\n训练结束时间: {datetime.now().isoformat()}\n")
            log_file.write(f"退出代码: {result.returncode}\n")

        if result.returncode == 0:
            print("✅ 模型训练完成")
            return True
        else:
            print(f"❌ 模型训练失败，退出代码: {result.returncode}")
            print(f"   查看日志: {TRAINING_LOG_FILE}")
            return False

    except Exception as e:
        print(f"❌ 训练脚本执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def upload_models_to_cos() -> bool:
    """
    上传训练好的模型到COS

    Returns:
        是否成功
    """
    try:
        # 检查COS配置
        if not all([
            os.getenv('TENCENT_SECRET_ID'),
            os.getenv('TENCENT_SECRET_KEY'),
            os.getenv('TENCENT_COS_BUCKET')
        ]):
            print("⚠️  腾讯云COS未配置，跳过模型上传")
            return False

        print("📤 上传模型到腾讯云COS...")

        from tencent_cos import get_cos_client

        client = get_cos_client()
        models_dir = os.path.join(project_root, 'data', 'models')

        if not os.path.exists(models_dir):
            print(f"⚠️  模型目录不存在: {models_dir}")
            return False

        # 上传所有模型文件
        model_files = [f for f in os.listdir(models_dir) if f.endswith(('.pkl', '.h5', '.json'))]

        if not model_files:
            print("⚠️  未找到模型文件")
            return False

        success_count = 0
        for filename in model_files:
            local_path = os.path.join(models_dir, filename)
            cos_path = f'models/{filename}'

            result = client.upload_file(local_path, cos_path)
            if result['success']:
                success_count += 1

        print(f"✅ 成功上传 {success_count}/{len(model_files)} 个模型文件")
        return success_count > 0

    except Exception as e:
        print(f"❌ 模型上传失败: {str(e)}")
        return False


def training_task(combined_data: List[Dict[str, Any]]):
    """
    后台训练任务（在独立线程中运行）

    Args:
        combined_data: 合并后的完整数据
    """
    print("\n" + "="*70)
    print("🚀 后台训练任务启动")
    print("="*70)

    update_training_status(
        'running',
        '正在训练模型...',
        started_at=datetime.now().isoformat()
    )

    try:
        # 步骤1：准备训练数据
        print("\n📊 步骤1：准备训练数据")
        if not prepare_training_data_from_combined(combined_data):
            update_training_status('failed', '准备训练数据失败')
            return

        # 步骤2：运行训练脚本
        print("\n🎯 步骤2：训练模型")
        if not run_training_script():
            update_training_status('failed', '模型训练失败')
            return

        # 步骤3：上传模型到COS
        print("\n☁️  步骤3：上传模型到COS")
        upload_models_to_cos()  # 不强制要求成功

        # 完成
        update_training_status(
            'completed',
            '模型训练完成',
            completed_at=datetime.now().isoformat()
        )

        print("\n" + "="*70)
        print("✅ 后台训练任务完成")
        print("="*70)

    except Exception as e:
        error_msg = f'训练任务异常: {str(e)}'
        print(f"\n❌ {error_msg}")
        update_training_status('failed', error_msg)
        import traceback
        traceback.print_exc()


def trigger_training(combined_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    触发后台训练任务

    Args:
        combined_data: 合并后的完整数据

    Returns:
        触发结果
    """
    # 检查是否已有训练任务在运行
    current_status = get_training_status()

    if current_status.get('status') == 'running':
        return {
            'success': False,
            'message': '已有训练任务正在运行',
            'status': current_status
        }

    # 启动后台训练线程
    thread = threading.Thread(
        target=training_task,
        args=(combined_data,),
        daemon=True
    )
    thread.start()

    return {
        'success': True,
        'message': '后台训练任务已启动',
        'status': 'running',
        'log_file': TRAINING_LOG_FILE,
        'status_file': TRAINING_STATUS_FILE
    }


if __name__ == '__main__':
    # 测试代码
    print("="*60)
    print("测试训练触发器")
    print("="*60)

    # 加载测试数据
    from _lottery_data import lottery_data

    # 触发训练
    result = trigger_training(lottery_data)

    print(f"\n触发结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # 等待一会儿查看状态
    import time
    time.sleep(5)

    status = get_training_status()
    print(f"\n当前状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
