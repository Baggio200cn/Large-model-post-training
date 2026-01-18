# 📊 大乐透历史数据扩展指南

## 目录
- [为什么需要扩展到500期](#为什么需要扩展到500期)
- [数据获取方法](#数据获取方法)
- [使用自动化脚本](#使用自动化脚本)
- [手动扩展数据](#手动扩展数据)
- [数据验证](#数据验证)

---

## 为什么需要扩展到500期

### 当前状况
- **现有数据量**: 302期（2023年11月 - 2025年11月）
- **时间跨度**: 约2年

### 问题分析
1. **样本量不足**: 对于机器学习模型来说，302期数据相对较少
2. **统计规律有限**: 彩票本质是随机事件，但更多历史数据能提供更稳定的统计特征
3. **过拟合风险**: 少量数据容易导致模型过度拟合特定模式

### 扩展到500期的好处
✅ **更充分的训练数据** - 500期数据约覆盖3-4年时间跨度
✅ **更稳定的统计规律** - 捕捉长期趋势和季节性模式
✅ **更好的泛化能力** - 减少过拟合，提升预测稳定性
✅ **更可靠的特征工程** - 支持更复杂的特征提取和分析

---

## 数据获取方法

### 方法1: 使用自动化脚本（推荐）

项目已提供自动化数据抓取脚本：

```bash
# 运行数据扩展脚本
python scripts/fetch_500_periods.py
```

**脚本功能：**
- 自动从多个数据源抓取历史数据
- 支持500彩票网、开彩网等API
- 自动数据验证和去重
- 生成Python代码格式的数据文件

**数据源：**
1. **500彩票网**: https://datachart.500.com/dlt/
2. **开彩网API**: https://www.opencai.net/api/dlt/
3. **中国体彩官网**: http://www.lottery.gov.cn/

**注意事项：**
- 需要稳定的网络连接
- 某些数据源可能有访问限制
- 建议在非高峰时段运行

---

### 方法2: 手动从官方网站获取

如果自动脚本无法使用，可以手动获取数据。

#### 步骤1: 访问数据源

**推荐网站：**
- 中国体育彩票官网: http://www.lottery.gov.cn/
- 500彩票网: https://datachart.500.com/dlt/
- 彩票走势网: http://www.cwl.gov.cn/

#### 步骤2: 下载历史数据

1. 访问大乐透历史开奖页面
2. 选择数据范围（建议选择近500期）
3. 导出为Excel或CSV格式

#### 步骤3: 数据格式转换

将下载的数据转换为项目需要的格式：

```python
# 数据格式: [期号, 前区1-5, 后区1-2, 开奖日期]
["25135", 3, 8, 15, 22, 35, 4, 11, "2025-11-22"],
["25134", 5, 12, 19, 28, 33, 2, 9, "2025-11-20"],
...
```

#### 步骤4: 更新数据文件

编辑 `api/_lottery_data.py` 文件，添加新数据：

```python
# -*- coding: utf-8 -*-
"""
大乐透历史开奖数据模块（扩展到500期）
"""

LOTTERY_HISTORY = [
    # 按时间从新到旧排列
    ["25135", 3, 8, 15, 22, 35, 4, 11, "2025-11-22"],
    ["25134", 5, 12, 19, 28, 33, 2, 9, "2025-11-20"],
    # ... 继续添加数据 ...
    # 确保总共有500期数据
]

# 数据统计
TOTAL_PERIODS = 500
DATE_RANGE = "2021-XX-XX 至 2025-11-22"
PERIOD_RANGE = "21XXX - 25135"
```

---

## 使用自动化脚本

### 脚本说明

项目提供的 `scripts/fetch_500_periods.py` 脚本具有以下功能：

```python
# 主要功能
1. 多数据源自动切换
2. 数据验证和去重
3. 自动生成Python代码
4. 错误处理和重试机制
```

### 使用步骤

#### 1. 安装依赖

```bash
pip install beautifulsoup4 requests
```

#### 2. 运行脚本

```bash
python scripts/fetch_500_periods.py
```

#### 3. 查看输出

脚本会生成 `api/_lottery_data_500.py` 文件，包含500期数据。

#### 4. 替换原数据文件

```bash
# 备份原文件
cp api/_lottery_data.py api/_lottery_data_backup.py

# 使用新数据
cp api/_lottery_data_500.py api/_lottery_data.py
```

---

## 手动扩展数据

### Excel/CSV 转换工具

如果你有Excel或CSV格式的数据，可以使用以下Python脚本转换：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Excel/CSV 转换为 Python 数据格式"""

import pandas as pd

def convert_excel_to_python(excel_file, output_file):
    """
    将Excel/CSV文件转换为Python数据格式

    Excel格式要求：
    列1: 期号
    列2-6: 前区号码（5个）
    列7-8: 后区号码（2个）
    列9: 开奖日期
    """
    # 读取Excel
    df = pd.read_excel(excel_file) if excel_file.endswith('.xlsx') else pd.read_csv(excel_file)

    lines = []
    lines.append('# -*- coding: utf-8 -*-')
    lines.append('LOTTERY_HISTORY = [')

    for _, row in df.iterrows():
        period = row[0]
        front = [int(row[i]) for i in range(1, 6)]
        back = [int(row[i]) for i in range(6, 8)]
        date = str(row[8])

        line = f'    ["{period}", {", ".join(map(str, front))}, {", ".join(map(str, back))}, "{date}"],'
        lines.append(line)

    lines.append(']')

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✅ 转换完成！共 {len(df)} 期数据")
    print(f"输出文件: {output_file}")

# 使用示例
convert_excel_to_python('lottery_data.xlsx', 'api/_lottery_data.py')
```

### 数据格式要求

**必须字段：**
- `期号`: 格式为YYNNN（如25135表示2025年第135期）
- `前区号码`: 5个不重复的1-35之间的整数
- `后区号码`: 2个不重复的1-12之间的整数
- `开奖日期`: YYYY-MM-DD格式

**数据验证规则：**
```python
def validate_lottery_data(period, front, back, date):
    """数据验证"""
    # 1. 期号格式
    assert len(period) == 5 and period.isdigit()

    # 2. 前区号码
    assert len(front) == 5
    assert all(1 <= num <= 35 for num in front)
    assert len(set(front)) == 5  # 无重复

    # 3. 后区号码
    assert len(back) == 2
    assert all(1 <= num <= 12 for num in back)
    assert len(set(back)) == 2  # 无重复

    # 4. 日期格式
    assert len(date) == 10
    assert date[4] == '-' and date[7] == '-'
```

---

## 数据验证

### 自动验证脚本

创建验证脚本 `scripts/validate_data.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据验证工具"""

def validate_lottery_history():
    """验证历史数据的完整性和正确性"""
    from api._lottery_data import LOTTERY_HISTORY

    print("="*60)
    print("📊 数据验证报告")
    print("="*60)

    total_periods = len(LOTTERY_HISTORY)
    print(f"\n✓ 总期数: {total_periods}")

    # 期号范围
    periods = [item[0] for item in LOTTERY_HISTORY]
    print(f"✓ 期号范围: {min(periods)} - {max(periods)}")

    # 日期范围
    dates = [item[8] for item in LOTTERY_HISTORY]
    print(f"✓ 日期范围: {min(dates)} - {max(dates)}")

    # 数据完整性检查
    errors = []

    for i, item in enumerate(LOTTERY_HISTORY):
        period, *numbers, date = item
        front = numbers[:5]
        back = numbers[5:7]

        # 检查前区
        if len(front) != 5:
            errors.append(f"第{i+1}条: 前区号码数量错误")
        elif not all(1 <= n <= 35 for n in front):
            errors.append(f"第{i+1}条: 前区号码超出范围")
        elif len(set(front)) != 5:
            errors.append(f"第{i+1}条: 前区号码有重复")

        # 检查后区
        if len(back) != 2:
            errors.append(f"第{i+1}条: 后区号码数量错误")
        elif not all(1 <= n <= 12 for n in back):
            errors.append(f"第{i+1}条: 后区号码超出范围")
        elif len(set(back)) != 2:
            errors.append(f"第{i+1}条: 后区号码有重复")

    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors[:10]:  # 只显示前10个
            print(f"  - {error}")
    else:
        print("\n✅ 所有数据格式验证通过！")

    print("="*60)

if __name__ == '__main__':
    validate_lottery_history()
```

### 运行验证

```bash
python scripts/validate_data.py
```

---

## 数据更新建议

### 定期更新策略

**推荐频率:** 每周更新3次（开奖后立即更新）

**大乐透开奖时间:**
- 周一: 20:30
- 周三: 20:30
- 周六: 20:30

### 自动化更新（GitHub Actions）

项目已配置GitHub Actions自动更新（参见 `.github/workflows/update-lottery.yml`）：

```yaml
name: Update Lottery Data

on:
  schedule:
    # 每周一、三、六 21:00 UTC+8 自动运行
    - cron: '0 13 * * 1,3,6'
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Fetch new data
        run: python scripts/fetch_lottery.py
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add api/_lottery_data.py
          git commit -m "Update lottery data" || echo "No changes"
          git push
```

---

## 常见问题

### Q1: 为什么自动脚本无法获取数据？

**可能原因：**
- 网络限制或防火墙
- 数据源网站维护
- IP被限制访问

**解决方案：**
- 使用代理或VPN
- 尝试其他数据源
- 手动下载数据

### Q2: 数据量达到500期后还需要继续扩展吗？

**建议：**
- 500期是推荐的最小值
- 有条件可以扩展到1000期或更多
- 但要注意Vercel Serverless的文件大小限制（最大50MB）

### Q3: 如何确保数据质量？

**质量保证措施：**
1. 使用官方数据源
2. 运行验证脚本
3. 对比多个数据源
4. 定期人工抽查

---

## 联系支持

如果在数据扩展过程中遇到问题：

1. 查看 [GitHub Issues](https://github.com/your-repo/issues)
2. 提交新的Issue描述问题
3. 附上错误日志和数据样本

---

**最后更新**: 2026-01-18
**文档版本**: 1.0
