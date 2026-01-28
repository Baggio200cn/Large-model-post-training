#!/usr/bin/env python3
"""
更新彩票历史数据脚本
从体彩官网获取最新的大乐透开奖数据
"""
import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_ROOT, 'lottery_data_full.json')


def fetch_from_sporttery(page_size=100):
    """从体彩官网获取数据"""
    url = f'https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize={page_size}&isVerify=1&pageNo=1'

    print(f"🔄 从体彩官网获取数据...")
    print(f"   URL: {url[:80]}...")

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.sporttery.cn/'
        })

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

        if result.get('value', {}).get('list'):
            data_list = []
            for item in result['value']['list']:
                draw_result = item.get('lotteryDrawResult', '').split()
                if len(draw_result) >= 7:
                    data_list.append({
                        'period': item.get('lotteryDrawNum'),
                        'front_zone': [int(x) for x in draw_result[:5]],
                        'back_zone': [int(x) for x in draw_result[5:7]],
                        'date': item.get('lotteryDrawTime', '')[:10],
                        'sales': item.get('totalSaleAmount', ''),
                        'pool': item.get('poolBalanceAfterdraw', '')
                    })

            print(f"✅ 获取成功: {len(data_list)} 期数据")
            return data_list

    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e}")
    except Exception as e:
        print(f"❌ 获取失败: {e}")

    return []


def load_existing_data():
    """加载现有数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = json.load(f)

            if isinstance(content, dict) and 'data' in content:
                return content['data']
            elif isinstance(content, list):
                return content
        except Exception as e:
            print(f"⚠️ 加载现有数据失败: {e}")

    return []


def merge_data(existing, new_data):
    """合并数据，去重"""
    existing_periods = {item.get('period') for item in existing}

    added = 0
    for item in new_data:
        if item['period'] not in existing_periods:
            existing.insert(0, item)
            added += 1

    # 按期号排序（降序）
    existing.sort(key=lambda x: x.get('period', ''), reverse=True)

    return existing, added


def save_data(data):
    """保存数据"""
    content = {
        'data': data,
        'total_records': len(data),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': 'sporttery.cn',
        'version': '2.0'
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print(f"💾 数据已保存: {DATA_FILE}")


def main():
    print("=" * 60)
    print("🎱 大乐透历史数据更新工具")
    print("=" * 60)

    # 加载现有数据
    existing = load_existing_data()
    print(f"\n📊 现有数据: {len(existing)} 期")
    if existing:
        print(f"   最新期号: {existing[0].get('period')}")
        print(f"   最早期号: {existing[-1].get('period')}")

    # 获取新数据
    new_data = fetch_from_sporttery(page_size=100)

    if new_data:
        # 合并数据
        merged, added = merge_data(existing, new_data)

        print(f"\n📈 数据合并结果:")
        print(f"   新增: {added} 期")
        print(f"   总计: {len(merged)} 期")

        if merged:
            print(f"   最新期号: {merged[0].get('period')} ({merged[0].get('date')})")

        # 保存
        save_data(merged)

        print("\n" + "=" * 60)
        print("✅ 数据更新完成！")
        print("=" * 60)

        # 显示最新5期
        print("\n📋 最新5期开奖号码:")
        for item in merged[:5]:
            front = ' '.join(f"{n:02d}" for n in item['front_zone'])
            back = ' '.join(f"{n:02d}" for n in item['back_zone'])
            print(f"   第{item['period']}期: {front} | {back}  ({item['date']})")

    else:
        print("\n❌ 无法获取新数据")
        print("   可能原因:")
        print("   1. 网络连接问题")
        print("   2. 体彩官网API变更")
        print("   3. 被防火墙/代理阻止")

        print("\n💡 您可以手动更新数据:")
        print(f"   1. 访问 https://www.sporttery.cn/")
        print(f"   2. 查找大乐透开奖历史")
        print(f"   3. 手动添加到 {DATA_FILE}")


if __name__ == '__main__':
    main()
