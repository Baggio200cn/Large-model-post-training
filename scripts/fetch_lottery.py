#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大乐透开奖数据自动抓取脚本
用于 GitHub Actions 定时任务
"""

import requests
import json
import re
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# 配置
API_SOURCES = [
    # 数据源1: 500彩票网API
    {
        'name': '500彩票网',
        'url': 'https://datachart.500.com/dlt/history/newinc/history.php?limit=10',
        'parser': 'parse_500_response'
    },
    # 数据源2: 备用源
    {
        'name': '彩票API',
        'url': 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice',
        'parser': 'parse_cwl_response'
    }
]

# 当前数据文件路径
LATEST_RESULTS_FILE = 'api/latest-results.py'
DATA_ANALYSIS_FILE = 'api/data-analysis.py'


def fetch_from_500():
    """从500彩票网抓取数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = 'https://datachart.500.com/dlt/history/newinc/history.php?limit=10'
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 解析表格数据
            rows = soup.find_all('tr', class_='t_tr1')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 8:
                    period = cells[0].get_text(strip=True)
                    # 获取前区和后区号码
                    front = [int(cells[i].get_text(strip=True)) for i in range(1, 6)]
                    back = [int(cells[i].get_text(strip=True)) for i in range(6, 8)]
                    
                    results.append({
                        'period': period,
                        'date': get_draw_date_by_period(period),
                        'numbers': front + back
                    })
            
            return results if results else None
    except Exception as e:
        print(f"从500彩票网抓取失败: {e}")
        return None


def fetch_from_api():
    """从备用API抓取数据"""
    try:
        # 这是一个示例，实际需要根据可用的API调整
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 使用开彩网API
        url = 'https://www.opencai.net/api/dlt/?num=10'
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                results = []
                for item in data.get('data', []):
                    numbers = [int(n) for n in item.get('opencode', '').replace('+', ',').split(',')]
                    if len(numbers) == 7:
                        results.append({
                            'period': item.get('expect'),
                            'date': item.get('opentime', '').split(' ')[0],
                            'numbers': numbers
                        })
                return results if results else None
    except Exception as e:
        print(f"从备用API抓取失败: {e}")
        return None


def get_draw_date_by_period(period):
    """根据期号推算开奖日期"""
    # 大乐透期号格式：YYNNN，如 25137 表示2025年第137期
    try:
        year = 2000 + int(period[:2])
        period_num = int(period[2:])
        
        # 大乐透每周开奖3次（周一、周三、周六）
        # 一年大约156期
        base_date = datetime(year, 1, 1)
        
        # 找到第一个开奖日（最近的周一、周三或周六）
        while base_date.weekday() not in [0, 2, 5]:  # 0=周一, 2=周三, 5=周六
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


def read_current_data():
    """读取当前数据文件中的期号列表"""
    try:
        with open(LATEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取所有期号
        periods = re.findall(r'"period":\s*"(\d+)"', content)
        return set(periods)
    except Exception as e:
        print(f"读取当前数据失败: {e}")
        return set()


def update_latest_results_file(new_data):
    """更新 latest-results.py 文件"""
    try:
        with open(LATEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到 LOTTERY_DATA 数组的位置
        match = re.search(r'(LOTTERY_DATA\s*=\s*\[)', content)
        if not match:
            print("找不到 LOTTERY_DATA 数组")
            return False
        
        # 生成新数据的代码
        new_entries = []
        for item in new_data:
            entry = f'    {{"period": "{item["period"]}", "date": "{item["date"]}", "numbers": {item["numbers"]}}},'
            new_entries.append(entry)
        
        new_code = '\n'.join(new_entries)
        
        # 插入新数据到数组开头
        insert_pos = match.end()
        updated_content = content[:insert_pos] + '\n' + new_code + content[insert_pos:]
        
        # 更新总期数
        current_count = len(re.findall(r'"period":', content))
        new_count = current_count + len(new_data)
        
        # 更新 total_periods
        updated_content = re.sub(
            r"'total_periods':\s*\d+",
            f"'total_periods': {new_count}",
            updated_content
        )
        
        # 更新 data_range
        all_periods = re.findall(r'"period":\s*"(\d+)"', updated_content)
        if all_periods:
            min_period = min(all_periods)
            max_period = max(all_periods)
            updated_content = re.sub(
                r"'data_range':\s*'[^']+'",
                f"'data_range': '{min_period} - {max_period}'",
                updated_content
            )
        
        with open(LATEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ 成功更新 {LATEST_RESULTS_FILE}")
        return True
    except Exception as e:
        print(f"更新文件失败: {e}")
        return False


def update_data_analysis_file(new_data):
    """更新 data-analysis.py 文件"""
    try:
        with open(DATA_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到 LOTTERY_DATA 数组的位置
        match = re.search(r'(LOTTERY_DATA\s*=\s*\[)', content)
        if not match:
            print("找不到 data-analysis.py 中的 LOTTERY_DATA 数组")
            return False
        
        # 生成新数据的代码
        new_entries = []
        for item in new_data:
            entry = f'    {{"period": "{item["period"]}", "date": "{item["date"]}", "numbers": {item["numbers"]}}},'
            new_entries.append(entry)
        
        new_code = '\n'.join(new_entries)
        
        # 插入新数据到数组开头
        insert_pos = match.end()
        updated_content = content[:insert_pos] + '\n' + new_code + content[insert_pos:]
        
        # 更新总期数
        current_count = len(re.findall(r'"period":', content))
        new_count = current_count + len(new_data)
        
        # 更新 total_draws
        updated_content = re.sub(
            r"'total_draws':\s*\d+",
            f"'total_draws': {new_count}",
            updated_content
        )
        
        with open(DATA_ANALYSIS_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ 成功更新 {DATA_ANALYSIS_FILE}")
        return True
    except Exception as e:
        print(f"更新 data-analysis.py 失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("🎯 大乐透开奖数据自动更新")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 读取当前已有的期号
    existing_periods = read_current_data()
    print(f"📊 当前已有 {len(existing_periods)} 期数据")
    
    # 从多个源尝试抓取
    fetched_data = None
    
    print("\n🔍 尝试从500彩票网抓取...")
    fetched_data = fetch_from_500()
    
    if not fetched_data:
        print("🔍 尝试从备用API抓取...")
        fetched_data = fetch_from_api()
    
    if not fetched_data:
        print("❌ 所有数据源均无法获取数据")
        return
    
    print(f"✅ 成功获取 {len(fetched_data)} 期数据")
    
    # 筛选出新数据
    new_data = [
        item for item in fetched_data 
        if item['period'] not in existing_periods
    ]
    
    if not new_data:
        print("ℹ️ 没有新的开奖数据需要更新")
        return
    
    print(f"\n📥 发现 {len(new_data)} 期新数据:")
    for item in new_data:
        front = item['numbers'][:5]
        back = item['numbers'][5:]
        print(f"  第{item['period']}期 ({item['date']}): {front} + {back}")
    
    # 更新文件
    print("\n📝 更新数据文件...")
    
    success1 = update_latest_results_file(new_data)
    success2 = update_data_analysis_file(new_data)
    
    if success1 and success2:
        print("\n✅ 数据更新完成！")
    else:
        print("\n⚠️ 部分文件更新失败，请检查")
    
    print("=" * 50)


if __name__ == '__main__':
    main()
