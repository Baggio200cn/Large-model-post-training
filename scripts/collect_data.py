"""
数据采集脚本
功能：从API获取大乐透历史数据
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LotteryDataFetcher:
    """大乐透数据获取器"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://www.mxnzp.com/api/lottery/common"
        
    def get_latest(self) -> Dict:
        """获取最新一期数据"""
        url = f"{self.base_url}/latest"
        params = {
            'code': 'cjdlt',  # 大乐透代码
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            print("正在获取最新一期数据...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 1:
                return self._parse_lottery_data(data['data'])
            else:
                raise Exception(f"API返回错误: {data['msg']}")
                
        except Exception as e:
            print(f"❌ 获取最新数据失败: {e}")
            return None
    
    def get_history(self, size: int = 50) -> List[Dict]:
        """
        获取历史数据
        
        Args:
            size: 获取的期数，默认50期（免费API限制）
        """
        url = f"{self.base_url}/history"
        params = {
            'code': 'cjdlt',
            'size': size,
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            print(f"正在获取最近{size}期历史数据...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 1:
                return [self._parse_lottery_data(item) for item in data['data']]
            else:
                raise Exception(f"API返回错误: {data['msg']}")
                
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return []
    
    def _parse_lottery_data(self, raw_data: Dict) -> Dict:
        """
        解析原始数据为统一格式
        
        原始格式示例：
        {
            "openCode": "08,15,27,29,31+01+07",
            "expect": "2025119",
            "name": "超级大乐透",
            "time": "2025-10-20 21:25:00"
        }
        """
        open_code = raw_data['openCode']
        
        # 处理红球和蓝球（蓝球之间也用+分隔）
        parts = open_code.split('+')
        red_str = parts[0]
        blue_str = ','.join(parts[1:])  # 把所有蓝球用逗号连接
        
        return {
            'period': raw_data['expect'],
            'date': raw_data['time'].split(' ')[0],
            'time': raw_data['time'],
            'red_balls': sorted([int(n) for n in red_str.split(',')]),
            'blue_balls': sorted([int(n) for n in blue_str.split(',')]),
            'original_code': open_code
        }
    
    def save_to_file(self, data: List[Dict], filepath: str):
        """保存数据到JSON文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {filepath}")
        print(f"   共 {len(data)} 期数据")
    
    def load_from_file(self, filepath: str) -> List[Dict]:
        """从文件加载数据"""
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_data(self, filepath: str, max_new: int = 10):
        """
        增量更新数据
        
        Args:
            filepath: 数据文件路径
            max_new: 最多获取多少期新数据
        """
        # 加载现有数据
        existing_data = self.load_from_file(filepath)
        
        if not existing_data:
            print("📝 没有现有数据，将获取全部历史数据")
            new_data = self.get_history(size=50)  # 免费API限制50期
            self.save_to_file(new_data, filepath)
            return
        
        # 获取最新一期
        latest = self.get_latest()
        if not latest:
            print("❌ 无法获取最新数据")
            return
        
        # 检查是否有新数据
        latest_period = existing_data[0]['period']
        if latest['period'] == latest_period:
            print(f"✅ 数据已是最新（最新期号: {latest_period}）")
            return
        
        # 获取新数据
        print(f"📥 发现新数据，开始更新...")
        new_data = self.get_history(size=max_new)
        
        # 合并数据（去重）
        existing_periods = {d['period'] for d in existing_data}
        new_items = [d for d in new_data if d['period'] not in existing_periods]
        
        if new_items:
            updated_data = new_items + existing_data
            self.save_to_file(updated_data, filepath)
            print(f"✅ 新增 {len(new_items)} 期数据")
        else:
            print("✅ 无新数据")


def main():
    """主函数"""
    print("="*50)
    print("🎯 大乐透数据采集工具")
    print("="*50)
    
    # 从环境变量读取API密钥
    app_id = os.getenv('LOTTERY_APP_ID')
    app_secret = os.getenv('LOTTERY_APP_SECRET')
    
    if not app_id or not app_secret:
        print("\n❌ 错误：请设置环境变量")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 在 .env 中填入你的 API 密钥")
        print("   3. 从 https://www.mxnzp.com 获取密钥")
        return
    
    # 创建数据获取器
    fetcher = LotteryDataFetcher(app_id, app_secret)
    
    # 数据文件路径
    data_file = 'data/raw/history.json'
    
    # 更新数据
    fetcher.update_data(data_file, max_new=20)
    
    # 显示统计信息
    data = fetcher.load_from_file(data_file)
    if data:
        print(f"\n📊 数据统计:")
        print(f"   数据范围: {data[-1]['period']} - {data[0]['period']}")
        print(f"   最新一期: {data[0]['period']} ({data[0]['date']})")
        print(f"   开奖号码: {data[0]['original_code']}")
        print(f"   总期数: {len(data)}")


if __name__ == '__main__':
    main()