#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号推文生成API - 支持DeepSeek优化
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import random
import os
import urllib.request
import urllib.error

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# ML小知识库
ML_KNOWLEDGE = [
    {"title": "什么是LSTM？", "content": "LSTM(长短期记忆网络)是一种特殊的循环神经网络，能够学习长期依赖关系。它通过门机制控制信息的流动，特别适合处理时间序列数据。"},
    {"title": "Transformer的注意力机制", "content": "Transformer模型的核心是自注意力机制，它能够让模型关注输入序列中不同位置的信息，帮助发现不同号码之间的关联性。"},
    {"title": "XGBoost的梯度提升", "content": "XGBoost是一种强大的集成学习算法，通过逐步添加决策树来纠正前面模型的错误，能够处理各种统计特征。"},
    {"title": "随机森林的投票机制", "content": "随机森林由多棵决策树组成，每棵树独立预测，最终通过投票确定结果，这种群体智慧能有效降低过拟合风险。"},
    {"title": "特征工程的重要性", "content": "特征工程是将原始数据转换为更有价值信息的过程，包括热门号码、冷门号码、遗漏期数等特征。"},
    {"title": "模型集成的威力", "content": "单个模型都有局限性，但将多个模型组合起来往往能获得更好的效果，取长补短，提高预测的稳定性。"},
    {"title": "置信度是什么？", "content": "置信度表示模型对自己预测结果的信心程度，但彩票本质上是随机的，置信度只能作为参考。"},
    {"title": "什么是过拟合？", "content": "过拟合是模型记住了训练数据的噪声而非真正规律的现象，我们通过交叉验证等技术防止过拟合。"},
    {"title": "时间序列分析", "content": "彩票号码可以看作时间序列数据，时间序列分析寻找数据中的趋势和周期性模式。"},
    {"title": "概率与随机性", "content": "彩票本质上是一个概率游戏，AI预测并不能改变这个事实，但可以帮助分析历史数据中的统计特征。"}
]

def call_deepseek(prompt, max_tokens=2500):
    """调用DeepSeek API生成内容"""
    if not DEEPSEEK_API_KEY:
        return None
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一位专业的科普作家，擅长将复杂的机器学习和数据分析概念用通俗易懂、生动有趣的语言解释给普通读者。你的文章风格轻松活泼，善于使用比喻和类比，同时保持专业性。请用中文Markdown格式输出。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return None

def get_image_prompt(period):
    """生成当期插图提示词"""
    seed = int(period) % 10
    prompts = [
        f"数字{period[-2:]}在宇宙星空中闪耀，周围环绕着数据流和AI神经网络，紫蓝色调，科幻艺术风格，4K高清",
        f"未来感水晶球显示第{period}期预测数字，全息投影统计图表环绕，赛博朋克风格，霓虹灯光",
        f"AI机器人正在分析彩票数据，多屏幕显示期号{period}，流动数据矩阵背景，科技蓝主调",
        f"量子计算机核心运算，光粒子组成数字{period[-2:]}形状，梦幻紫色和金色，抽象科技艺术",
        f"神经网络三维可视化，发光节点闪烁第{period}期关键数字，深邃黑色背景，霓虹色彩",
        f"四个AI模型化身为四种元素：火(LSTM)、水(Transformer)、土(XGBoost)、风(RF)融合成预测能量球",
        f"深度学习层次抽象表达，层层神经元如同未来城市夜景，第{period}期数字在最顶层闪耀",
        f"数据科学家的控制室，巨大全息屏幕显示第{period}期分析，周围漂浮着图表和代码",
        f"时间线上的数据节点，高亮显示第{period}期，过去和未来的数据流在此交汇，时空概念艺术",
        f"一本发光的魔法书打开，页面上浮现第{period}期预测数字和公式，魔法粒子飘散，奇幻科技结合"
    ]
    return prompts[seed]

