#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI彩票分析实验室 - 大乐透数据采集脚本
版本: 3.0 - 严格模式（只使用真实数据）
作者: Baggio200cn
更新: 2025-10-31
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional


class LotteryDataCollector:
    """大乐透数据采集器 - 严格模式"""
    
    def __init__(self):
        self.data_dir = 'data/raw'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        print("✅ 数据采集器初始化完成（严格模式）\n")
    
    def fetch_real_data(self, count: int = 100) -> Optional[List[Dict]]:
        """
        从官方API获取真实数据
        
        Args:
            count: 要获取的期数
            
        Returns:
            数据列表，失败返回None
        """
        print(f"📡 正在从官方API获取最近 {count} 期数据...")
        print(f"   API地址: http://www.cwl.gov.cn/...")
        
        try:
            url = 'http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice'
            
            params = {
                'name': 'dlt',
                'issueCount': str(count),
                'issueStart': '',
                'issueEnd': '',
            }
            
            print(f"   发送请求...")
            
            response = requests.post(
                url,
                json=params,
                headers=self.headers,
                timeout=30
            )
            
            print(f"   收到响应: HTTP {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API返回错误: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get('state') == 0 and 'result' in data:
                print(f"   解析数据...")
                parsed_data = self._parse_official_data(data['result'])
                
                if parsed_data:
                    print(f"\n✅ 成功获取 {len(parsed_data)} 期真实数据")
                    self._validate_data_quality(parsed_data[:5])
                    return parsed_data
                else:
                    print("❌ 解析数据失败")
                    return None
            else:
                error_msg = data.get('errorMessage', '未知错误')
                print(f"❌ API返回格式错误: {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ API请求超时（30秒）")
            print("   可能原因：网络连接慢或服务器响应慢")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接失败")
            print("   可能原因：无网络连接或DNS解析失败")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return None
        except json.JSONDecodeError:
            print("❌ API返回的不是有效的JSON格式")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_official_data(self, raw_data: List[Dict]) -> List[Dict]:
        """解析官方API返回的数据"""
        parsed = []
        errors = []
        
        for item in raw_data:
            try:
                # 解析红球
                red_str = item.get('red', '')
                if not red_str:
                    errors.append(f"期号 {item.get('code', 'N/A')} 缺少红球数据")
                    continue
                    
                red_balls = [int(x.strip()) for x in red_str.split(',') if x.strip()]
                
                # 解析蓝球
                blue_str = item.get('blue', '')
                if not blue_str:
                    errors.append(f"期号 {item.get('code', 'N/A')} 缺少蓝球数据")
                    continue
                    
                blue_balls = [int(x.strip()) for x in blue_str.split(',') if x.strip()]
                
                # 验证数据
                if len(red_balls) != 5:
                    errors.append(f"期号 {item.get('code', 'N/A')} 红球数量不正确: {len(red_balls)}")
                    continue
                
                if len(blue_balls) != 2:
                    errors.append(f"期号 {item.get('code', 'N/A')} 蓝球数量不正确: {len(blue_balls)}")
                    continue
                
                if not all(1 <= n <= 35 for n in red_balls):
                    errors.append(f"期号 {item.get('code', 'N/A')} 红球号码超出范围")
                    continue
                    
                if not all(1 <= n <= 12 for n in blue_balls):
                    errors.append(f"期号 {item.get('code', 'N/A')} 蓝球号码超出范围")
                    continue
                
                parsed.append({
                    'period': item.get('code', ''),
                    'date': item.get('date', ''),
                    'red_balls': sorted(red_balls),
                    'blue_balls': sorted(blue_balls)
                })
                
            except Exception as e:
                errors.append(f"处理数据失败: {e}")
                continue
        
        # 打印错误信息（如果有）
        if errors:
            print(f"\n⚠️  解析过程中发现 {len(errors)} 个问题:")
            for error in errors[:5]:  # 只显示前5个
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... 还有 {len(errors) - 5} 个问题")
        
        return parsed
    
    def _validate_data_quality(self, sample_data: List[Dict]):
        """验证数据质量"""
        print("\n📊 数据质量验证（前5期）:")
        print("-" * 80)
        
        for i, record in enumerate(sample_data, 1):
            period = record.get('period', 'N/A')
            date_str = record.get('date', 'N/A')
            red_balls = record.get('red_balls', [])
            blue_balls = record.get('blue_balls', [])
            
            # 验证日期
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                weekday_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][weekday]
                is_valid_day = weekday in [0, 2, 5]
                day_check = '✅' if is_valid_day else '❌'
            except:
                weekday_name = '无效'
                day_check = '❌'
            
            print(f"第{i}期: {period} | {date_str} ({weekday_name}) {day_check}")
            print(f"      红球: {red_balls} | 蓝球: {blue_balls}")
    
    def save_data(self, data: List[Dict], filename: str = 'history.json'):
        """保存数据到文件"""
        filepath = os.path.join(self.data_dir, filename)
        
        save_data = {
            'updated_at': datetime.now().isoformat(),
            'updated_at_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(data),
            'data_source': 'official_api',  # 明确标注：真实数据
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据已保存: {filepath}")
        print(f"✅ 共保存 {len(data)} 期真实数据")
        
        if data:
            latest = data[0]
            print(f"\n📊 最新一期:")
            print(f"   期号: {latest['period']}")
            print(f"   日期: {latest['date']}")
            print(f"   红球: {latest['red_balls']}")
            print(f"   蓝球: {latest['blue_balls']}")


def main():
    """主函数 - 严格模式：只使用真实数据"""
    print("=" * 80)
    print("🎯 大乐透数据采集工具 v3.0 - 严格模式")
    print("=" * 80)
    print("📌 策略: 只接受真实数据，不生成模拟数据")
    print("📌 来源: 中国福利彩票官方API")
    print()
    
    try:
        collector = LotteryDataCollector()
        
        # 只尝试获取真实数据
        data = collector.fetch_real_data(count=100)
        
        # 如果失败，直接退出
        if not data or len(data) == 0:
            print("\n" + "=" * 80)
            print("❌ 数据采集失败")
            print("=" * 80)
            print("\n可能的原因:")
            print("  1. 网络连接问题")
            print("  2. 官方API服务不可用")
            print("  3. API接口发生变更")
            print("  4. 请求被拒绝或限流")
            print("\n建议:")
            print("  - 检查网络连接")
            print("  - 稍后重试")
            print("  - 查看完整错误日志")
            print("\n⚠️  注意: 本程序采用严格模式，不会生成模拟数据")
            return 1
        
        # 保存真实数据
        collector.save_data(data)
        
        print("\n" + "=" * 80)
        print("🎉 数据采集成功！")
        print("=" * 80)
        print("\n✅ 采集了 100% 真实的官方数据")
        print("✅ 数据将自动提交到 GitHub")
        print("✅ Vercel 将自动部署到网站")
        print("\n💡 提示: 网站只显示真实开奖数据，绝无模拟")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
