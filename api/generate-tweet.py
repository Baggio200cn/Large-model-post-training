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

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

# ML小知识库 - 使用单引号避免中文引号冲突
ML_KNOWLEDGE = [
    {'title': '什么是LSTM？', 'content': 'LSTM(长短期记忆网络)是一种特殊的循环神经网络，能够学习长期依赖关系。它通过门控机制控制信息的流动，特别适合处理时间序列数据。'},
    {'title': 'Transformer的注意力机制', 'content': 'Transformer模型的核心是自注意力机制，它能够让模型关注输入序列中不同位置的信息，帮助发现不同号码之间的关联性。'},
    {'title': 'XGBoost的梯度提升', 'content': 'XGBoost是一种强大的集成学习算法，通过逐步添加决策树来纠正前面模型的错误，能够处理各种统计特征。'},
    {'title': '随机森林的投票机制', 'content': '随机森林由多棵决策树组成，每棵树独立预测，最终通过投票确定结果，这种群体智慧能有效降低过拟合风险。'},
    {'title': '特征工程的重要性', 'content': '特征工程是将原始数据转换为更有价值信息的过程，包括热门号码、冷门号码、遗漏期数等特征。'},
    {'title': '模型集成的威力', 'content': '单个模型都有局限性，但将多个模型组合起来往往能获得更好的效果，取长补短，提高预测的稳定性。'},
    {'title': '置信度是什么？', 'content': '置信度表示模型对自己预测结果的信心程度，但彩票本质上是随机的，置信度只能作为参考。'},
    {'title': '什么是过拟合？', 'content': '过拟合是模型记住了训练数据的噪声而非真正规律的现象，我们通过交叉验证等技术防止过拟合。'},
    {'title': '时间序列分析', 'content': '彩票号码可以看作时间序列数据，时间序列分析寻找数据中的趋势和周期性模式。'},
    {'title': '概率与随机性', 'content': '彩票本质上是一个概率游戏，AI预测并不能改变这个事实，但可以帮助分析历史数据中的统计特征。'}
]


