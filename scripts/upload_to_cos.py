"""
上传数据和模型到腾讯云COS
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from datetime import datetime
from api._lottery_data import LOTTERY_HISTORY
from utils.tencent_cos import TencentCOSClient


def prepare_lottery_data():
    """准备彩票历史数据"""
    print("\n📚 准备彩票历史数据...")

    # 转换为标准格式
    data = []
    for record in LOTTERY_HISTORY:
        if len(record) < 9:
            continue

        data.append({
            'period': record[0],
            'front_zone': [record[1], record[2], record[3], record[4], record[5]],
            'back_zone': [record[6], record[7]],
            'date': record[8] if len(record) > 8 else ""
        })

    print(f"   共 {len(data)} 期历史数据")

    return {
        'data': data,
        'total_records': len(data),
        'last_updated': datetime.now().isoformat(),
        'source': 'Large-model-post-training',
        'version': '1.0'
    }


def upload_lottery_data(client: TencentCOSClient):
    """上传彩票数据到COS"""
    print("\n" + "=" * 60)
    print("上传彩票历史数据")
    print("=" * 60)

    lottery_data = prepare_lottery_data()

    # 上传JSON格式
    result = client.upload_json(
        lottery_data,
        'data/lottery_history.json'
    )

    if result['success']:
        print(f"✅ 彩票数据上传成功！")
        print(f"   COS路径: data/lottery_history.json")
        print(f"   数据量: {lottery_data['total_records']} 期")
    else:
        print(f"❌ 上传失败: {result.get('error')}")

    return result


def upload_models(client: TencentCOSClient):
    """上传ML模型到COS"""
    print("\n" + "=" * 60)
    print("上传机器学习模型")
    print("=" * 60)

    models_dir = 'data/models'

    if not os.path.exists(models_dir):
        print(f"⚠️  模型目录不存在: {models_dir}")
        print("   请先运行训练脚本生成模型")
        return False

    # 查找所有模型文件
    model_files = []
    for file in os.listdir(models_dir):
        if file.endswith(('.pkl', '.h5', '.json')):
            model_files.append(file)

    if not model_files:
        print(f"⚠️  未找到模型文件")
        return False

    print(f"\n找到 {len(model_files)} 个模型文件")

    # 上传每个模型
    results = []
    for filename in model_files:
        local_path = os.path.join(models_dir, filename)
        cos_path = f'models/{filename}'

        print(f"\n📤 上传: {filename}")
        result = client.upload_file(local_path, cos_path)
        results.append(result)

        if not result['success']:
            print(f"❌ 上传失败: {result.get('error')}")

    success_count = sum(1 for r in results if r['success'])
    print(f"\n✅ 成功上传 {success_count}/{len(results)} 个模型文件")

    return success_count == len(results)


def upload_training_data(client: TencentCOSClient):
    """上传训练数据到COS"""
    print("\n" + "=" * 60)
    print("上传训练数据")
    print("=" * 60)

    training_dir = 'data/training'

    if not os.path.exists(training_dir):
        print(f"⚠️  训练数据目录不存在: {training_dir}")
        return False

    # 上传训练数据文件
    files_to_upload = [
        'training_data.pkl',
        'metadata.json'
    ]

    results = []
    for filename in files_to_upload:
        local_path = os.path.join(training_dir, filename)

        if not os.path.exists(local_path):
            print(f"⚠️  文件不存在: {filename}")
            continue

        cos_path = f'training/{filename}'
        print(f"\n📤 上传: {filename}")
        result = client.upload_file(local_path, cos_path)
        results.append(result)

    success_count = sum(1 for r in results if r['success'])
    print(f"\n✅ 成功上传 {success_count}/{len(results)} 个训练数据文件")

    return success_count > 0


def verify_uploads(client: TencentCOSClient):
    """验证上传的文件"""
    print("\n" + "=" * 60)
    print("验证上传的文件")
    print("=" * 60)

    # 列出所有文件
    all_files = client.list_files()

    print(f"\n✅ COS存储桶中共有 {len(all_files)} 个文件：\n")

    # 按类别分组
    categories = {
        'data/': [],
        'models/': [],
        'training/': []
    }

    for file in all_files:
        key = file['key']
        for prefix in categories.keys():
            if key.startswith(prefix):
                categories[prefix].append(file)
                break

    # 打印每个类别
    for category, files in categories.items():
        if files:
            print(f"\n📁 {category} ({len(files)} 个文件):")
            for f in files:
                size_kb = f['size'] / 1024
                print(f"   - {f['key']} ({size_kb:.2f} KB)")


def main():
    print("=" * 70)
    print("🚀 上传数据和模型到腾讯云COS")
    print("=" * 70)

    try:
        # 初始化COS客户端
        client = TencentCOSClient()

        # 1. 上传彩票数据
        upload_lottery_data(client)

        # 2. 上传训练数据
        upload_training_data(client)

        # 3. 上传模型
        upload_models(client)

        # 4. 验证上传
        verify_uploads(client)

        print("\n" + "=" * 70)
        print("✅ 所有数据已上传完成！")
        print("=" * 70)

    except ValueError as e:
        print(f"\n❌ 配置错误: {str(e)}")
        print("\n请设置以下环境变量：")
        print("  export TENCENT_SECRET_ID=你的SecretId")
        print("  export TENCENT_SECRET_KEY=你的SecretKey")
        print("  export TENCENT_COS_BUCKET=你的存储桶名称")
        print("  export TENCENT_COS_REGION=ap-guangzhou")

    except Exception as e:
        print(f"\n❌ 上传失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
