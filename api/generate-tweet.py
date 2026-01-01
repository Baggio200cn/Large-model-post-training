<<<<<<< HEAD
﻿from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import json
import traceback
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 科普写作要点（精华提炼）
POPULAR_SCIENCE_GUIDE = """
科普写作核心原则：
- 用日常语言解释复杂概念，避免术语堆砌。
- 以故事和人物为线索，增强叙事性。
- 强调研究的意义和影响，回答“为什么重要”。
- 善用类比，把抽象变具体。
- 结构清晰：开篇吸引、背景铺垫、方法揭秘、结果展示、意义阐释。
- 段落简短，主动语态，避免模糊表达。
- 适当承认局限，保持科学诚信。
"""

class ArticleRequest(BaseModel):
    title: str
    abstract: str
    authors: Optional[str] = None
    institution: Optional[str] = None
    keywords: Optional[str] = None
    target_audience: Optional[str] = '普通读者'
    length: Optional[str] = '中等'
    focus: Optional[str] = None
    style: Optional[str] = None

@app.post("/generate-tweet")
async def generate_tweet():
    try:
        # 生成模拟文章内容
        content = f"大乐透智能预测分析报告\n\n日期: {datetime.now().strftime('%Y-%m-%d')}\n\n本期推荐号码: {sorted(random.sample(range(1, 36), 5))} + {sorted(random.sample(range(1, 13), 2))}\n\n分析：本期号码基于历史数据与AI模型综合分析，具有较高参考价值。祝您好运！"
        response = {
            'status': 'success',
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        return response
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_response, ensure_ascii=False).encode('utf-8')

@app.post("/popularize-paper")
async def popularize_paper(req: ArticleRequest):
    """
    生成学术论文科普文章，融合最佳科普写作原则。
    """
    try:
        # 1. 开篇吸引
        opening = f"你是否曾好奇：{req.title}？今天，我们就来聊聊这项前沿研究背后的故事。"
        # 2. 背景铺垫
        background = f"这项研究由{req.authors or '一组科学家'}在{req.institution or '知名机构'}完成，旨在解决一个重要的科学问题。"
        # 3. 方法揭秘
        method = f"研究团队采用了创新的方法，具体来说：{req.abstract}。他们善用类比，将复杂问题变得易于理解。"
        # 4. 结果展示
        result = f"研究取得了突破性进展，为该领域带来了新的希望。"
        # 5. 意义阐释
        significance = f"这项研究不仅推动了学科发展，也有望影响我们的日常生活。为什么重要？因为它让我们离解决{req.focus or '关键科学难题'}更近一步。"
        # 6. 结尾平衡视角
        balance = "当然，科学探索永无止境，这项研究也有待进一步验证，但它无疑为未来打开了新大门。"
        # 7. 融入写作要点
        guide = POPULAR_SCIENCE_GUIDE
        # 8. 组装文章
        body = (
            f"{opening}\n\n"
            f"【背景故事】\n{background}\n\n"
            f"【方法揭秘】\n{method}\n\n"
            f"【结果展示】\n{result}\n\n"
            f"【意义阐释】\n{significance}\n\n"
            f"【科学视角】\n{balance}\n\n"
            f"\n---\n\n【科普写作要点】\n{guide}"
        )
        response = {
            'status': 'success',
            'content': body,
            'timestamp': datetime.now().isoformat()
        }
        return response
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        return error_response
=======
# -*- coding: utf-8 -*-
"""
禅心慧算 - 推文生成API（统一模板版）
"""

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ============ 统一模板配置 ============

PLATFORMS = {
    "weibo": {"name": "微博", "max_length": 2000, "min_length": 100},
    "xiaohongshu": {"name": "小红书", "max_length": 1000, "min_length": 300},
    "toutiao": {"name": "今日头条", "max_length": 2000, "min_length": 800},
    "twitter": {"name": "Twitter", "max_length": 280, "min_length": 50}
}

