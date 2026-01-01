from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import hashlib
import json
import traceback

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 简单内存用户表（生产建议用数据库）
USERS = {
    'admin': 'admin123',
}
# 简单token机制（生产建议用JWT）
TOKENS = {}

# 手动维护开奖号码数据（可持久化到文件/数据库）
MANUAL_RESULTS = []  # [{period, draw_date, front_zone, back_zone, note, created_at}]


class LoginRequest(BaseModel):
    username: str
    password: str

class ManualResult(BaseModel):
    period: str
    draw_date: str
    front_zone: list
    back_zone: list
    note: str = ''


@app.post("/admin/login")
async def admin_login(req: LoginRequest):
    if req.username in USERS and req.password == USERS[req.username]:
        token = f"token-{req.username}-{datetime.now().timestamp()}"
        TOKENS[token] = req.username
        return { 'status': 'success', 'token': token }
    else:
        return { 'status': 'error', 'message': '用户名或密码错误' }


@app.get("/admin/info")
async def admin_info(request: Request):
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '')
    username = TOKENS.get(token)
    if username:
        return { 'status': 'success', 'user': username, 'role': 'admin', 'time': datetime.now().isoformat() }
    else:
        return { 'status': 'error', 'message': '未授权' }

# 新增：手动上传开奖号码
@app.post("/admin/manual-result")
async def add_manual_result(req: ManualResult, request: Request):
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '')
    username = TOKENS.get(token)
    if not username:
        return { 'status': 'error', 'message': '未授权' }
    entry = req.dict()
    entry['created_at'] = datetime.now().isoformat()
    MANUAL_RESULTS.append(entry)
    return { 'status': 'success', 'message': '开奖号码已添加', 'data': entry }

# 新增：获取所有手动上传的开奖号码
@app.get("/admin/manual-results")
async def get_manual_results(request: Request):
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '')
    username = TOKENS.get(token)
    if not username:
        return { 'status': 'error', 'message': '未授权' }
    return { 'status': 'success', 'results': MANUAL_RESULTS }
