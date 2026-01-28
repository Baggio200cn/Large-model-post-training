#!/bin/bash
# 本地开发服务器启动脚本

echo "=========================================="
echo "🚀 启动本地开发服务器"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi

# 设置环境变量（如果需要COS功能）
# export TENCENT_SECRET_ID="your_secret_id"
# export TENCENT_SECRET_KEY="your_secret_key"
# export TENCENT_COS_BUCKET="your_bucket"
# export TENCENT_COS_REGION="ap-guangzhou"

# 启动服务器
cd "$(dirname "$0")"
python3 local_server.py
