# -*- coding: utf-8 -*-
"""
数据同步模块
负责将新增数据同步到_lottery_data.py和腾讯云COS
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入COS客户端
try:
    from tencent_cos import get_cos_client
    COS_AVAILABLE = True
except:
    COS_AVAILABLE = False


def update_lottery_data_file(new_records: List[Dict[str, Any]]) -> bool:
    """
    更新_lottery_data.py文件，将新数据添加到LOTTERY_HISTORY

    Args:
        new_records: 新增的记录列表，格式：
            [
                {
                    'period': '25142',
                    'date': '2024-01-25',
                    'front_zone': [2, 3, 9, 14, 29],
                    'back_zone': [2, 4]
                }
            ]

    Returns:
        是否成功
    """
    try:
        data_file = os.path.join(os.path.dirname(__file__), '_lottery_data.py')

        # 读取现有文件
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 找到LOTTERY_HISTORY的位置
        history_start = content.find('LOTTERY_HISTORY = [')

        if history_start == -1:
            print("❌ 无法找到LOTTERY_HISTORY定义")
            return False

        # 找到第一个数据项的位置（在注释后面）
        first_item_start = content.find('["', history_start)

        if first_item_start == -1:
            print("❌ 无法找到数据项位置")
            return False

        # 构建新数据的Python代码
        new_items = []
        for record in new_records:
            period = record['period']
            date = record.get('date', datetime.now().strftime('%Y-%m-%d'))
            front = record['front_zone']
            back = record['back_zone']

            # 格式化为Python列表
            item = f'    ["{period}", {front[0]}, {front[1]}, {front[2]}, {front[3]}, {front[4]}, {back[0]}, {back[1]}, "{date}"]'
            new_items.append(item)

        # 插入新数据到文件开头（最新数据在前）
        new_data_str = ',\n'.join(new_items) + ',\n    '

        # 重构文件内容
        new_content = (
            content[:first_item_start] +
            new_data_str +
            content[first_item_start:]
        )

        # 写回文件
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ 成功更新_lottery_data.py，新增 {len(new_records)} 条记录")
        return True

    except Exception as e:
        print(f"❌ 更新_lottery_data.py失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def upload_to_cos(combined_data: List[Dict[str, Any]]) -> bool:
    """
    上传合并后的数据到腾讯云COS

    Args:
        combined_data: 合并后的完整数据（用户数据 + 固定数据）

    Returns:
        是否成功
    """
    if not COS_AVAILABLE:
        print("⚠️  腾讯云COS模块不可用，跳过上传")
        return False

    try:
        # 检查COS配置
        if not all([
            os.getenv('TENCENT_SECRET_ID'),
            os.getenv('TENCENT_SECRET_KEY'),
            os.getenv('TENCENT_COS_BUCKET')
        ]):
            print("⚠️  腾讯云COS未配置，跳过上传")
            return False

        # 获取COS客户端
        client = get_cos_client()

        # 准备上传数据
        upload_data = {
            'data': combined_data,
            'total_records': len(combined_data),
            'last_updated': datetime.now().isoformat(),
            'source': 'admin-manual-add',
            'version': '1.0'
        }

        # 上传到COS
        print("📤 上传数据到腾讯云COS...")
        result = client.upload_json(upload_data, 'data/lottery_history.json')

        if result['success']:
            print(f"✅ 成功上传到COS: data/lottery_history.json")
            print(f"   数据量: {len(combined_data)} 期")
            return True
        else:
            print(f"❌ COS上传失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ COS上传异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def sync_new_data(new_records: List[Dict[str, Any]], combined_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    同步新数据：更新本地文件并上传到COS

    Args:
        new_records: 新增的记录列表
        combined_data: 合并后的完整数据（包含新记录）

    Returns:
        同步结果
    """
    result = {
        'success': False,
        'file_updated': False,
        'cos_uploaded': False,
        'message': ''
    }

    try:
        # 1. 更新本地_lottery_data.py文件
        print("\n" + "="*60)
        print("📝 步骤1：更新本地数据文件")
        print("="*60)

        file_updated = update_lottery_data_file(new_records)
        result['file_updated'] = file_updated

        # 2. 上传到COS
        print("\n" + "="*60)
        print("☁️  步骤2：上传到腾讯云COS")
        print("="*60)

        cos_uploaded = upload_to_cos(combined_data)
        result['cos_uploaded'] = cos_uploaded

        # 判断整体是否成功
        if file_updated or cos_uploaded:
            result['success'] = True
            result['message'] = '数据同步完成'

            if file_updated and cos_uploaded:
                result['message'] += '（本地文件✅ + COS✅）'
            elif file_updated:
                result['message'] += '（仅本地文件✅，COS未配置）'
            elif cos_uploaded:
                result['message'] += '（仅COS✅，本地文件更新失败）'
        else:
            result['message'] = '数据同步失败'

        print(f"\n{'='*60}")
        print(f"📊 同步结果：{result['message']}")
        print(f"{'='*60}")

        return result

    except Exception as e:
        result['message'] = f'同步异常: {str(e)}'
        print(f"❌ {result['message']}")
        return result


if __name__ == '__main__':
    # 测试代码
    print("="*60)
    print("测试数据同步模块")
    print("="*60)

    # 模拟新增数据
    test_records = [
        {
            'period': '25999',
            'date': '2026-01-25',
            'front_zone': [1, 5, 10, 15, 20],
            'back_zone': [3, 7]
        }
    ]

    # 加载现有数据
    from _lottery_data import lottery_data
    combined = test_records + lottery_data

    # 执行同步
    result = sync_new_data(test_records, combined)

    print(f"\n测试结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
