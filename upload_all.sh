#!/bin/bash

# 腾讯云COS上传脚本
# 使用方法: ./upload_all.sh

echo "========================================"
echo "🚀 上传数据和模型到腾讯云COS"
echo "========================================"

# 检查环境变量
if [ -z "$TENCENT_SECRET_ID" ]; then
    echo "❌ 错误: 未设置 TENCENT_SECRET_ID"
    echo ""
    echo "请先设置环境变量："
    echo "  export TENCENT_SECRET_ID=你的SecretId"
    echo "  export TENCENT_SECRET_KEY=你的SecretKey"
    echo "  export TENCENT_COS_BUCKET=你的存储桶名称"
    echo "  export TENCENT_COS_REGION=ap-guangzhou"
    exit 1
fi

if [ -z "$TENCENT_SECRET_KEY" ]; then
    echo "❌ 错误: 未设置 TENCENT_SECRET_KEY"
    exit 1
fi

if [ -z "$TENCENT_COS_BUCKET" ]; then
    echo "❌ 错误: 未设置 TENCENT_COS_BUCKET"
    exit 1
fi

echo ""
echo "📋 配置信息："
echo "  存储桶: $TENCENT_COS_BUCKET"
echo "  区域: ${TENCENT_COS_REGION:-ap-guangzhou}"
echo ""

# 1. 安装依赖（如果还没有）
echo "📦 检查依赖..."
pip show cos-python-sdk-v5 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装 cos-python-sdk-v5..."
    pip install cos-python-sdk-v5 -q
fi

# 2. 执行上传
echo ""
echo "📤 开始上传..."
python scripts/upload_to_cos.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 上传完成！"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ 上传失败，请检查错误信息"
    echo "========================================"
    exit 1
fi
