from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

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
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            action = request_data.get('action', 'view')
            
            if action == 'upload':
                upload_type = request_data.get('type', 'image')
                
                if upload_type == 'image':
                    image_data = {
                        'data': request_data.get('image_data', ''),
                        'name': request_data.get('image_name', 'unnamed.jpg'),
                        'object_count': request_data.get('object_count', 1),
                        'uploaded_at': datetime.now().isoformat(),
                        'id': len(SPIRITUAL_DATA['images']) + 1
                    }
                    SPIRITUAL_DATA['images'].append(image_data)
                    message = '图片上传成功'
                    
                elif upload_type == 'text':
                    text_data = {
                        'content': request_data.get('text', ''),
                        'length': len(request_data.get('text', '')),
                        'uploaded_at': datetime.now().isoformat(),
                        'id': len(SPIRITUAL_DATA['texts']) + 1
                    }
                    SPIRITUAL_DATA['texts'].append(text_data)
                    message = '文字上传成功'
                else:
                    raise ValueError('未知的上传类型')
                
                SPIRITUAL_DATA['metadata']['last_update'] = datetime.now().isoformat()
                SPIRITUAL_DATA['metadata']['total_uploads'] += 1
                
            elif action == 'clear':
                SPIRITUAL_DATA['images'] = []
                SPIRITUAL_DATA['texts'] = []
                SPIRITUAL_DATA['metadata']['last_update'] = datetime.now().isoformat()
                message = '数据已清空'
                
            elif action == 'view':
                message = '数据查看成功'
            else:
                raise ValueError('未知的操作类型')
            
            response = {
                'status': 'success',
                'message': message,
                'data': SPIRITUAL_DATA,
                'timestamp': datetime.now().isoformat()
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
        try:
            response = {
                'status': 'success',
                'message': '数据查看成功',
                'data': SPIRITUAL_DATA,
                'timestamp': datetime.now().isoformat()
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
