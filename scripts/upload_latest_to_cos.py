#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传最新开奖数据到腾讯云COS
用于GitHub Actions自动更新
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from datetime import datetime


def read_lottery_data_from_file():
    """从本地Python文件读取彩票数据"""
    try:
        # 导入lottery_data
        from api.utils._lottery_data import lottery_data

        print(f"📚 读取到 {len(lottery_data)} 期历史数据")

        return {
            'data': lottery_data,
            'total_records': len(lottery_data),
            'last_updated': datetime.now().isoformat(),
            'source': 'GitHub-Actions-Auto-Update',
            'version': '2.0'
        }
    except Exception as e:
        print(f"❌ 读取数据失败: {str(e)}")
        return None


def upload_to_cos(data_dict):
    """上传数据到腾讯云COS"""
    try:
        from qcloud_cos import CosConfig, CosS3Client
        import json

        # 从环境变量获取配置
        secret_id = os.getenv('TENCENT_SECRET_ID')
        secret_key = os.getenv('TENCENT_SECRET_KEY')
        bucket = os.getenv('TENCENT_COS_BUCKET')
        region = os.getenv('TENCENT_COS_REGION', 'ap-guangzhou')

        if not all([secret_id, secret_key, bucket]):
            print("❌ 缺少必要的环境变量配置")
            print("   需要: TENCENT_SECRET_ID, TENCENT_SECRET_KEY, TENCENT_COS_BUCKET")
            return False

        print(f"\n🔐 COS配置:")
        print(f"   存储桶: {bucket}")
        print(f"   地域: {region}")

        # 初始化COS客户端
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key
        )
        client = CosS3Client(config)

        # 转换为JSON
        json_data = json.dumps(data_dict, ensure_ascii=False, indent=2)

        # 上传到COS
        cos_key = 'data/lottery_history.json'

        print(f"\n📤 上传数据到COS...")
        print(f"   目标路径: {cos_key}")
        print(f"   数据大小: {len(json_data) / 1024:.2f} KB")

        response = client.put_object(
            Bucket=bucket,
            Body=json_data.encode('utf-8'),
            Key=cos_key,
            ContentType='application/json'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"\n✅ 数据上传成功！")
            print(f"   ETag: {response.get('ETag', 'N/A')}")
            return True
        else:
            print(f"❌ 上传失败: HTTP {response['ResponseMetadata']['HTTPStatusCode']}")
            return False

    except Exception as e:
        print(f"\n❌ 上传过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 自动上传开奖数据到腾讯云COS")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 读取数据
    data_dict = read_lottery_data_from_file()

    if not data_dict:
        print("\n❌ 无法读取数据，退出")
        sys.exit(1)

    print(f"\n📊 数据统计:")
    print(f"   总期数: {data_dict['total_records']}")
    if data_dict['data']:
        latest = data_dict['data'][0]
        print(f"   最新期号: {latest.get('period', 'N/A')}")
        print(f"   开奖日期: {latest.get('date', 'N/A')}")

    # 上传到COS
    success = upload_to_cos(data_dict)

    if success:
        print("\n" + "=" * 70)
        print("✅ 自动更新完成！")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ 上传失败")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()
