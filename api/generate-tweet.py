# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import random
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

ML_TIPS = [
    {'title': 'LSTM', 'desc': 'LSTM is a recurrent neural network that learns long-term dependencies through gate mechanisms.'},
    {'title': 'Transformer', 'desc': 'Transformer uses self-attention to find correlations between different numbers.'},
    {'title': 'XGBoost', 'desc': 'XGBoost is a gradient boosting algorithm that corrects errors by adding decision trees.'},
    {'title': 'RandomForest', 'desc': 'Random Forest uses multiple decision trees voting to make robust predictions.'},
    {'title': 'Feature Engineering', 'desc': 'Feature engineering transforms raw data into valuable features like hot/cold numbers.'},
    {'title': 'Ensemble Learning', 'desc': 'Combining multiple models often achieves better results than any single model.'},
]

ML_TIPS_CN = [
    {'title': 'LSTM', 'content': 'LSTM(长短期记忆网络)通过门控机制学习序列数据的长期依赖关系，特别适合分析号码的时序规律。'},
    {'title': 'Transformer', 'content': 'Transformer使用自注意力机制发现不同号码之间的关联性，能够捕捉到一些号码经常一起出现的规律。'},
    {'title': 'XGBoost', 'content': 'XGBoost是一种梯度提升算法，通过逐步添加决策树来纠正预测错误，处理各种统计特征效果出色。'},
    {'title': 'RandomForest', 'content': '随机森林由多棵决策树投票决定结果，这种集体智慧能有效降低单一模型的过拟合风险。'},
    {'title': 'Feature Engineering', 'content': '特征工程是将原始数据转换为有价值特征的过程，包括热门号码、冷门号码、遗漏期数等。'},
    {'title': 'Ensemble', 'content': '模型集成将多个模型组合起来，取长补短，往往比单一模型获得更稳定的预测效果。'},
]


def call_deepseek(prompt):
    if not DEEPSEEK_API_KEY:
        return None
    try:
        import urllib.request
        url = 'https://api.deepseek.com/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + DEEPSEEK_API_KEY
        }
        body = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': 'You are a professional science writer. Write in Chinese. Use Markdown format.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        req = urllib.request.Request(url, json.dumps(body).encode('utf-8'), headers, method='POST')
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return text if text and len(text) > 100 else None
    except:
        return None


