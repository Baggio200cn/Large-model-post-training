"""AI智能体知识科普API - 提供科普文章内容"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

# 读取AI知识科普文章数据
def load_articles():
    """加载AI知识科普文章数据"""
    try:
        articles_file = os.path.join(os.path.dirname(__file__), 'ai_knowledge', 'ai_knowledge_articles.json')
        with open(articles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  加载文章数据失败: {str(e)}")
        return {
            "metadata": {
                "total_issues": 0,
                "description": "AI智能体知识科普系列",
                "error": str(e)
            },
            "articles": []
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 解析URL和查询参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # 加载文章数据
            data = load_articles()

            # 默认返回所有文章列表
            response = {
                'status': 'success',
                'metadata': data['metadata']
            }

            # 如果指定了issue参数，返回特定期的文章
            if 'issue' in query_params:
                try:
                    issue_num = int(query_params['issue'][0])
                    article = next((a for a in data['articles'] if a['issue'] == issue_num), None)

                    if article:
                        response['article'] = article
                    else:
                        response['status'] = 'error'
                        response['message'] = f'未找到第{issue_num}期文章'
                except ValueError:
                    response['status'] = 'error'
                    response['message'] = 'issue参数必须是数字'

            # 如果指定了list参数，只返回文章列表（不包含详细内容）
            elif 'list' in query_params or parsed_url.path.endswith('/list'):
                response['articles'] = [
                    {
                        'issue': a['issue'],
                        'title': a['title'],
                        'chapters': a['chapters'],
                        'tags': a['tags'],
                        'reading_time': a.get('reading_time', '未知'),
                        'difficulty': a.get('difficulty', '未知'),
                        'summary': a.get('summary', ''),
                        'status': a.get('status', 'published')
                    }
                    for a in data['articles']
                ]

            # 返回所有文章完整内容
            else:
                response['articles'] = data['articles']

            # 发送响应
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
            error_response = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_POST(self):
        """POST请求也支持，方便客户端调用"""
        self.do_GET()

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