def get_dynamic_title(hit_count, period):
    """生成动态标题"""
    if hit_count >= 4:
        titles = [
            f"🎯 第{period}期预测：上期命中{hit_count}个，AI状态火热！",
            f"🔥 连续发力！第{period}期深度分析震撼来袭",
            f"💪 命中{hit_count}个！第{period}期乘胜追击"
        ]
    elif hit_count >= 2:
        titles = [
            f"📊 第{period}期预测：数据揭示新趋势",
            f"🔮 第{period}期深度解析：模型持续进化中",
            f"🎲 第{period}期分析：稳扎稳打，步步为营"
        ]
    else:
        titles = [
            f"🤖 第{period}期预测：模型调优重新出发",
            f"📈 第{period}期分析：从数据中寻找新规律",
            f"🔬 第{period}期：AI学习永不止步"
        ]
    return random.choice(titles)

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            tweet_type = request_data.get('type', 'detailed')
            prediction = request_data.get('prediction', {}) or {}
            last_actual = request_data.get('last_actual', {}) or {}
            last_predicted = request_data.get('last_predicted', {}) or {}
            statistics = request_data.get('statistics', {}) or {}
            ml_models = request_data.get('ml_models', {}) or {}
            target_period = str(request_data.get('target_period', '25142'))
            
            # 计算命中数
            hit_count = 0
            front_hits = []
            back_hits = []
            if last_actual and last_predicted:
                actual_front = set(last_actual.get('front', []) or [])
                actual_back = set(last_actual.get('back', []) or [])
                pred_front = set(last_predicted.get('front', []) or [])
                pred_back = set(last_predicted.get('back', []) or [])
                front_hits = sorted(actual_front & pred_front)
                back_hits = sorted(actual_back & pred_back)
                hit_count = len(front_hits) + len(back_hits)
            
            ml_knowledge = random.choice(ML_KNOWLEDGE)
            title = get_dynamic_title(hit_count, target_period)
            image_prompt = get_image_prompt(target_period)
            date_str = datetime.now().strftime('%Y年%m月%d日')
            
            # 获取预测号码
            front = prediction.get('front', []) or []
            back = prediction.get('back', []) or []
            confidence = prediction.get('confidence', 0.75)
            
            front_str = ' '.join([str(n).zfill(2) for n in front]) if front else '--'
            back_str = ' '.join([str(n).zfill(2) for n in back]) if back else '--'
            
            # 先生成基础文章框架
            base_article = self._build_base_article(
                title, date_str, target_period, front_str, back_str, confidence,
                last_actual, last_predicted, front_hits, back_hits, hit_count,
                ml_models, statistics, ml_knowledge, image_prompt, tweet_type
            )
            
            # 尝试用DeepSeek优化（如果API可用且不是简洁版）
            deepseek_used = False
            final_article = base_article
            
            if DEEPSEEK_API_KEY and tweet_type != 'simple':
                enhanced = self._enhance_with_deepseek(
                    base_article, ml_knowledge, target_period, hit_count
                )
                if enhanced:
                    final_article = enhanced
                    deepseek_used = True
            
            response = {
                'status': 'success',
                'article': final_article,
                'title': title,
                'image_prompt': image_prompt,
                'ml_knowledge': ml_knowledge,
                'hit_count': hit_count,
                'deepseek_enhanced': deepseek_used,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json(200, response)
            
        except Exception as e:
            import traceback
            self._send_json(500, {
                'status': 'error',
                'message': str(e),
                'trace': traceback.format_exc()
            })
    
    def _build_base_article(self, title, date_str, target_period, front_str, back_str, 
                            confidence, last_actual, last_predicted, front_hits, back_hits,
                            hit_count, ml_models, statistics, ml_knowledge, image_prompt, tweet_type):
        """构建基础文章"""
        
        article = f"""# {title}

📅 {date_str} | 大乐透AI预测系统

---

"""
        # 上期回顾
        if last_actual:
            last_front = last_actual.get('front', []) or []
            last_back = last_actual.get('back', []) or []
            last_front_str = ' '.join([str(n).zfill(2) for n in last_front]) if last_front else '--'
            last_back_str = ' '.join([str(n).zfill(2) for n in last_back]) if last_back else '--'
            
            article += f"""## 📊 上期开奖回顾

**开奖号码：** {last_front_str} + {last_back_str}

"""
            if last_predicted:
                pred_front_list = last_predicted.get('front', []) or []
                pred_back_list = last_predicted.get('back', []) or []
                pred_front_str = ' '.join([str(n).zfill(2) for n in pred_front_list]) if pred_front_list else '--'
                pred_back_str = ' '.join([str(n).zfill(2) for n in pred_back_list]) if pred_back_list else '--'
                
                article += f"""**上期AI预测：** {pred_front_str} + {pred_back_str}

**命中情况：** 
- 前区命中 {len(front_hits)} 个{('：' + ', '.join(map(str, front_hits))) if front_hits else ''}
- 后区命中 {len(back_hits)} 个{('：' + ', '.join(map(str, back_hits))) if back_hits else ''}

"""
                # 模型调整建议
                if hit_count >= 4:
                    article += """🎉 **表现优秀！** 模型捕捉到了较强的数据规律，本期继续保持当前配置。

"""
                elif hit_count >= 2:
                    article += """👍 **表现良好！** 部分预测与实际吻合，本期微调LSTM时序权重。

"""
                else:
                    article += """🔧 **模型优化中：** 
- 提高Transformer权重，加强号码关联性分析
- 增加历史数据回溯窗口至最近50期
- 平衡热冷号码比例

"""
        
        article += f"""---

## 🎯 第{target_period}期预测号码

**🔴 前区推荐：** {front_str}

**🔵 后区推荐：** {back_str}

**📊 综合置信度：** {confidence*100:.1f}%

"""
        
        # 详细版和分析版添加模型详情
        if tweet_type != 'simple' and ml_models:
            article += """---

## 🤖 各模型预测详情

| 模型 | 前区预测 | 后区预测 | 置信度 |
|:---:|:---:|:---:|:---:|
"""
            model_names = {'lstm': 'LSTM', 'transformer': 'Transformer', 'xgboost': 'XGBoost', 'random_forest': 'RandomForest'}
            for key, name in model_names.items():
                if key in ml_models:
                    m = ml_models[key]
                    m_front = ', '.join(map(str, m.get('front', []))) if m.get('front') else '--'
                    m_back = ', '.join(map(str, m.get('back', []))) if m.get('back') else '--'
                    m_conf = m.get('confidence', 0.75) * 100
                    article += f"| {name} | {m_front} | {m_back} | {m_conf:.1f}% |\n"
            
            article += "\n"
        
        # 统计分析（分析版）
        if tweet_type == 'analysis' and statistics:
            article += """---

## 📈 号码统计分析

"""
            if statistics.get('front_hot'):
                hot_nums = statistics['front_hot'][:5]
                hot_str = ', '.join([f"{n.get('number', n)}({n.get('count', '?')}次)" if isinstance(n, dict) else str(n) for n in hot_nums])
                article += f"**前区热门号码：** {hot_str}\n\n"
            
            if statistics.get('back_hot'):
                back_hot = statistics['back_hot'][:3]
                back_str = ', '.join([f"{n.get('number', n)}({n.get('count', '?')}次)" if isinstance(n, dict) else str(n) for n in back_hot])
                article += f"**后区热门号码：** {back_str}\n\n"
            
            if statistics.get('front_cold'):
                cold_nums = statistics['front_cold'][:5]
                cold_str = ', '.join([str(n.get('number', n)) if isinstance(n, dict) else str(n) for n in cold_nums])
                article += f"**前区冷门号码：** {cold_str}\n\n"
        
        # ML小知识
        article += f"""---

## 🧠 机器学习小课堂

### {ml_knowledge['title']}

{ml_knowledge['content']}

---

## 🖼️ 本期专属插图提示词

> {image_prompt}

---

## ⚠️ 免责声明

本预测基于历史数据分析和机器学习算法，仅供参考娱乐。彩票具有完全随机性，任何预测都不能保证准确。请理性购彩，量力而行。

---

*大乐透AI预测系统 | {date_str}*
*Powered by LSTM + Transformer + XGBoost + RandomForest*
"""
        
        return article
    
    def _enhance_with_deepseek(self, base_article, ml_knowledge, period, hit_count):
        """使用DeepSeek优化文章"""
        try:
            prompt = f"""请帮我优化以下大乐透预测公众号文章，要求：

1. **保持所有数据不变**：预测号码、置信度、统计数据等必须原样保留
2. **优化语言表达**：使用更生动有趣的科普风格语言
3. **增加过渡语句**：让文章更流畅自然
4. **扩展ML小课堂**：用更通俗易懂的比喻解释"{ml_knowledge['title']}"这个概念
5. **保持Markdown格式**：标题、表格、列表格式不变
6. **增加一些emoji**：适当使用表情符号增加趣味性
7. **字数控制**：总字数控制在1500字以内

上期命中情况：{hit_count}个号码

原文：
{base_article}

请直接输出优化后的完整Markdown文章，不要添加任何解释说明："""
            
            enhanced = call_deepseek(prompt, max_tokens=2500)
            if enhanced and len(enhanced) > 500:  # 确保返回内容足够
                return enhanced
            return None
        except Exception as e:
            print(f"DeepSeek enhancement error: {e}")
            return None
    
    def do_GET(self):
        """GET请求返回API信息"""
        self._send_json(200, {
            'status': 'success',
            'message': '公众号推文生成API',
            'deepseek_configured': bool(DEEPSEEK_API_KEY),
            'usage': 'POST请求，传入prediction、last_actual、type等参数'
        })
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
