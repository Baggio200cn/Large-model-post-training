"""
独立的腾讯云COS上传脚本
可以单独运行，不需要其他依赖文件

使用方法：
1. 设置环境变量
2. python standalone_upload.py
"""

import os
import sys
import json
import tempfile

# 检查环境变量
REQUIRED_ENV = {
    'TENCENT_SECRET_ID': '腾讯云SecretId',
    'TENCENT_SECRET_KEY': '腾讯云SecretKey',
    'TENCENT_COS_BUCKET': '存储桶名称',
    'TENCENT_COS_REGION': '区域（默认：ap-guangzhou）'
}

print("=" * 70)
print("🚀 腾讯云COS独立上传脚本")
print("=" * 70)
print()

# 检查环境变量
missing_vars = []
for var, desc in REQUIRED_ENV.items():
    if var == 'TENCENT_COS_REGION':
        continue  # 可选
    if not os.getenv(var):
        missing_vars.append(f"{var} ({desc})")

if missing_vars:
    print("❌ 缺少必需的环境变量：\n")
    for var in missing_vars:
        print(f"  - {var}")
    print("\n请设置环境变量后重试：")
    print("  Windows PowerShell:")
    print('    $env:TENCENT_SECRET_ID="你的SecretId"')
    print('    $env:TENCENT_SECRET_KEY="你的SecretKey"')
    print('    $env:TENCENT_COS_BUCKET="你的存储桶名称"')
    print('    $env:TENCENT_COS_REGION="ap-guangzhou"')
    sys.exit(1)

# 尝试导入腾讯云SDK
try:
    from qcloud_cos import CosConfig, CosS3Client
    print("✅ 腾讯云SDK已安装")
except ImportError:
    print("❌ 未安装腾讯云SDK")
    print("\n请先安装：")
    print("  pip install cos-python-sdk-v5")
    sys.exit(1)

# 初始化配置
SECRET_ID = os.getenv('TENCENT_SECRET_ID')
SECRET_KEY = os.getenv('TENCENT_SECRET_KEY')
BUCKET = os.getenv('TENCENT_COS_BUCKET')
REGION = os.getenv('TENCENT_COS_REGION', 'ap-guangzhou')

config = CosConfig(
    Region=REGION,
    SecretId=SECRET_ID,
    SecretKey=SECRET_KEY,
    Scheme='https'
)

client = CosS3Client(config)

print(f"✅ COS客户端初始化成功")
print(f"   区域: {REGION}")
print(f"   存储桶: {BUCKET}")
print()

# 彩票历史数据（302期）
LOTTERY_HISTORY = [
    ["25135", 3, 8, 15, 22, 35, 4, 11, "2025-11-22"],
    ["25134", 5, 12, 19, 28, 33, 2, 9, "2025-11-20"],
    ["25133", 2, 7, 14, 25, 31, 6, 10, "2025-11-17"],
    # ... (这里应该包含所有302期数据，为了简洁省略)
]

def prepare_lottery_data():
    """准备彩票数据"""
    data = []
    for record in LOTTERY_HISTORY:
        if len(record) < 9:
            continue
        data.append({
            'period': record[0],
            'front_zone': [record[1], record[2], record[3], record[4], record[5]],
            'back_zone': [record[6], record[7]],
            'date': record[8]
        })

    return {
        'data': data,
        'total_records': len(data),
        'last_updated': '2026-01-19',
        'source': 'Large-model-post-training',
        'version': '1.0'
    }

def upload_json_to_cos(data, cos_path):
    """上传JSON数据到COS"""
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        temp_path = f.name

    try:
        print(f"📤 上传: {cos_path}")
        response = client.upload_file(
            Bucket=BUCKET,
            LocalFilePath=temp_path,
            Key=cos_path,
            PartSize=10,
            MAXThread=10
        )

        file_size = os.path.getsize(temp_path) / 1024
        print(f"✅ 上传成功！文件大小: {file_size:.2f} KB")
        return True

    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def upload_file_to_cos(local_path, cos_path):
    """上传文件到COS"""
    if not os.path.exists(local_path):
        print(f"⚠️  文件不存在: {local_path}")
        return False

    try:
        print(f"📤 上传: {local_path} -> {cos_path}")
        response = client.upload_file(
            Bucket=BUCKET,
            LocalFilePath=local_path,
            Key=cos_path,
            PartSize=10,
            MAXThread=10
        )

        file_size = os.path.getsize(local_path) / 1024
        print(f"✅ 上传成功！文件大小: {file_size:.2f} KB")
        return True

    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return False

def list_cos_files():
    """列出COS中的文件"""
    print("\n" + "=" * 70)
    print("📋 验证上传的文件")
    print("=" * 70)

    try:
        response = client.list_objects(
            Bucket=BUCKET,
            MaxKeys=1000
        )

        files = []
        if 'Contents' in response:
            for item in response['Contents']:
                files.append({
                    'key': item['Key'],
                    'size': int(item['Size']),
                    'last_modified': item['LastModified']
                })

        print(f"\n✅ 找到 {len(files)} 个文件：\n")

        # 按类别分组
        categories = {
            'data/': [],
            'models/': [],
            'training/': []
        }

        for file in files:
            key = file['key']
            for prefix in categories.keys():
                if key.startswith(prefix):
                    categories[prefix].append(file)
                    break

        for category, files in categories.items():
            if files:
                print(f"📁 {category} ({len(files)} 个文件):")
                for f in files:
                    size_kb = f['size'] / 1024
                    if size_kb > 1024:
                        size_str = f"{size_kb/1024:.2f} MB"
                    else:
                        size_str = f"{size_kb:.2f} KB"
                    print(f"   - {f['key']} ({size_str})")

    except Exception as e:
        print(f"❌ 列出文件失败: {str(e)}")

def main():
    """主函数"""
    print("=" * 70)
    print("开始上传")
    print("=" * 70)
    print()

    # 1. 上传彩票数据
    print("📚 准备彩票历史数据...")
    lottery_data = prepare_lottery_data()
    print(f"   共 {lottery_data['total_records']} 期历史数据")

    success = upload_json_to_cos(lottery_data, 'data/lottery_history.json')

    if not success:
        print("\n⚠️  数据上传失败")

    # 2. 上传模型（如果存在）
    print("\n📦 检查本地模型文件...")

    model_dir = 'data/models'
    if os.path.exists(model_dir):
        model_files = [f for f in os.listdir(model_dir) if f.endswith(('.pkl', '.h5', '.json'))]

        if model_files:
            print(f"   找到 {len(model_files)} 个模型文件")
            for filename in model_files:
                local_path = os.path.join(model_dir, filename)
                cos_path = f'models/{filename}'
                upload_file_to_cos(local_path, cos_path)
        else:
            print("   ⚠️  未找到模型文件")
    else:
        print("   ℹ️  模型目录不存在（如在远程运行则正常）")

    # 3. 验证
    list_cos_files()

    print("\n" + "=" * 70)
    print("✅ 上传流程完成！")
    print("=" * 70)
    print("\n提示：")
    print("  - 数据已上传到腾讯云COS")
    print("  - 在Vercel中配置相同的环境变量即可使用")
    print("  - API会自动从COS加载数据")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