def fmt(nums):
    if not nums:
        return '--'
    return ' '.join([str(n).zfill(2) for n in nums])


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        result = {'status': 'error'}
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8')) if length > 0 else {}
            
            ttype = body.get('type', 'detailed')
            pred = body.get('prediction') or {}
            last_act = body.get('last_actual') or {}
            last_pred = body.get('last_predicted') or {}
            models = body.get('ml_models') or {}
            period = str(body.get('target_period', '25142'))
            
            front = pred.get('front') or []
            back = pred.get('back') or []
            conf = pred.get('confidence') or 0.75
            
            hits = 0
            fhits, bhits = [], []
            if last_act and last_pred:
                af = set(last_act.get('front') or [])
                ab = set(last_act.get('back') or [])
                pf = set(last_pred.get('front') or [])
                pb = set(last_pred.get('back') or [])
                fhits = sorted(af & pf)
                bhits = sorted(ab & pb)
                hits = len(fhits) + len(bhits)
            
            tip = random.choice(ML_TIPS_CN)
            date = datetime.now().strftime('%Y-%m-%d')
            
            if hits >= 4:
                title = '🎯 第' + period + '期：上期命中' + str(hits) + '个，状态火热！'
            elif hits >= 2:
                title = '📊 第' + period + '期：数据揭示新趋势'
            else:
                title = '🤖 第' + period + '期：模型优化后重新出发'
            
            seed = int(period) % 5
            imgs = [
                '数字' + period[-2:] + '在星空中闪耀，AI神经网络环绕，紫蓝色调，科幻风格',
                '水晶球显示第' + period + '期预测，全息图表，赛博朋克风格',
                'AI机器人分析数据，屏幕显示' + period + '，数据矩阵背景',
                '神经网络3D可视化，节点闪烁' + period + '，霓虹色彩',
                '四种AI模型融合成能量球，奇幻科技风格'
            ]
            img = imgs[seed]
            
            art = '# ' + title + '\n\n'
            art += '📅 ' + date + '\n\n---\n\n'
            
            if last_act:
                lf = last_act.get('front') or []
                lb = last_act.get('back') or []
                art += '## 📊 上期回顾\n\n'
                art += '**开奖：** ' + fmt(lf) + ' + ' + fmt(lb) + '\n\n'
                if last_pred:
                    lpf = last_pred.get('front') or []
                    lpb = last_pred.get('back') or []
                    art += '**预测：** ' + fmt(lpf) + ' + ' + fmt(lpb) + '\n\n'
                    art += '**命中：** 前区' + str(len(fhits)) + '个'
                    if fhits:
                        art += '(' + ','.join(map(str, fhits)) + ')'
                    art += '，后区' + str(len(bhits)) + '个'
                    if bhits:
                        art += '(' + ','.join(map(str, bhits)) + ')'
                    art += '\n\n'
                    if hits >= 3:
                        art += '🎉 表现不错！\n\n'
                    else:
                        art += '🔧 本期调整Transformer权重\n\n'
            
            art += '---\n\n## 🎯 第' + period + '期预测\n\n'
            art += '**🔴 前区：** ' + fmt(front) + '\n\n'
            art += '**🔵 后区：** ' + fmt(back) + '\n\n'
            art += '**📊 置信度：** ' + str(round(conf * 100, 1)) + '%\n\n'
            
            if ttype != 'simple' and models:
                art += '---\n\n## 🤖 模型详情\n\n'
                art += '| 模型 | 前区 | 后区 | 置信度 |\n|:---:|:---:|:---:|:---:|\n'
                for k, n in [('lstm', 'LSTM'), ('transformer', 'Transformer'), ('xgboost', 'XGBoost'), ('random_forest', 'RF')]:
                    if k in models:
                        m = models[k]
                        mf = ','.join(map(str, m.get('front') or [])) or '--'
                        mb = ','.join(map(str, m.get('back') or [])) or '--'
                        mc = str(round((m.get('confidence') or 0.75) * 100, 1)) + '%'
                        art += '| ' + n + ' | ' + mf + ' | ' + mb + ' | ' + mc + ' |\n'
                art += '\n'
            
            art += '---\n\n## 🧠 ML小课堂：' + tip['title'] + '\n\n'
            art += tip['content'] + '\n\n'
            art += '---\n\n## 🖼️ 插图提示词\n\n> ' + img + '\n\n'
            art += '---\n\n⚠️ 仅供参考，理性购彩\n\n*AI预测系统 | ' + date + '*\n'
            
            ds_used = False
            if DEEPSEEK_API_KEY and ttype != 'simple':
                try:
                    p = '请优化这篇大乐透预测文章：\n1.保持号码不变\n2.语言更生动\n3.扩展ML小课堂\n4.Markdown格式\n5.1500字内\n\n' + art
                    enhanced = call_deepseek(p)
                    if enhanced:
                        art = enhanced
                        ds_used = True
                except:
                    pass
            
            result = {
                'status': 'success',
                'article': art,
                'title': title,
                'image_prompt': img,
                'ml_knowledge': tip,
                'hit_count': hits,
                'deepseek_enhanced': ds_used,
                'deepseek_configured': bool(DEEPSEEK_API_KEY)
            }
        except Exception as e:
            result = {'status': 'error', 'message': str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        r = {'status': 'success', 'api': 'generate-tweet', 'deepseek': bool(DEEPSEEK_API_KEY)}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(r).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
