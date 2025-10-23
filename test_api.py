import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app_id = os.getenv('LOTTERY_APP_ID')
app_secret = os.getenv('LOTTERY_APP_SECRET')

url = "https://www.mxnzp.com/api/lottery/common/history"
params = {
    'code': 'cjdlt',
    'size': 5,
    'app_id': app_id,
    'app_secret': app_secret
}

response = requests.get(url, params=params)
data = response.json()

print("API返回的原始数据：")
print(json.dumps(data, ensure_ascii=False, indent=2))
