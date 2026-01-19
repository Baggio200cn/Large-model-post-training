# Windows PowerShell 上传脚本
# 使用方法: .\upload_all.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 上传数据和模型到腾讯云COS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查环境变量
if (-not $env:TENCENT_SECRET_ID) {
    Write-Host "❌ 错误: 未设置 TENCENT_SECRET_ID" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先设置环境变量：" -ForegroundColor Yellow
    Write-Host '  $env:TENCENT_SECRET_ID="你的SecretId"' -ForegroundColor Yellow
    Write-Host '  $env:TENCENT_SECRET_KEY="你的SecretKey"' -ForegroundColor Yellow
    Write-Host '  $env:TENCENT_COS_BUCKET="你的存储桶名称"' -ForegroundColor Yellow
    Write-Host '  $env:TENCENT_COS_REGION="ap-guangzhou"' -ForegroundColor Yellow
    exit 1
}

if (-not $env:TENCENT_SECRET_KEY) {
    Write-Host "❌ 错误: 未设置 TENCENT_SECRET_KEY" -ForegroundColor Red
    exit 1
}

if (-not $env:TENCENT_COS_BUCKET) {
    Write-Host "❌ 错误: 未设置 TENCENT_COS_BUCKET" -ForegroundColor Red
    exit 1
}

Write-Host "📋 配置信息：" -ForegroundColor Green
Write-Host "  存储桶: $env:TENCENT_COS_BUCKET"
if ($env:TENCENT_COS_REGION) {
    Write-Host "  区域: $env:TENCENT_COS_REGION"
} else {
    Write-Host "  区域: ap-guangzhou (默认)"
}
Write-Host ""

# 1. 检查依赖
Write-Host "📦 检查依赖..." -ForegroundColor Yellow
pip show cos-python-sdk-v5 > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "正在安装 cos-python-sdk-v5..."
    pip install cos-python-sdk-v5 -q
}

# 2. 执行上传
Write-Host ""
Write-Host "📤 开始上传..." -ForegroundColor Yellow
python scripts\upload_to_cos.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 上传完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 上传失败，请检查错误信息" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
