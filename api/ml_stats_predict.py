# api/ml_stats_predict.py
"""
融合机器学习与统计建模预测API
- 支持ML模型（如LSTM/Transformer/XGBoost）
- 支持统计模型（如OLS/GLM/ARIMA，基于statsmodels）
- 统一输入/输出格式，便于前端和融合模块调用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import traceback
import numpy as np
import pandas as pd
from utils.data_pipeline import DataPipeline

# 可选：导入sklearn、xgboost、keras、statsmodels等
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from tensorflow.keras.models import load_model
import statsmodels.api as sm

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    csv_path: str = 'data/processed_samlpe.csv'
    target_col: str = None
    model_type: str = 'rf'  # 'rf', 'xgb', 'lstm', 'transformer'

@app.post("/ml-stats-predict")
async def ml_stats_predict(req: PredictRequest):
    try:
        # 1. 数据加载与预处理
        pipeline = DataPipeline(req.csv_path, req.target_col)
        pipeline.load_data()
        pipeline.preprocess()
        pipeline.feature_engineering()
        X, y = pipeline.split_X_y()
        pipeline.scale_features()
        pipeline.encode_categorical()

        # 2. 机器学习模型选择
        model = None
        if req.model_type == 'rf':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif req.model_type == 'xgb':
            model = XGBRegressor(n_estimators=100, random_state=42)
        elif req.model_type == 'lstm':
            model = load_model('models/lstm_model')
        elif req.model_type == 'transformer':
            model = load_model('models/transformer_model')
        else:
            return {'status': 'error', 'message': 'Unknown model type'}

        # 3. 模型训练与预测
        pred = None
        if req.model_type in ['lstm', 'transformer']:
            X_input = np.array(X)
            pred = model.predict(X_input)
        else:
            model.fit(X, y)
            pred = model.predict(X)

        # 4. 统一输出
        response = {
            'status': 'success',
            'prediction': pred.tolist(),
            'model_type': req.model_type,
            'timestamp': datetime.now().isoformat()
        }
        return response
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}
