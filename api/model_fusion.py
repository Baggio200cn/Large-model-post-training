# api/model_fusion.py
"""
模型融合API
- 支持多模型（ML/统计/启发式）融合预测
- 可扩展集成策略（加权平均、投票、stacking等）
- 统一输入/输出，便于前端和自动化调用
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import numpy as np
from utils.data_pipeline import DataPipeline
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FusionRequest(BaseModel):
    csv_path: str = 'data/processed_samlpe.csv'
    target_col: str = None

@app.post("/model-fusion")
async def model_fusion(req: FusionRequest):
    try:
        pipeline = DataPipeline(req.csv_path, req.target_col)
        pipeline.load_data()
        pipeline.preprocess()
        pipeline.feature_engineering()
        X, y = pipeline.split_X_y()
        pipeline.scale_features()
        pipeline.encode_categorical()
        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(X, y)
        rf_pred = rf.predict(X)
        X_const = sm.add_constant(X)
        ols = sm.OLS(y, X_const).fit()
        ols_pred = ols.predict(X_const)
        fusion_pred = 0.6 * rf_pred + 0.4 * ols_pred
        response = {
            'status': 'success',
            'fusion_prediction': fusion_pred.tolist(),
            'rf_prediction': rf_pred.tolist(),
            'ols_prediction': ols_pred.tolist(),
            'fusion_strategy': '0.6*RF + 0.4*OLS',
            'timestamp': datetime.now().isoformat()
        }
        return response
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
