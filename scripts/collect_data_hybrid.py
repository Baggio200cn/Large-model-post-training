#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Lottery Analysis Lab - Hybrid Data Scraper
Strategy 1: Official website scraping
Strategy 2: Generate sample data as fallback
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class HybridLotteryScraper:
    """Hybrid lottery data scraper"""
    
    def __init__(self):
        self.data_dir = 'data/raw'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
    
    def fetch_data(self, count: int = 100) -> List[Dict]:
        """Fetch data using multiple strategies"""
        print(f"Starting to fetch {count} periods of data...")
        
        # Strategy 1: Official site
        print("Strategy 1: Official website")
        data = self._fetch_from_official_site(count)
        if data:
            print(f"Success: {len(data)} periods")
            return data
        print("Failed, using sample data")
        
        # Strategy 2: Generate sample data
        print("Strategy 2: Generate sample data")
        data = self._generate_sample_data(count)
        print(f"Generated {len(data)} periods")
        return data
    
    def _fetch_from_official_site(self, count: int) -> Optional[List[Dict]]:
        """Fetch from official site"""
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
        """Generate sample data with correct current dates"""
        import random
        
        data = []
        
        # Use current date and work backwards
        end_date = datetime.now()
        start_date = end_date - timedelta(days=count*3)  # 3 days between draws
        
        # Calculate period numbers for current year
        current_year = datetime.now().year
        year_code = current_year - 2000  # 2025 -> 25
        
        # Estimate current period (approximately 3 draws per week, ~150 per year)
        day_of_year = end_date.timetuple().tm_yday
        estimated_period = int(day_of_year / 2.4)  # roughly 365/150
        base_period = year_code * 1000 + max(1, estimated_period - count + 1)
        
        for i in range(count):
            period = f"{base_period + i:05d}"
            draw_date = start_date + timedelta(days=i*3)
            
            # Generate random numbers
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
        
        # Return with newest first
        return list(reversed(data))
    
    def _parse_official_data(self, raw: Dict) -> Dict:
        """Parse official data"""
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
        """Save data to files with metadata"""
        if not data:
            print("No data to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output with metadata
        output = {
            'updated_at': datetime.now().isoformat(),
            'updated_at_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(data),
            'data_source': data[0].get('source', 'unknown'),
            'latest_period': data[0]['period'],
            'latest_date': data[0]['date'],
            'data': data
        }
        
        # Save JSON with metadata
        json_path = os.path.join(self.data_dir, 'history.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"JSON saved: {json_path}")
        
        # Save backup
        backup_path = os.path.join(self.data_dir, f'history_{timestamp}.json')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Backup saved: {backup_path}")
        
        # Save CSV
        self._save_csv(data)
        
        print(f"Total: {len(data)} periods saved")
    
    def _save_csv(self, data: List[Dict]):
        """Save as CSV"""
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
            print(f"CSV saved: {csv_path}")
            
        except ImportError:
            print("pandas not installed, skipping CSV")
    
    def load_data(self) -> List[Dict]:
        """Load existing data"""
        json_path = os.path.join(self.data_dir, 'history.json')
        if not os.path.exists(json_path):
            return []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # Handle both old format (array) and new format (object with metadata)
                if isinstance(content, list):
                    return content
                elif isinstance(content, dict) and 'data' in content:
                    return content['data']
                else:
                    return []
        except:
            return []
    
    def update_data(self, max_new: int = 50):
        """Update data incrementally"""
        existing = self.load_data()
        
        if not existing:
            print("First run, fetching all data")
            new_data = self.fetch_data(count=100)
            self.save_data(new_data)
            self._print_stats(new_data)
            return
        
        print(f"Existing: {len(existing)} periods")
        print(f"Latest: {existing[0]['period']}")
        
        fresh_data = self.fetch_data(count=max_new)
        
        if not fresh_data:
            print("Failed to fetch new data")
            return
        
        if fresh_data[0]['period'] == existing[0]['period']:
            print(f"Already up to date: {existing[0]['period']}")
            return
        
        existing_periods = {d['period'] for d in existing}
        new_items = [d for d in fresh_data if d['period'] not in existing_periods]
        
        if new_items:
            updated_data = new_items + existing
            self.save_data(updated_data)
            print(f"Added {len(new_items)} new periods")
            self._print_stats(updated_data)
        else:
            print("No new data")
    
    def _print_stats(self, data: List[Dict]):
        """Print statistics"""
        if not data:
            return
        
        print("\n" + "="*60)
        print("Data Statistics")
        print("="*60)
        print(f"Total periods: {len(data)}")
        print(f"Period range: {data[-1]['period']} ~ {data[0]['period']}")
        print(f"Date range: {data[-1]['date']} ~ {data[0]['date']}")
        print(f"\nLatest:")
        print(f"  Period: {data[0]['period']}")
        print(f"  Date: {data[0]['date']}")
        print(f"  Numbers: {data[0]['original_code']}")
        print(f"  Source: {data[0].get('source', 'unknown')}")
        print("="*60 + "\n")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("AI Lottery Analysis Lab - Data Collection")
    print("="*60)
    print("Educational project only\n")
    
    scraper = HybridLotteryScraper()
    scraper.update_data(max_new=50)
    
    print("Complete!\n")

if __name__ == '__main__':
    main()
