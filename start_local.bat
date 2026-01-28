@echo off
REM 本地开发服务器启动脚本 (Windows)

echo ==========================================
echo 🚀 启动本地开发服务器
echo ==========================================

REM 设置环境变量（如果需要COS功能）
REM set TENCENT_SECRET_ID=your_secret_id
REM set TENCENT_SECRET_KEY=your_secret_key
REM set TENCENT_COS_BUCKET=your_bucket
REM set TENCENT_COS_REGION=ap-guangzhou

REM 启动服务器
cd /d "%~dp0"
python local_server.py

pause
