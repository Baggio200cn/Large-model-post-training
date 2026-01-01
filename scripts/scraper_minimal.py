#!/usr/bin/env python3

import json
import os
import requests
from bs4 import BeautifulSoup


def fetch_data(size=30):
    url = "https://www.lottery.gov.cn/dlt/dltHistoryData.jhtml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, params={'size': size}, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        data = []
        for row in soup.select('table.lottery-table tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 8:
                data.append({
                    'period': cols[0].text.strip(),
                    'date': cols[1].text.strip(),
                    'front': [cols[i].text.strip() for i in range(2, 7)],
                    'back': [cols[i].text.strip() for i in range(7, 9)]
                })
        return data
    except:
        return []


def save_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_data(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    path = 'data/raw/history.json'
    existing = load_data(path)
    new = fetch_data(50 if not existing else 30)
    
    if not new:
        print("Fetch failed")
        return
    
    if not existing:
        save_data(new, path)
        print(f"Saved {len(new)} records")
        return
    
    if new[0]['period'] == existing[0]['period']:
        print("Already up to date")
        return
    
    periods = {d['period'] for d in existing}
    added = [d for d in new if d['period'] not in periods]
    
    if added:
        save_data(added + existing, path)
        print(f"Added {len(added)} records")


if __name__ == '__main__':
    main()
