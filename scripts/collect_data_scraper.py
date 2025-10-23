#!/usr/bin/env python3
"""
数据采集脚本（网页爬虫版）
从彩票网站爬取大乐透历史数据
"""
import requests
import json
import os
import re
from datetime import datetime  
from typing import List, Dict


class LotteryDataScraper:
    """大乐透数据爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.lottery.gov.cn/'
        }
        # 使用公开的彩票数据接口
        self.base_url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
    
    def get_history(self, size: int = 50) -> List[Dict]:
        """
        获取历史数据
        
        Args:
            size: 获取的期数
        """
        params = {
            'gameNo': '85',  # 大乐透游戏编号
            'provinceId': '0',
            'pageSize': str(size),
            'isVerify': '1',
            'pageNo': '1'
        }
        
        try:
            print(f"正在获取最近{size}期历史数据...")
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                results = data.get('value', {}).get('list', [])
                return [self._parse_lottery_data(item) for item in results]
            else:
                print(f"❌ 获取数据失败: {data.get('errorMessage', '未知错误')}")
                return []
                
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            return []
    
    def _parse_lottery_data(self, raw_data: Dict) -> Dict:
        """
        解析原始数据为统一格式
        
        API返回格式示例：
        {
            "lotteryDrawNum": "2025120",
            "lotteryDrawTime": "2025-10-22",
            "lotteryDrawResult": "02 08 11 13 22 + 01 07"
        }
        """
        period = raw_data.get('lotteryDrawNum', '')
        date = raw_data.get('lotteryDrawTime', '')
        draw_result = raw_data.get('lotteryDrawResult', '')
        
        # 解析号码
        try:
            # 分离红球和蓝球
            if '+' in draw_result:
                red_part, blue_part = draw_result.split('+')
                red_balls = sorted([int(n.strip()) for n in red_part.strip().split() if n.strip().isdigit()])
                blue_balls = sorted([int(n.strip()) for n in blue_part.strip().split() if n.strip().isdigit()])
            else:
                # 备用解析方式
                numbers = [int(n.strip()) for n in draw_result.split() if n.strip().isdigit()]
                red_balls = sorted(numbers[:5])
                blue_balls = sorted(numbers[5:7])
        except Exception as e:
            print(f"⚠️ 解析号码失败: {draw_result}, 错误: {e}")
            red_balls = []
            blue_balls = []
        
        return {
            'period': period,
            'date': date,
            'time': f"{date} 20:30:00",  # 大乐透开奖时间
            'red_balls': red_balls,
            'blue_balls': blue_balls,
            'original_code': draw_result.replace(' ', ',')
        }
    
    def save_to_file(self, data: List[Dict], filepath: str):
        """保存数据到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {filepath}")
        print(f"   共 {len(data)} 期数据")
    
    def load_from_file(self, filepath: str) -> List[Dict]:
        """从文件加载数据"""
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载文件失败: {e}")
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
            print("📝 没有现有数据，将获取历史数据")
            new_data = self.get_history(size=50)
            if new_data:
                self.save_to_file(new_data, filepath)
            else:
                print("❌ 无法获取数据")
            return
        
        # 获取新数据
        print(f"📥 检查是否有新数据...")
        new_data = self.get_history(size=max_new)
        
        if not new_data:
            print("❌ 无法获取新数据")
            return
        
        # 检查是否有新数据
        latest_period = existing_data[0]['period']
        newest_period = new_data[0]['period']
        
        if newest_period == latest_period:
            print(f"✅ 数据已是最新（最新期号: {latest_period}）")
            return
        
        # 合并数据（去重）
        existing_periods = {d['period'] for d in existing_data}
        new_items = [d for d in new_data if d['period'] not in existing_periods]
        
        if new_items:
            updated_data = new_items + existing_data
            self.save_to_file(updated_data, filepath)
            print(f"✅ 新增 {len(new_items)} 期数据")
        else:
            print("✅ 无新数据需要添加")


def main():
    """主函数"""
    print("="*50)
    print("🎯 大乐透数据采集工具（爬虫版）")
    print("="*50)
    
    # 创建爬虫
    scraper = LotteryDataScraper()
    
    # 数据文件路径
    data_file = 'data/raw/history.json'
    
    # 更新数据
    scraper.update_data(data_file, max_new=30)
    
    # 显示统计信息
    data = scraper.load_from_file(data_file)
    if data:
        print(f"\n📊 数据统计:")
        print(f"   数据范围: {data[-1]['period']} - {data[0]['period']}")
        print(f"   最新一期: {data[0]['period']} ({data[0]['date']})")
        print(f"   开奖号码: {data[0]['original_code']}")
        print(f"   总期数: {len(data)}")


if __name__ == '__main__':
    main()
