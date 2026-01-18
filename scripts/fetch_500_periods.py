#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展大乐透历史数据到500期
用于提升模型训练效果
"""

import requests
import json
import re
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def fetch_large_dataset_from_500(limit=500):
    """从500彩票网抓取大量历史数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://datachart.500.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        # 500彩票网支持通过limit参数获取更多历史数据
        url = f'https://datachart.500.com/dlt/history/newinc/history.php?limit={limit}'

        print(f"🔍 正在从500彩票网抓取 {limit} 期历史数据...")
        print(f"URL: {url}")

        response = requests.get(url, headers=headers, timeout=60)
        response.encoding = 'gb2312'  # 500彩票网使用gb2312编码

        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # 查找开奖数据表格
        table = soup.find('tbody', {'id': 'tdata'})
        if not table:
            print("❌ 未找到数据表格")
            return None

        rows = table.find_all('tr')
        print(f"✅ 找到 {len(rows)} 行数据")

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 8:
                continue

            try:
                # 解析期号
                period = cells[0].get_text(strip=True)

                # 解析开奖日期
                date_text = cells[13].get_text(strip=True) if len(cells) > 13 else ""

                # 解析前区号码（5个）
                front_numbers = []
                for i in range(1, 6):
                    num_text = cells[i].get_text(strip=True)
                    if num_text.isdigit():
                        front_numbers.append(int(num_text))

                # 解析后区号码（2个）
                back_numbers = []
                for i in range(6, 8):
                    num_text = cells[i].get_text(strip=True)
                    if num_text.isdigit():
                        back_numbers.append(int(num_text))

                # 验证数据完整性
                if len(front_numbers) == 5 and len(back_numbers) == 2:
                    results.append({
                        'period': period,
                        'date': date_text if date_text else calculate_date_from_period(period),
                        'front': front_numbers,
                        'back': back_numbers
                    })
            except Exception as e:
                print(f"⚠️ 解析行数据失败: {e}")
                continue

        print(f"✅ 成功解析 {len(results)} 期有效数据")
        return results

    except Exception as e:
        print(f"❌ 抓取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def fetch_from_opencai(page=1, page_size=100):
    """从开彩网API抓取数据（支持分页）"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        url = f'https://www.opencai.net/api/dlt/?num={page_size}&page={page}'

        print(f"🔍 从开彩网抓取第 {page} 页数据（每页 {page_size} 条）...")

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                results = []
                for item in data.get('data', []):
                    # 解析开奖号码，格式如 "01,05,12,23,35+03,11"
                    opencode = item.get('opencode', '')
                    if '+' in opencode:
                        parts = opencode.split('+')
                        front = [int(n) for n in parts[0].split(',')]
                        back = [int(n) for n in parts[1].split(',')]

                        if len(front) == 5 and len(back) == 2:
                            results.append({
                                'period': item.get('expect'),
                                'date': item.get('opentime', '').split(' ')[0],
                                'front': front,
                                'back': back
                            })

                print(f"✅ 获取 {len(results)} 期数据")
                return results

        return None
    except Exception as e:
        print(f"❌ 从开彩网抓取失败: {e}")
        return None


def fetch_500_periods_multi_source():
    """从多个数据源获取500期数据"""
    all_data = []

    # 方法1: 尝试从500彩票网一次性获取500期
    print("\n" + "="*60)
    print("方法1: 从500彩票网获取大量历史数据")
    print("="*60)

    data_500 = fetch_large_dataset_from_500(limit=500)
    if data_500 and len(data_500) >= 400:
        print(f"✅ 成功从500彩票网获取 {len(data_500)} 期数据")
        all_data.extend(data_500)

    # 方法2: 如果数据不足，从开彩网API分页获取
    if len(all_data) < 500:
        print("\n" + "="*60)
        print("方法2: 从开彩网API分页获取补充数据")
        print("="*60)

        target = 500 - len(all_data)
        page = 1
        page_size = 100

        while len(all_data) < 500 and page <= 5:
            data_opencai = fetch_from_opencai(page=page, page_size=page_size)
            if data_opencai:
                # 去重
                existing_periods = {item['period'] for item in all_data}
                new_data = [item for item in data_opencai if item['period'] not in existing_periods]
                all_data.extend(new_data)
                print(f"累计获取 {len(all_data)} 期数据")

            page += 1
            time.sleep(1)  # 避免请求过快

    return all_data


def calculate_date_from_period(period):
    """根据期号计算开奖日期"""
    try:
        year = 2000 + int(period[:2])
        period_num = int(period[2:])

        # 大乐透每周开奖3次（周一、周三、周六）
        base_date = datetime(year, 1, 1)

        # 找到第一个开奖日
        while base_date.weekday() not in [0, 2, 5]:
            base_date += timedelta(days=1)

        # 计算第N期的日期
        draws = 0
        current_date = base_date
        while draws < period_num - 1:
            current_date += timedelta(days=1)
            if current_date.weekday() in [0, 2, 5]:
                draws += 1

        return current_date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def generate_lottery_data_code(data):
    """生成Python代码格式的数据"""
    lines = ['# -*- coding: utf-8 -*-']
    lines.append('"""')
    lines.append('大乐透历史开奖数据模块（扩展到500期）')
    lines.append('包含500期真实历史数据，供ML模型训练使用')
    lines.append('"""')
    lines.append('')
    lines.append('# 历史开奖数据格式: [期号, 前区1-5, 后区1-2, 开奖日期]')
    lines.append('# 数据来源: 中国体彩官网 + 500彩票网')
    lines.append('LOTTERY_HISTORY = [')

    # 按期号排序（从新到旧）
    sorted_data = sorted(data, key=lambda x: x['period'], reverse=True)

    for item in sorted_data:
        period = item['period']
        date = item['date']
        front = item['front']
        back = item['back']

        # 格式化为: ["25135", 3, 8, 15, 22, 35, 4, 11, "2025-11-22"],
        line = f'    ["{period}", {", ".join(map(str, front))}, {", ".join(map(str, back))}, "{date}"],'
        lines.append(line)

    lines.append(']')
    lines.append('')
    lines.append(f'# 数据统计')
    lines.append(f'TOTAL_PERIODS = {len(data)}')
    lines.append(f'DATE_RANGE = "{sorted_data[-1]["date"]} 至 {sorted_data[0]["date"]}"')
    lines.append(f'PERIOD_RANGE = "{sorted_data[-1]["period"]} - {sorted_data[0]["period"]}"')

    return '\n'.join(lines)


def main():
    """主函数"""
    print("\n" + "🎯 " + "="*58)
    print("  大乐透历史数据扩展工具 - 目标500期")
    print("="*60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 获取500期数据
    data = fetch_500_periods_multi_source()

    if not data:
        print("\n❌ 无法获取数据，请检查网络连接或数据源")
        return

    print(f"\n✅ 总计获取 {len(data)} 期历史数据")

    if len(data) < 500:
        print(f"⚠️ 数据量不足500期，实际获取 {len(data)} 期")
        print("这可能是因为数据源限制或网络问题")

    # 数据验证
    print("\n" + "="*60)
    print("📊 数据验证")
    print("="*60)

    periods = [item['period'] for item in data]
    print(f"期号范围: {min(periods)} - {max(periods)}")
    print(f"最早日期: {min(item['date'] for item in data)}")
    print(f"最晚日期: {max(item['date'] for item in data)}")

    # 检查数据完整性
    invalid_count = 0
    for item in data:
        if len(item['front']) != 5 or len(item['back']) != 2:
            invalid_count += 1

    if invalid_count > 0:
        print(f"⚠️ 发现 {invalid_count} 期数据不完整")
    else:
        print("✅ 所有数据格式验证通过")

    # 生成代码
    print("\n" + "="*60)
    print("📝 生成数据文件")
    print("="*60)

    code = generate_lottery_data_code(data)

    # 保存到文件
    output_file = 'api/_lottery_data_500.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"✅ 数据已保存到: {output_file}")
    print(f"📦 文件大小: {len(code)} 字节")

    # 显示示例数据
    print("\n" + "="*60)
    print("📋 数据示例（最新5期）")
    print("="*60)

    sorted_data = sorted(data, key=lambda x: x['period'], reverse=True)
    for item in sorted_data[:5]:
        print(f"第{item['period']}期 ({item['date']}): {item['front']} + {item['back']}")

    print("\n✅ 数据扩展完成！")
    print("="*60)


if __name__ == '__main__':
    main()
