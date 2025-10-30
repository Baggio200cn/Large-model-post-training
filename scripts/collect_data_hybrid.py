#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI彩票分析实验室 - 混合策略数据爬虫
策略1: 使用官方API - 需要密钥
策略2: 直接爬取官网 - 免费但可能失效
策略3: 生成模拟数据 - 兜底方案
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class HybridLotteryScraper:
    """混合策略大乐透数据爬虫"""
    
    def __init__(self):
        self.data_dir = 'data/raw'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
    
    def fetch_data(self, count: int = 100) -> List[Dict]:
        """获取数据 - 尝试多种策略"""
        print(f"🎯 开始获取最近 {count} 期数据...\n")
        
        # 策略1: 爬取福彩官网
        print("🕷️  策略1: 爬取福彩官网")
        data = self._fetch_from_official_site(count)
        if data:
            print(f"✅ 官网爬取成功: {len(data)} 期")
            return data
        print("❌ 官网爬取失败，使用模拟数据\n")
        
        # 策略2: 生成模拟数据
        print("🎲 策略2: 生成模拟数据（用于测试）")
        data = self._generate_sample_data(count)
        print(f"✅ 生成模拟数据: {len(data)} 期")
        return data
    
    def _fetch_from_official_site(self, count: int) -> Optional[List[Dict]]:
        """从官网爬取"""
        try:
            url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
            response = requests.post(
                url,
                json={'name': 'dlt', 'issueCount': count},
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return [self._parse_official_data(item) for item in data]
        except:
            pass
        
        return None
    
    def _generate_sample_data(self, count: int) -> List[Dict]:
        """生成模拟数据"""
        import random
        
        data = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(count):
            period = f"24{i+1:03d}"
            draw_date = base_date + timedelta(days=i*2)
            
            red = sorted(random.sample(range(1, 36), 5))
            blue = sorted(random.sample(range(1, 13), 2))
            
            data.append({
                'period': period,
                'date': draw_date.strftime('%Y-%m-%d'),
                'time': draw_date.strftime('%Y-%m-%d 21:30:00'),
                'red_balls': red,
                'blue_balls': blue,
                'original_code': f"{','.join(map(str, red))}+{'+'.join(map(str, blue))}",
                'source': 'simulated'
            })
        
        return data
    
    def _parse_official_data(self, raw: Dict) -> Dict:
        """解析官网数据"""
        red_str = raw.get('red', '')
        blue_str = raw.get('blue', '')
        
        return {
            'period': raw.get('code', ''),
            'date': raw.get('date', ''),
            'time': raw.get('date', '') + ' 21:30:00',
            'red_balls': sorted([int(n) for n in red_str.split(',') if n]),
            'blue_balls': sorted([int(n) for n in blue_str.split(',') if n]),
            'original_code': f"{red_str}+{blue_str}",
            'source': 'official_site'
        }
    
    def save_data(self, data: List[Dict]):
        """保存数据"""
        if not data:
            print("⚠️  没有数据需要保存")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON
        json_path = os.path.join(self.data_dir, 'history.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON已保存: {json_path}")
        
        # 保存备份
        backup_path = os.path.join(self.data_dir, f'history_{timestamp}.json')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 备份已保存: {backup_path}")
        
        # 保存CSV格式
        self._save_csv(data)
        
        print(f"📊 共保存 {len(data)} 期数据")
    
    def _save_csv(self, data: List[Dict]):
        """保存为CSV格式"""
        try:
            import pandas as pd
            
            rows = []
            for item in data:
                row = {
                    'period': item['period'],
                    'date': item['date'],
                    'front_1': item['red_balls'][0] if len(item['red_balls']) > 0 else None,
                    'front_2': item['red_balls'][1] if len(item['red_balls']) > 1 else None,
                    'front_3': item['red_balls'][2] if len(item['red_balls']) > 2 else None,
                    'front_4': item['red_balls'][3] if len(item['red_balls']) > 3 else None,
                    'front_5': item['red_balls'][4] if len(item['red_balls']) > 4 else None,
                    'back_1': item['blue_balls'][0] if len(item['blue_balls']) > 0 else None,
                    'back_2': item['blue_balls'][1] if len(item['blue_balls']) > 1 else None,
                    'source': item.get('source', 'unknown')
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            csv_path = os.path.join(self.data_dir, 'lottery_history.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"💾 CSV已保存: {csv_path}")
            
        except ImportError:
            print("ℹ️  pandas未安装，跳过CSV保存")
    
    def load_data(self) -> List[Dict]:
        """加载现有数据"""
        json_path = os.path.join(self.data_dir, 'history.json')
        if not os.path.exists(json_path):
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_data(self, max_new: int = 50):
        """增量更新数据"""
        existing = self.load_data()
        
        if not existing:
            print("📝 首次运行，获取历史数据\n")
            new_data = self.fetch_data(count=100)
            self.save_data(new_data)
            self._print_stats(new_data)
            return
        
        print(f"📚 已有 {len(existing)} 期数据")
        print(f"   最新期号: {existing[0]['period']}\n")
        
        fresh_data = self.fetch_data(count=max_new)
        
        if not fresh_data:
            print("❌ 无法获取新数据")
            return
        
        if fresh_data[0]['period'] == existing[0]['period']:
            print(f"✅ 数据已是最新（最新期: {existing[0]['period']}）")
            return
        
        existing_periods = {d['period'] for d in existing}
        new_items = [d for d in fresh_data if d['period'] not in existing_periods]
        
        if new_items:
            updated_data = new_items + existing
            self.save_data(updated_data)
            print(f"\n✅ 新增 {len(new_items)} 期数据")
            self._print_stats(updated_data)
        else:
            print("ℹ️  无新数据")
    
    def _print_stats(self, data: List[Dict]):
        """打印统计信息"""
        if not data:
            return
        
        print("\n" + "="*60)
        print("📊 数据统计")
        print("="*60)
        print(f"总期数: {len(data)}")
        print(f"期号范围: {data[-1]['period']} ~ {data[0]['period']}")
        print(f"日期范围: {data[-1]['date']} ~ {data[0]['date']}")
        print(f"\n最新一期:")
        print(f"  期号: {data[0]['period']}")
        print(f"  日期: {data[0]['date']}")
        print(f"  号码: {data[0]['original_code']}")
        print(f"  来源: {data[0].get('source', 'unknown')}")
        print("="*60 + "\n")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎯 AI彩票分析实验室 - 数据采集工具")
    print("="*60)
    print("⚠️  教育项目 - 仅用于学习数据科学")
    print("="*60 + "\n")
    
    scraper = HybridLotteryScraper()
    scraper.update_data(max_new=50)
    
    print("✅ 数据采集完成！\n")

if __name__ == '__main__':
    main()
```

### 步骤 6: 提交文件

滚动到页面底部，你会看到 "Commit new file" 部分：

1. **Commit message** 输入：
```
   ✨ Add hybrid data scraper with fallback strategies
```

2. **Extended description**（可选）输入：
```
   - 整合多种数据采集策略
   - 官网爬取 + 模拟数据备份
   - 支持CSV和JSON格式输出
```

3. 点击绿色按钮 **`Commit new file`**

---

## ✅ 完成后验证

创建成功后，你会看到文件出现在：
```
https://github.com/Baggio200cn/Large-model-post-training/blob/main/scripts/collect_data_hybrid.py
