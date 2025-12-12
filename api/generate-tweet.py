#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号推文生成API - 调用DeepSeek生成科普风格文章
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
    {
        "title": "什么是LSTM？",
        "content": "LSTM(长短期记忆网络)是一种特殊的循环神经网络，能够学习长期依赖关系。它通过"门"机制控制信息的流动，特别适合处理时间序列数据。在彩票预测中，LSTM能捕捉号码出现的时序规律。",
        "image_prompt": "一个抽象的神经网络图，蓝色神经元通过金色连接线相连，背景是深蓝色的数据流，科技感十足，3D渲染风格"
    },
    {
        "title": "Transformer的注意力机制",
        "content": "Transformer模型的核心是自注意力机制，它能够让模型关注输入序列中不同位置的信息。在号码预测中，注意力机制帮助发现不同号码之间的关联性，比如某些号码经常一起出现。",
        "image_prompt": "一个发光的注意力矩阵可视化，彩色热力图显示不同元素之间的关联强度，紫色和金色渐变，未来科技风格"
    },
    {
        "title": "XGBoost的梯度提升",
        "content": "XGBoost是一种强大的集成学习算法，通过逐步添加决策树来纠正前面模型的错误。它的优势在于能够处理各种统计特征，如号码频率、遗漏期数等，从多个维度分析数据。",
        "image_prompt": "多棵决策树组成的森林，树叶是彩色的数据点，树干由算法符号构成，绿色和金色主调，数字艺术风格"
    },
    {
        "title": "随机森林的投票机制",
        "content": "随机森林由多棵决策树组成，每棵树独立预测，最终通过投票确定结果。这种"群体智慧"能有效降低过拟合风险。在预测中，不同的树关注不同的特征，综合得出更稳健的预测。",
        "image_prompt": "一片由数字和代码构成的魔幻森林，树木发出柔和的蓝绿色光芒，空中飘浮着投票气泡，梦幻科技风格"
    },
    {
        "title": "特征工程的重要性",
        "content": "特征工程是将原始数据转换为更有价值信息的过程。在彩票分析中，我们提取热门号码、冷门号码、遗漏期数、号码对关联等特征，这些特征直接影响模型的预测效果。",
        "image_prompt": "数据炼金术，原始数据矿石被提炼成闪亮的特征宝石，传送带和齿轮装置，蒸汽朋克与科技融合风格"
    },
    {
        "title": "模型集成的威力",
        "content": "单个模型都有局限性，但将多个模型组合起来往往能获得更好的效果。我们的系统融合了LSTM、Transformer、XGBoost和RandomForest四种模型，取长补短，提高预测的稳定性。",
        "image_prompt": "四个不同颜色的能量球汇聚成一个更大的金色光球，周围环绕着数据流和公式，宇宙星空背景，科幻艺术风格"
    },
    {
        "title": "置信度是什么？",
        "content": "置信度表示模型对自己预测结果的"信心"程度。高置信度意味着模型在历史数据中找到了较强的规律支持，但彩票本质上是随机的，置信度只能作为参考而非确定性指标。",
        "image_prompt": "一个精密的仪表盘显示置信度刻度，指针指向高区域，周围是数据分析图表，专业科技蓝色调"
    },
    {
        "title": "什么是过拟合？",
        "content": "过拟合是模型"记住"了训练数据的噪声而非真正规律的现象。就像学生只背答案不理解原理。我们通过交叉验证、正则化等技术防止过拟合，确保模型能泛化到新数据。",
        "image_prompt": "一条曲线完美穿过所有散点但过于弯曲扭曲，旁边是一条简洁的直线更好地拟合趋势，对比图风格，教育插图"
    },
    {
        "title": "时间序列分析",
        "content": "彩票号码可以看作时间序列数据，即按时间顺序排列的数据点。时间序列分析寻找数据中的趋势、周期性和季节性模式，帮助我们理解号码出现的时间规律。",
        "image_prompt": "一条蜿蜒的时间线，上面标记着数据点和趋势波动，背景是时钟和日历元素，蓝色和橙色主调，信息图风格"
    },
    {
        "title": "概率与随机性",
        "content": "彩票本质上是一个概率游戏，每个号码被抽中的概率是相等的。AI预测并不能改变这个事实，但可以帮助我们分析历史数据中的统计特征，做出更informed的选择。",
        "image_prompt": "多个彩色骰子在空中翻滚，周围是概率公式和统计图表，动感十足，数学艺术风格"
    }
]

def call_deepseek_api(prompt, max_tokens=2000):
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
                    'content': '你是一位专业的科普作家，擅长将复杂的机器学习和数据分析概念用通俗易懂的语言解释给普通读者。你的文章风格轻松有趣，善于使用比喻和类比，同时保持专业性和准确性。'
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

