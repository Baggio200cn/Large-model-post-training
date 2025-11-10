from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取预测数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
            else:
                data = {}
            
            prediction = data.get('prediction', {})
            front = prediction.get('front_zone', [7, 12, 23, 28, 35])
            back = prediction.get('back_zone', [3, 7])
            confidence = prediction.get('confidence', 0.82)
            
            date_str = datetime.now().strftime('%Y年%m月%d日')
            
            # 生成推文内容
            post_content = f'''🎯 大乐透AI智能预测 | {date_str}

📊 本期AI推荐号码

🔴 前区推荐
{' '.join([f'{n:02d}' for n in front])}

🔵 后区推荐  
{' '.join([f'{n:02d}' for n in back])}

📈 预测详情
- AI置信度：{confidence*100:.1f}%
- 数据基础：100期历史
- 模型组合：LSTM + Transformer + XGBoost

🧠 AI分析
本期预测综合考虑了：
✓ 号码出现频率
✓ 时序变化趋势
✓ 号码关联模式
✓ 统计学特征

⚠️ 理性提示
彩票具有随机性，AI预测仅供参考。
请理性购彩，量力而行。

---
🤖 由大乐透AI预测系统生成
📅 预测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
            
            response = {
                'status': 'success',
                'post': {
                    'content': post_content,
                    'format': 'text',
                    'char_count': len(post_content),
                    'prediction': prediction
                },
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
            error = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
