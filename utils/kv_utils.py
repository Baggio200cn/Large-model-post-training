import os
import requests

KV_URL = os.environ.get('KV_REST_API_URL')
KV_TOKEN = os.environ.get('KV_REST_API_TOKEN')
NAMESPACE = 'lottery-data'  # 替换为你的实际命名空间

def kv_set(key, value):
    """
    向 Vercel KV 存储数据
    :param key: 键名
    :param value: 字符串（如 JSON）
    """
    url = f"{KV_URL}/set/{NAMESPACE}:{key}"
    headers = {"Authorization": f"Bearer {KV_TOKEN}"}
    resp = requests.post(url, headers=headers, json={"value": value})
    resp.raise_for_status()

def kv_get(key):
    """
    从 Vercel KV 读取数据
    :param key: 键名
    :return: 字符串（如 JSON）
    """
    url = f"{KV_URL}/get/{NAMESPACE}:{key}"
    headers = {"Authorization": f"Bearer {KV_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("result", {}).get("value")