def call_deepseek(prompt):
    """调用DeepSeek API生成内容"""
    if not DEEPSEEK_API_KEY:
        return None
    
    try:
        import urllib.request
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + DEEPSEEK_API_KEY
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一位专业的科普作家，擅长用通俗易懂、生动有趣的语言解释机器学习概念。请用中文Markdown格式输出。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        req = urllib.request.Request(
            'https://api.deepseek.com/v1/chat/completions',
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content and len(content) > 200:
                return content
        return None
    except Exception as e:
        print('DeepSeek error: ' + str(e))
        return None


def safe_get(d, key, default=None):
    """安全获取字典值"""
    if d is None:
        return default
    return d.get(key, default) if isinstance(d, dict) else default


def format_nums(nums):
    """格式化号码列表"""
    if not nums:
        return '--'
    return ' '.join([str(n).zfill(2) for n in nums])


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        response_data = {'status': 'error', 'message': 'Unknown error'}
        
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            
            # 安全获取参数
            tweet_type = safe_get(request_data, 'type', 'detailed')
            prediction = safe_get(request_data, 'prediction', {}) or {}
            last_actual = safe_get(request_data, 'last_actual', {}) or {}
            last_predicted = safe_get(request_data, 'last_predicted', {}) or {}
            ml_models = safe_get(request_data, 'ml_models', {}) or {}
            target_period = str(safe_get(request_data, 'target_period', '25142'))
            
            # 获取预测号码
            front = safe_get(prediction, 'front', []) or []
            back = safe_get(prediction, 'back', []) or []
            confidence = safe_get(prediction, 'confidence', 0.75) or 0.75
            
            # 计算命中数
            hit_count = 0
            front_hits = []
            back_hits = []
            
            if last_actual and last_predicted:
                actual_front = set(safe_get(last_actual, 'front', []) or [])
                actual_back = set(safe_get(last_actual, 'back', []) or [])
                pred_front = set(safe_get(last_predicted, 'front', []) or [])
                pred_back = set(safe_get(last_predicted, 'back', []) or [])
                front_hits = sorted(list(actual_front & pred_front))
                back_hits = sorted(list(actual_back & pred_back))
                hit_count = len(front_hits) + len(back_hits)
            
            # 随机选择ML知识
            ml_knowledge = random.choice(ML_KNOWLEDGE)
            
            # 生成动态标题
            if hit_count >= 4:
                title = '🎯 第' + target_period + '期预测：上期命中' + str(hit_count) + '个，AI状态火热！'
            elif hit_count >= 2:
                title = '📊 第' + target_period + '期预测：数据揭示新趋势'
            else:
                title = '🤖 第' + target_period + '期预测：模型优化后重新出发'
            
            # 生成插图提示词
            seed = int(target_period) % 7
            prompts = [
                '数字' + target_period[-2:] + '在宇宙星空中闪耀，周围环绕着数据流和AI神经网络，紫蓝色调，科幻艺术风格',
                '未来感水晶球显示第' + target_period + '期预测，全息投影统计图表，赛博朋克风格',
                'AI机器人分析彩票数据，屏幕显示期号' + target_period + '，流动数据矩阵背景',
                '量子计算机运算，粒子组成数字' + target_period[-2:] + '形状，梦幻紫色和金色',
                '神经网络三维可视化，节点闪烁第' + target_period + '期关键数字，霓虹色彩',
                '四个AI模型化身为四种元素融合成预测能量，奇幻科技风格',
                '深度学习抽象表达，层层神经元如城市夜景，第' + target_period + '期数字在顶层闪耀'
            ]
            image_prompt = prompts[seed]
            
            # 日期
            date_str = datetime.now().strftime('%Y年%m月%d日')
            
            # 构建文章
            article = '# ' + title + '\n\n'
            article += '📅 ' + date_str + ' | 大乐透AI预测系统\n\n---\n\n'
            
            # 上期回顾
            if last_actual:
                last_front = safe_get(last_actual, 'front', []) or []
                last_back = safe_get(last_actual, 'back', []) or []
                
                article += '## 📊 上期开奖回顾\n\n'
                article += '**开奖号码：** ' + format_nums(last_front) + ' + ' + format_nums(last_back) + '\n\n'
                
                if last_predicted:
                    pred_front_list = safe_get(last_predicted, 'front', []) or []
                    pred_back_list = safe_get(last_predicted, 'back', []) or []
                    
                    article += '**上期AI预测：** ' + format_nums(pred_front_list) + ' + ' + format_nums(pred_back_list) + '\n\n'
                    article += '**命中情况：** \n'
                    article += '- 前区命中 ' + str(len(front_hits)) + ' 个'
                    if front_hits:
                        article += '：' + ', '.join([str(n) for n in front_hits])
                    article += '\n'
                    article += '- 后区命中 ' + str(len(back_hits)) + ' 个'
                    if back_hits:
                        article += '：' + ', '.join([str(n) for n in back_hits])
                    article += '\n\n'
                    
                    if hit_count >= 3:
                        article += '🎉 **表现不错！** 模型状态良好，继续保持！\n\n'
                    else:
                        article += '🔧 **模型调优：** 本期将调整Transformer权重，加强号码关联性分析。\n\n'
            
            # 本期预测
            article += '---\n\n'
            article += '## 🎯 第' + target_period + '期预测号码\n\n'
            article += '**🔴 前区推荐：** ' + format_nums(front) + '\n\n'
            article += '**🔵 后区推荐：** ' + format_nums(back) + '\n\n'
            article += '**📊 综合置信度：** ' + str(round(confidence * 100, 1)) + '%\n\n'
            
            # 模型详情
            if tweet_type != 'simple' and ml_models:
                article += '---\n\n'
                article += '## 🤖 各模型预测详情\n\n'
                article += '| 模型 | 前区预测 | 后区预测 | 置信度 |\n'
                article += '|:---:|:---:|:---:|:---:|\n'
                
                model_names = [('lstm', 'LSTM'), ('transformer', 'Transformer'), 
                              ('xgboost', 'XGBoost'), ('random_forest', 'RandomForest')]
                
                for key, name in model_names:
                    if key in ml_models:
                        m = ml_models[key]
                        m_front = ', '.join([str(x) for x in safe_get(m, 'front', []) or []])
                        m_back = ', '.join([str(x) for x in safe_get(m, 'back', []) or []])
                        m_conf = safe_get(m, 'confidence', 0.75) or 0.75
                        article += '| ' + name + ' | ' + (m_front or '--') + ' | ' + (m_back or '--') + ' | ' + str(round(m_conf * 100, 1)) + '% |\n'
                
                article += '\n'
            
            # ML小知识
            article += '---\n\n'
            article += '## 🧠 机器学习小课堂\n\n'
            article += '### ' + ml_knowledge['title'] + '\n\n'
            article += ml_knowledge['content'] + '\n\n'
            
            # 插图提示词
            article += '---\n\n'
            article += '## 🖼️ 本期专属插图提示词\n\n'
            article += '> ' + image_prompt + '\n\n'
            
            # 免责声明
            article += '---\n\n'
            article += '## ⚠️ 免责声明\n\n'
            article += '本预测基于历史数据分析和机器学习算法，仅供参考娱乐。彩票具有完全随机性，任何预测都不能保证准确。请理性购彩，量力而行。\n\n'
            article += '---\n\n'
            article += '*大乐透AI预测系统 | ' + date_str + '*\n'
            
            # DeepSeek优化
            deepseek_used = False
            if DEEPSEEK_API_KEY and tweet_type != 'simple':
                try:
                    prompt = '请优化以下大乐透预测文章，要求：\n'
                    prompt += '1. 保持所有号码和数据不变\n'
                    prompt += '2. 使用更生动有趣的语言\n'
                    prompt += '3. 扩展ML小课堂部分，用通俗比喻解释\n'
                    prompt += '4. 保持Markdown格式\n'
                    prompt += '5. 字数控制在1500字以内\n\n'
                    prompt += '原文：\n' + article
                    
                    enhanced = call_deepseek(prompt)
                    if enhanced:
                        article = enhanced
                        deepseek_used = True
                except Exception as e:
                    print('DeepSeek enhancement failed: ' + str(e))
            
            response_data = {
                'status': 'success',
                'article': article,
                'title': title,
                'image_prompt': image_prompt,
                'ml_knowledge': ml_knowledge,
                'hit_count': hit_count,
                'deepseek_enhanced': deepseek_used,
                'deepseek_configured': bool(DEEPSEEK_API_KEY),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            response_data = {
                'status': 'error',
                'message': str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        response_data = {
            'status': 'success',
            'message': '公众号推文生成API',
            'deepseek_configured': bool(DEEPSEEK_API_KEY),
            'usage': 'POST请求生成推文'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