def generate_comparison_analysis(last_actual, last_predicted):
    """生成上期对比分析"""
    if not last_actual or not last_predicted:
        return "暂无上期对比数据"
    
    # 计算命中情况
    actual_front = set(last_actual.get('front', []))
    actual_back = set(last_actual.get('back', []))
    pred_front = set(last_predicted.get('front', []))
    pred_back = set(last_predicted.get('back', []))
    
    front_hit = actual_front & pred_front
    back_hit = actual_back & pred_back
    
    hit_count = len(front_hit) + len(back_hit)
    
    # 生成分析文本
    analysis = f"""
### 📊 上期预测回顾

**实际开奖号码：** {' '.join(map(lambda x: str(x).zfill(2), sorted(actual_front)))} + {' '.join(map(lambda x: str(x).zfill(2), sorted(actual_back)))}

**AI预测号码：** {' '.join(map(lambda x: str(x).zfill(2), sorted(pred_front)))} + {' '.join(map(lambda x: str(x).zfill(2), sorted(pred_back)))}

**命中情况：** 
- 前区命中 {len(front_hit)} 个：{', '.join(map(str, sorted(front_hit))) if front_hit else '无'}
- 后区命中 {len(back_hit)} 个：{', '.join(map(str, sorted(back_hit))) if back_hit else '无'}
"""
    
    # 命中评价
    if hit_count >= 4:
        analysis += "\n🎉 **表现优秀！** 模型捕捉到了较强的数据规律。\n"
    elif hit_count >= 2:
        analysis += "\n👍 **表现良好！** 部分预测与实际吻合。\n"
    else:
        analysis += "\n🤔 **继续优化！** 彩票随机性较强，我们将调整模型参数。\n"
    
    return analysis

def generate_model_adjustment(hit_count, models_performance):
    """生成模型调整建议"""
    adjustments = []
    
    if hit_count < 2:
        adjustments.append("- 📈 **提高Transformer权重**：加强号码关联性分析")
        adjustments.append("- 🔄 **增加历史数据回溯**：扩大分析窗口至最近50期")
        adjustments.append("- ⚖️ **平衡热冷号比例**：当前可能过于偏向热门号码")
    elif hit_count < 4:
        adjustments.append("- 🎯 **微调LSTM时序权重**：加强对近期趋势的捕捉")
        adjustments.append("- 🔍 **优化特征工程**：增加号码间隔特征")
    else:
        adjustments.append("- ✅ **保持当前模型配置**：权重分配效果良好")
        adjustments.append("- 📊 **继续观察验证**：收集更多数据验证稳定性")
    
    return "\n".join(adjustments)

def generate_dynamic_title(hit_count, period):
    """生成动态标题"""
    titles = {
        'excellent': [
            f"🎯 第{period}期预测：上期命中{hit_count}个，模型状态火热！",
            f"🔥 AI预测连续发力！第{period}期深度分析来了",
            f"💪 命中{hit_count}个！第{period}期继续乘胜追击"
        ],
        'good': [
            f"📊 第{period}期预测：数据分析揭示新趋势",
            f"🎲 第{period}期深度解析：模型优化进行时",
            f"🔮 AI预测第{period}期：稳扎稳打，步步为营"
        ],
        'normal': [
            f"🤖 第{period}期预测：模型调优后重新出发",
            f"📈 第{period}期分析：从数据中寻找新规律",
            f"🎯 第{period}期预测：AI学习永不止步"
        ]
    }
    
    if hit_count >= 4:
        category = 'excellent'
    elif hit_count >= 2:
        category = 'good'
    else:
        category = 'normal'
    
    return random.choice(titles[category])