RISK_WORDS = {
    "预测": "分析",
    "预测号码": "概率计算",
    "中奖": "命中",
    "必中": "高频",
    "推荐号码": "参考数据",
    "投资建议": "技术分享",
    "稳赚": "学习"
}

DISCLAIMERS = {
    "short": "⚠️ 纯技术学习，彩票随机，理性娱乐！",
    "standard": "【声明】本内容为AI技术学习记录，不构成任何投资建议。彩票是随机事件，请理性娱乐。",
    "casual": "🎯 这是AI学习实验，彩票猜不准的～开心就好！"
}

# ============ 推文模板 ============

TWEET_TEMPLATES = {
    "tech_share": [
        "🤖 AI学习日记 | 用{models}分析{data_type}数据，探索机器学习在随机数据上的表现。结论：AI也猜不准随机数～技术很有趣，但彩票还是随机的！{disclaimer}",
        "📊 数据实验 | 训练了{models}模型，分析{period}期{data_type}数据。发现：所有模型命中率都接近随机水平，再次证明彩票的随机性！{disclaimer}",
        "🔬 ML实验记录 | 当深度学习遇上真正的随机数据会怎样？用{data_type}做了个实验，LSTM和Transformer都"认输"了～{disclaimer}"
    ],
    "philosophy": [
        "🧘 禅与AI | 机器学习教会我的事：有些事，算法再强也无能为力。随机之道，不可强求。{disclaimer}",
        "☯️ 技术感悟 | 用AI分析{data_type}，不是为了赢，而是为了理解"随机"的本质。万法皆空，理性为本。{disclaimer}"
    ],
    "casual": [
        "😂 AI：我分析了{period}期数据！\n彩票：我是随机的。\nAI：...\n\n技术学习很快乐，但别指望AI能猜中彩票哦～{disclaimer}",
        "🎲 让AI分析彩票数据的结果：它学会了"认命"。随机就是随机，这才是最大的收获！{disclaimer}"
    ]
}

# ============ 生成器类 ============

