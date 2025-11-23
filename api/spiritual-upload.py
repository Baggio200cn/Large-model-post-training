"""灵修内容上传API - 内存存储版本"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 全局内存存储
SPIRITUAL_DATA = {
    'images': [],
    'texts': [],
    'metadata': {
        'last_update': None,
        'total_uploads': 0
    }
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            action = request_data.get('action', 'upload')
            
            if action == 'upload':
                upload_type = request_data.get('type', 'text')
                
                if upload_type == 'image':
                    # 上传图片（base64）
                    image_data = request_data.get('image_data', '')
                    image_name = request_data.get('image_name', 'unnamed.jpg')
                    object_count = request_data.get('object_count', 0)  # 用户输入的物品数量
                    
                    image_entry = {
                        'data': image_data[:100] + '...',  # 只存储前100字符用于验证
                        'name': image_name,
                        'object_count': object_count,
                        'uploaded_at': datetime.now().isoformat(),
                        'id': len(SPIRITUAL_DATA['images']) + 1
                    }
                    
                    SPIRITUAL_DATA['images'].append(image_entry)
                    message = f'图片 {image_name} 上传成功'
                    
                elif upload_type == 'text':
                    # 上传文字
                    text_content = request_data.get('text', '')
                    
                    text_entry = {
                        'content': text_content,
                        'length': len(text_content),
                        'uploaded_at': datetime.now().isoformat(),
                        'id': len(SPIRITUAL_DATA['texts']) + 1
                    }
                    
                    SPIRITUAL_DATA['texts'].append(text_entry)
                    message = '文字内容上传成功'
                
                SPIRITUAL_DATA['metadata']['last_update'] = datetime.now().isoformat()
                SPIRITUAL_DATA['metadata']['total_uploads'] += 1
                
                response = {
                    'status': 'success',
                    'message': message,
                    'storage_info': {
                        'total_images': len(SPIRITUAL_DATA['images']),
                        'total_texts': len(SPIRITUAL_DATA['texts']),
                        'last_update': SPIRITUAL_DATA['metadata']['last_update']
                    }
                }
            
            elif action == 'view':
                # 查看当前存储的内容
                response = {
                    'status': 'success',
                    'data': {
                        'images': [
                            {
                                'id': img['id'],
                                'name': img['name'],
                                'object_count': img.get('object_count', 0),
                                'uploaded_at': img['uploaded_at']
                            }
                            for img in SPIRITUAL_DATA['images']
                        ],
                        'texts': [
                            {
                                'id': txt['id'],
                                'preview': txt['content'][:50] + '...' if len(txt['content']) > 50 else txt['content'],
                                'length': txt['length'],
                                'uploaded_at': txt['uploaded_at']
                            }
                            for txt in SPIRITUAL_DATA['texts']
                        ],
                        'metadata': SPIRITUAL_DATA['metadata']
                    }
                }
            
            elif action == 'clear':
                # 清空存储
                SPIRITUAL_DATA['images'] = []
                SPIRITUAL_DATA['texts'] = []
                SPIRITUAL_DATA['metadata']['last_update'] = datetime.now().isoformat()
                
                response = {
                    'status': 'success',
                    'message': '所有灵修内容已清空'
                }
            
            else:
                response = {
                    'status': 'error',
                    'message': f'未知操作: {action}'
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        # GET请求查看存储内容
        try:
            response = {
                'status': 'success',
                'data': {
                    'images': [
                        {
                            'id': img['id'],
                            'name': img['name'],
                            'object_count': img.get('object_count', 0),
                            'uploaded_at': img['uploaded_at']
                        }
                        for img in SPIRITUAL_DATA['images']
                    ],
                    'texts': [
                        {
                            'id': txt['id'],
                            'preview': txt['content'][:50] + '...' if len(txt['content']) > 50 else txt['content'],
                            'length': txt['length'],
                            'uploaded_at': txt['uploaded_at']
                        }
                        for txt in SPIRITUAL_DATA['texts']
                    ],
                    'metadata': SPIRITUAL_DATA['metadata']
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