def generate_image_prompt(period, theme='prediction'):
    """生成当期专属的插图提示词"""
    # 基于期号生成变化
    seed = int(period) % 10
    
    base_prompts = [
        f"数字{period[-2:]}在宇宙星空中闪耀，周围环绕着数据流和AI神经网络，紫蓝色调，科幻艺术风格，4K高清",
        f"一个未来感的水晶球显示着第{period}期的数字预测，周围是全息投影的统计图表，赛博朋克风格",
        f"AI机器人正在分析彩票数据，屏幕显示期号{period}，背景是流动的数据矩阵，科技蓝主调",
        f"量子计算机正在运算，粒子组成数字{period[-2:]}的形状，梦幻紫色和金色，抽象科技艺术",
        f"数据科学家的工作台，大屏幕显示第{period}期分析，周围是图表和代码，温暖的工作室光线",
        f"一本打开的魔法书，页面上浮现第{period}期的预测数字，魔法粒子飘散，奇幻与科技结合",
        f"神经网络的三维可视化，节点闪烁着第{period}期的关键数字，深邃的黑色背景，霓虹色彩",
        f"时间线上的数据节点，高亮显示第{period}期，过去和未来的数据流汇聚，时间旅行概念艺术",
        f"四个AI模型化身为四种元素：火(LSTM)、水(Transformer)、土(XGBoost)、风(RF)，融合成预测能量，奇幻风格",
        f"深度学习的抽象表达，层层神经元如同城市夜景，第{period}期数字在顶层闪耀，赛博城市风格"
    ]
    
    return base_prompts[seed]

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            # 获取请求参数
            tweet_type = request_data.get('type', 'detailed')  # simple, detailed, analysis
            current_prediction = request_data.get('prediction', {})
            last_actual = request_data.get('last_actual', {})
            last_predicted = request_data.get('last_predicted', {})
            statistics = request_data.get('statistics', {})
            ml_models = request_data.get('ml_models', {})
            target_period = request_data.get('target_period', '25142')
            
            # 计算命中数
            hit_count = 0
            if last_actual and last_predicted:
                actual_front = set(last_actual.get('front', []))
                actual_back = set(last_actual.get('back', []))
                pred_front = set(last_predicted.get('front', []))
                pred_back = set(last_predicted.get('back', []))
                hit_count = len(actual_front & pred_front) + len(actual_back & pred_back)
            
            # 选择ML小知识
            ml_knowledge = random.choice(ML_KNOWLEDGE)
            
            # 生成动态标题
            title = generate_dynamic_title(hit_count, target_period)
            
            # 生成插图提示词
            image_prompt = generate_image_prompt(target_period)
            
            # 生成日期
            date_str = datetime.now().strftime('%Y年%m月%d日')
            
            # 构建文章内容
            if tweet_type == 'simple':
                article = self._generate_simple_tweet(
                    title, date_str, target_period, current_prediction,
                    last_actual, last_predicted, hit_count, image_prompt
                )
            elif tweet_type == 'analysis':
                article = self._generate_analysis_tweet(
                    title, date_str, target_period, current_prediction,
                    last_actual, last_predicted, hit_count, statistics,
                    ml_models, ml_knowledge, image_prompt
                )
            else:  # detailed
                article = self._generate_detailed_tweet(
                    title, date_str, target_period, current_prediction,
                    last_actual, last_predicted, hit_count, statistics,
                    ml_models, ml_knowledge, image_prompt
                )
            
            # 尝试用DeepSeek优化文章（如果API可用）
            if DEEPSEEK_API_KEY and tweet_type in ['detailed', 'analysis']:
                enhanced_content = self._enhance_with_deepseek(
                    article, ml_knowledge, target_period
                )
                if enhanced_content:
                    article = enhanced_content
            
            response = {
                'status': 'success',
                'article': article,
                'title': title,
                'image_prompt': image_prompt,
                'ml_knowledge': ml_knowledge,
                'hit_count': hit_count,
                'deepseek_enhanced': bool(DEEPSEEK_API_KEY),
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            self._send_json_response(500, {
                'status': 'error',
                'message': str(e)
            })
    
    def _generate_simple_tweet(self, title, date_str, period, prediction, 
                                last_actual, last_predicted, hit_count, image_prompt):
        """生成简洁版推文"""
        front = prediction.get('front', [])
        back = prediction.get('back', [])
        confidence = prediction.get('confidence', 0.75)
        
        front_str = ' '.join(map(lambda x: str(x).zfill(2), front))
        back_str = ' '.join(map(lambda x: str(x).zfill(2), back))
        
        article = f"""# {title}

📅 {date_str}

---

## 🎯 本期预测号码

**前区推荐：** {front_str}

**后区推荐：** {back_str}

**AI置信度：** {confidence*100:.1f}%

---

"""
        
        if last_actual:
            last_front = ' '.join(map(lambda x: str(x).zfill(2), last_actual.get('front', [])))
            last_back = ' '.join(map(lambda x: str(x).zfill(2), last_actual.get('back', [])))
            article += f"""## 📊 上期开奖回顾

**开奖号码：** {last_front} + {last_back}

**命中个数：** {hit_count} 个

---

"""
        
        article += f"""## 🖼️ 本期插图提示词

> {image_prompt}

---

⚠️ **温馨提示：** 预测仅供参考，理性购彩！

*大乐透AI预测系统 | {date_str}*
"""
        
        return article
    
    def _generate_detailed_tweet(self, title, date_str, period, prediction,
                                  last_actual, last_predicted, hit_count, statistics,
                                  ml_models, ml_knowledge, image_prompt):
        """生成详细版推文"""
        front = prediction.get('front', [])
        back = prediction.get('back', [])
        confidence = prediction.get('confidence', 0.75)
        
        front_str = ' '.join(map(lambda x: str(x).zfill(2), front))
        back_str = ' '.join(map(lambda x: str(x).zfill(2), back))
        
        article = f"""# {title}

📅 {date_str} | 大乐透AI预测系统

---

"""
        
        # 上期回顾
        if last_actual:
            article += generate_comparison_analysis(last_actual, last_predicted)
            article += "\n---\n\n"
        
        # 模型调整建议
        article += f"""## 🔧 模型优化方向

基于上期表现，本期我们进行了以下调整：

{generate_model_adjustment(hit_count, ml_models)}

---

## 🎯 第{period}期预测号码

经过四大AI模型的深度分析，本期推荐：

**🔴 前区号码：** {front_str}

**🔵 后区号码：** {back_str}

**📊 综合置信度：** {confidence*100:.1f}%

"""
        
        # 各模型预测详情
        if ml_models:
            article += """
### 各模型预测详情

| 模型 | 前区预测 | 后区预测 | 置信度 |
|:---:|:---:|:---:|:---:|
"""
            for model_name, model_data in ml_models.items():
                m_front = ', '.join(map(str, model_data.get('front', [])))
                m_back = ', '.join(map(str, model_data.get('back', [])))
                m_conf = model_data.get('confidence', 0.75) * 100
                display_name = {
                    'lstm': 'LSTM',
                    'transformer': 'Transformer',
                    'xgboost': 'XGBoost',
                    'random_forest': 'RandomForest'
                }.get(model_name, model_name)
                article += f"| {display_name} | {m_front} | {m_back} | {m_conf:.1f}% |\n"
        
        article += f"""
---

## 🧠 机器学习小课堂

### {ml_knowledge['title']}

{ml_knowledge['content']}

---

## 🖼️ 本期专属插图

**AI绘图提示词：**

> {image_prompt}

---

## ⚠️ 免责声明

本预测基于历史数据分析和机器学习算法，仅供参考娱乐。彩票具有完全随机性，任何预测都不能保证准确。请理性购彩，量力而行。

---

*大乐透AI预测系统 | {date_str}*

*Powered by LSTM + Transformer + XGBoost + RandomForest*
"""
        
        return article
    
    def _generate_analysis_tweet(self, title, date_str, period, prediction,
                                  last_actual, last_predicted, hit_count, statistics,
                                  ml_models, ml_knowledge, image_prompt):
        """生成专业分析版推文"""
        # 先生成详细版，然后添加更多分析内容
        base_article = self._generate_detailed_tweet(
            title, date_str, period, prediction,
            last_actual, last_predicted, hit_count, statistics,
            ml_models, ml_knowledge, image_prompt
        )
        
        # 插入统计分析部分
        stats_section = """
---

## 📈 深度统计分析

### 热门号码追踪

基于近300期数据统计，以下号码出现频率最高：

"""
        
        if statistics:
            front_hot = statistics.get('front_hot', [])
            back_hot = statistics.get('back_hot', [])
            front_cold = statistics.get('front_cold', [])
            
            if front_hot:
                stats_section += "**前区热门：** " + ', '.join([f"{n.get('number', n)}({n.get('count', '?')}次)" if isinstance(n, dict) else str(n) for n in front_hot[:5]]) + "\n\n"
            if back_hot:
                stats_section += "**后区热门：** " + ', '.join([f"{n.get('number', n)}({n.get('count', '?')}次)" if isinstance(n, dict) else str(n) for n in back_hot[:3]]) + "\n\n"
            if front_cold:
                stats_section += "**前区冷门：** " + ', '.join([f"{n.get('number', n)}" if isinstance(n, dict) else str(n) for n in front_cold[:5]]) + "\n\n"
        
        stats_section += """
### 号码分布特征

- **奇偶比例分析**：关注奇偶号码的平衡分布
- **大小号分析**：前区以18为界，后区以6为界
- **连号趋势**：近期连号出现概率分析
- **重号追踪**：上期号码再次出现的可能性

"""
        
        # 在免责声明前插入统计分析
        base_article = base_article.replace("## ⚠️ 免责声明", stats_section + "## ⚠️ 免责声明")
        
        return base_article
    
    def _enhance_with_deepseek(self, article, ml_knowledge, period):
        """使用DeepSeek优化文章"""
        prompt = f"""请帮我优化以下大乐透预测公众号文章，要求：
1. 保持原有结构和数据不变
2. 使用更生动有趣的语言
3. 增加一些过渡语句，让文章更流畅
4. 机器学习小课堂部分可以适当扩展，加入更多通俗易懂的解释
5. 保持Markdown格式
6. 不要改变预测号码和统计数据

原文：
{article}

请输出优化后的完整文章："""
        
        enhanced = call_deepseek_api(prompt, max_tokens=3000)
        return enhanced
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