class TweetGenerator:
    """推文生成器"""
    
    def __init__(self, platform: str = "weibo", style: str = "tech_share"):
        self.platform = platform
        self.platform_config = PLATFORMS.get(platform, PLATFORMS["weibo"])
        self.style = style
        self.templates = TWEET_TEMPLATES.get(style, TWEET_TEMPLATES["tech_share"])
    
    def sanitize(self, content: str) -> str:
        """替换风险词"""
        for risk, safe in RISK_WORDS.items():
            content = content.replace(risk, safe)
        return content
    
    def generate(self, data_type: str = "大乐透", period: int = 260,
                 models: str = "LSTM+XGBoost", template_index: int = 0,
                 disclaimer_style: str = "short") -> dict:
        """生成推文"""
        
        template = self.templates[template_index % len(self.templates)]
        disclaimer = DISCLAIMERS.get(disclaimer_style, DISCLAIMERS["short"])
        
        content = template.format(
            data_type=data_type,
            period=period,
            models=models,
            disclaimer=disclaimer
        )
        
        # 安全化处理
        content = self.sanitize(content)
        
        # 长度检查
        max_len = self.platform_config["max_length"]
        if len(content) > max_len:
            content = content[:max_len-3] + "..."
        
        return {
            "success": True,
            "platform": self.platform,
            "platform_name": self.platform_config["name"],
            "style": self.style,
            "content": content,
            "length": len(content),
            "max_length": max_len,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_batch(self, data_type: str = "大乐透", period: int = 260,
                       models: str = "LSTM+XGBoost") -> list:
        """批量生成所有模板"""
        results = []
        for i, template in enumerate(self.templates):
            results.append(self.generate(
                data_type=data_type,
                period=period,
                models=models,
                template_index=i
            ))
        return results


# ============ DeepSeek集成（可选）============

def generate_with_deepseek(prompt_type: str, data_type: str = "大乐透",
                           period: int = 260) -> dict:
    """使用DeepSeek生成推文"""
    
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return {"success": False, "error": "未配置DEEPSEEK_API_KEY"}
    
    prompts = {
        "tech": f"写一条关于用AI分析{data_type}数据的技术分享推文，100字以内，强调这是学习实验，AI无法预测随机数，要有趣轻松",
        "philosophy": f"写一条融合禅意的AI技术感悟推文，关于机器学习与随机性，100字以内，有哲理感",
        "casual": f"写一条轻松幽默的推文，关于AI分析{data_type}数据的有趣发现，100字以内，要搞笑"
    }
    
    try:
        import urllib.request
        
        prompt = prompts.get(prompt_type, prompts["tech"])
        prompt += "\n\n要求：不要使用'预测'这个词，用'分析'代替。结尾加上：⚠️ 技术学习，理性娱乐"
        
        data = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.8
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            content = result["choices"][0]["message"]["content"]
            
            # 安全化
            for risk, safe in RISK_WORDS.items():
                content = content.replace(risk, safe)
            
            return {
                "success": True,
                "content": content,
                "source": "deepseek",
                "generated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ API Handler ============

class handler(BaseHTTPRequestHandler):
    
    def set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.set_cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.set_cors()
        self.end_headers()
    
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        action = query.get('action', ['generate'])[0]
        
        if action == 'info':
            self.send_json({
                "success": True,
                "name": "推文生成API",
                "platforms": list(PLATFORMS.keys()),
                "styles": list(TWEET_TEMPLATES.keys()),
                "disclaimer_styles": list(DISCLAIMERS.keys())
            })
            return
        
        if action == 'templates':
            self.send_json({
                "success": True,
                "templates": TWEET_TEMPLATES
            })
            return
        
        # 默认生成
        platform = query.get('platform', ['weibo'])[0]
        style = query.get('style', ['tech_share'])[0]
        data_type = query.get('data_type', ['大乐透'])[0]
        period = int(query.get('period', ['260'])[0])
        
        gen = TweetGenerator(platform, style)
        result = gen.generate(data_type=data_type, period=period)
        self.send_json(result)
    
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8')) if length > 0 else {}
            
            action = body.get('action', 'generate')
            
            # DeepSeek生成
            if action == 'deepseek':
                prompt_type = body.get('prompt_type', 'tech')
                data_type = body.get('data_type', '大乐透')
                period = body.get('period', 260)
                result = generate_with_deepseek(prompt_type, data_type, period)
                self.send_json(result)
                return
            
            # 批量生成
            if action == 'batch':
                platform = body.get('platform', 'weibo')
                style = body.get('style', 'tech_share')
                data_type = body.get('data_type', '大乐透')
                period = body.get('period', 260)
                
                gen = TweetGenerator(platform, style)
                results = gen.generate_batch(data_type=data_type, period=period)
                self.send_json({"success": True, "tweets": results})
                return
            
            # 单条生成
            platform = body.get('platform', 'weibo')
            style = body.get('style', 'tech_share')
            data_type = body.get('data_type', '大乐透')
            period = body.get('period', 260)
            models = body.get('models', 'LSTM+XGBoost')
            template_index = body.get('template_index', 0)
            disclaimer_style = body.get('disclaimer_style', 'short')
            
            gen = TweetGenerator(platform, style)
            result = gen.generate(
                data_type=data_type,
                period=period,
                models=models,
                template_index=template_index,
                disclaimer_style=disclaimer_style
            )
            self.send_json(result)
            
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
```

---

## API使用示例

**获取信息：**
```
GET /api/generate-tweet?action=info
```

**生成推文：**
```
GET /api/generate-tweet?platform=weibo&style=tech_share
>>>>>>> 75fe0abe06fc410ae65f8e03c73d15ef57737fbd
