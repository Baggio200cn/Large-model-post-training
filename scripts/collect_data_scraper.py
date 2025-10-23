#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大乐透历史数据采集脚本（网页爬虫版）
从官方网站直接获取开奖数据
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class LotteryDataScraper:
    """大乐透数据爬虫类"""
    
    def __init__(self):
        self.base_url = "https://www.lottery.gov.cn"
        self.history_url = f"{self.base_url}/dlt/dltHistoryData.jhtml"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def get_history(self, size: int = 30) -> List[Dict]:
        """
        获取历史开奖数据
        
        Args:
            size: 获取的期数
            
        Returns:
            开奖数据列表
        """
        try:
            print(f"正在获取最近 {size} 期数据...")
            
            response = requests.get(
                self.history_url,
                headers=self.headers,
                params={'size': size},
                timeout=10
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析数据表格
            data_list = []
            rows = soup.select('table.lottery-table tr')[1:]  # 跳过表头
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 8:
                    period = cols[0].text.strip()
                    date = cols[1].text.strip()
                    
                    # 前区号码
                    front_nums = [cols[i].text.strip() for i in range(2, 7)]
                    # 后区号码
                    back_nums = [cols[i].text.strip() for i in range(7, 9)]
                    
                    data_list.append({
                        'period': period,
                        'date': date,
                        'front_code': front_nums,
                        'back_code': back_nums,
                        'original_code': f"{' '.join(front_nums)} + {' '.join(back_nums)}"
                    })
            
            print(f"成功获取 {len(data_list)} 期数据")
            return data_list
            
        except requests.RequestException as e:
            print(f"网络请求失败: {e}")
            return []
        except Exception as e:
            print(f"数据解析失败: {e}")
            return []
    
    def save_to_file(self, data: List[Dict], filepath: str):
        """保存数据到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filepath}")
        print(f"共 {len(data)} 期数据")
    
    def load_from_file(self, filepath: str) -> List[Dict]:
        """从文件加载数据"""
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文件失败: {e}")
            return []
    
    def update_data(self, filepath: str, max_new: int = 30):
        """
        增量更新数据
        
        Args:
            filepath: 数据文件路径
            max_new: 最多获取多少期新数据
        """
        # 加载现有数据
        existing_data = self.load_from_file(filepath)
        
        if not existing_data:
            print("没有现有数据，将获取历史数据")
            new_data = self.get_history(size=50)
            if new_data:
                self.save_to_file(new_data, filepath)
            else:
                print("无法获取数据")
            return
        
        # 获取新数据
        print("检查是否有新数据...")
        new_data = self.get_history(size=max_new)
        
        if not new_data:
            print("无法获取新数据")
            return
        
        # 检查是否有新数据
        latest_period = existing_data[0]['period']
        newest_period = new_data[0]['period']
        
        if newest_period == latest_period:
            print(f"数据已是最新（最新期号: {latest_period}）")
            return
        
        # 合并数据（去重）
        existing_periods = {d['period'] for d in existing_data}
        new_items = [d for d in new_data if d['period'] not in existing_periods]
        
        if new_items:
            updated_data = new_items + existing_data
            self.save_to_file(updated_data, filepath)
            print(f"新增 {len(new_items)} 期数据")
        else:
            print("无新数据需要添加")


def main():
    """主函数"""
    print("=" * 50)
    print("大乐透数据采集工具（爬虫版）")
    print("=" * 50)
    
    # 创建爬虫
    scraper = LotteryDataScraper()
    
    # 数据文件路径
    data_file = 'data/raw/history.json'
    
    # 更新数据
    scraper.update_data(data_file, max_new=30)
    
    # 显示统计信息
    data = scraper.load_from_file(data_file)
    if data:
        print(f"\n数据统计:")
        print(f"数据范围: {data[-1]['period']} - {data[0]['period']}")
        print(f"最新一期: {data[0]['period']} ({data[0]['date']})")
        print(f"开奖号码: {data[0]['original_code']}")
        print(f"总期数: {len(data)}")


if __name__ == '__main__':
    main()
