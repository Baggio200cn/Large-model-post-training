import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_latest_dlt_result():
    """
    抓取500彩票网大乐透最新一期开奖信息。
    返回dict: {period, draw_date, winning_numbers, ...}
    """
    url = "https://datachart.500.com/dlt/history/newinc/history.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'gb2312'
    # 保存HTML源码到桌面，便于调试和分析
    desktop_path = r'C:\Users\baggio200cn\Desktop\dlt_requests_debug.html'
    with open(desktop_path, 'w', encoding='utf-8') as f:
        f.write(resp.text)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 查找数据表格
    table = soup.find('table', attrs={'id': 't1'})
    if not table:
        raise Exception('未找到开奖数据表格')
    # 查找第一个数据行
    data_row = None
    for row in table.find_all('tr'):
        tds = row.find_all('td')
        if tds and tds[0].text.strip().isdigit():
            data_row = tds
            break
    if not data_row:
        raise Exception('未找到开奖数据行')
    period = data_row[0].text.strip()
    try:
        front_zone = [int(data_row[i].text.strip()) for i in range(1, 6)]
        back_zone = [int(data_row[i].text.strip()) for i in range(6, 8)]
    except Exception:
        raise Exception('开奖号码解析失败')
    draw_date = data_row[-1].text.strip()
    result = {
        'period': period,
        'draw_date': draw_date,
        'winning_numbers': {
            'front_zone': front_zone,
            'back_zone': back_zone,
            'display': f"{' '.join([f'{n:02d}' for n in front_zone])} + {' '.join([f'{n:02d}' for n in back_zone])}"
        }
    }
    return result
