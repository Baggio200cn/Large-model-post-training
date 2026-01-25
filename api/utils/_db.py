"""数据库操作模块 - MongoDB Atlas"""
import os
from datetime import datetime

# MongoDB连接字符串（从环境变量读取）
MONGODB_URI = os.environ.get('MONGODB_URI', '')

_client = None
_db = None

def get_database():
    """获取数据库连接"""
    global _client, _db
    if not MONGODB_URI:
        raise Exception("未配置MONGODB_URI环境变量")
    if _db is None:
        from pymongo import MongoClient
        _client = MongoClient(MONGODB_URI)
        _db = _client['lottery_db']
    return _db

def get_all_lottery_data():
    """获取所有历史数据"""
    try:
        db = get_database()
        collection = db['lottery_history']
        data = list(collection.find({}, {'_id': 0}).sort('period', 1))
        return data
    except Exception as e:
        print(f"获取数据失败: {e}")
        return []

def add_lottery_data(period, date, front_zone, back_zone):
    """添加新的开奖数据"""
    try:
        db = get_database()
        collection = db['lottery_history']
        existing = collection.find_one({'period': period})
        if existing:
            return {'success': False, 'message': f'期数{period}已存在'}
        document = {
            'period': period,
            'date': date,
            'front_zone': front_zone,
            'back_zone': back_zone,
            'created_at': datetime.now().isoformat()
        }
        collection.insert_one(document)
        return {'success': True, 'message': f'成功添加期数{period}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def delete_lottery_data(period):
    """删除指定期数的数据"""
    try:
        db = get_database()
        collection = db['lottery_history']
        result = collection.delete_one({'period': period})
        if result.deleted_count > 0:
            return {'success': True, 'message': f'成功删除期数{period}'}
        else:
            return {'success': False, 'message': f'期数{period}不存在'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def update_lottery_data(period, date, front_zone, back_zone):
    """更新指定期数的数据"""
    try:
        db = get_database()
        collection = db['lottery_history']
        result = collection.update_one(
            {'period': period},
            {'$set': {
                'date': date,
                'front_zone': front_zone,
                'back_zone': back_zone,
                'updated_at': datetime.now().isoformat()
            }}
        )
        if result.modified_count > 0:
            return {'success': True, 'message': f'成功更新期数{period}'}
        else:
            return {'success': False, 'message': f'期数{period}不存在或数据未变化'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
