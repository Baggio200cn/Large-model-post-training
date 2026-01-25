#!/bin/bash
# 更新文档中的Vercel域名占位符

set -e

# 检查.vercel-domain文件是否存在
if [ ! -f ".vercel-domain" ]; then
    echo "错误: 找不到 .vercel-domain 文件"
    echo "请先创建该文件并填入您的实际Vercel域名"
    exit 1
fi

# 读取实际域名
VERCEL_DOMAIN=$(grep "^VERCEL_DOMAIN=" .vercel-domain | cut -d'=' -f2)

# 验证域名不为空且不是占位符
if [ -z "$VERCEL_DOMAIN" ] || [[ "$VERCEL_DOMAIN" == *"your-actual-domain"* ]]; then
    echo "错误: 请先在 .vercel-domain 文件中填入您的实际Vercel域名"
    echo ""
    echo "步骤："
    echo "1. 登录 https://vercel.com/dashboard"
    echo "2. 找到项目 'Large-model-post-training'"
    echo "3. 复制实际域名（例如：large-model-post-training-abc123.vercel.app）"
    echo "4. 编辑 .vercel-domain 文件，替换 VERCEL_DOMAIN 的值"
    echo "5. 重新运行此脚本"
    exit 1
fi

echo "正在更新文档中的域名为: $VERCEL_DOMAIN"
echo ""

# 备份原文件
echo "备份原文件..."
cp DEPLOYMENT.md DEPLOYMENT.md.backup
cp docs/AUTO_TRAINING.md docs/AUTO_TRAINING.md.backup

# 替换所有占位符域名
echo "更新 DEPLOYMENT.md..."
sed -i "s|your-project\.vercel\.app|$VERCEL_DOMAIN|g" DEPLOYMENT.md
sed -i "s|your-domain\.vercel\.app|$VERCEL_DOMAIN|g" DEPLOYMENT.md

echo "更新 docs/AUTO_TRAINING.md..."
sed -i "s|your-domain\.com|$VERCEL_DOMAIN|g" docs/AUTO_TRAINING.md

echo ""
echo "✅ 更新完成！"
echo ""
echo "已更新的文件："
echo "  - DEPLOYMENT.md"
echo "  - docs/AUTO_TRAINING.md"
echo ""
echo "备份文件："
echo "  - DEPLOYMENT.md.backup"
echo "  - docs/AUTO_TRAINING.md.backup"
echo ""
echo "下一步："
echo "  git add DEPLOYMENT.md docs/AUTO_TRAINING.md"
echo "  git commit -m \"docs: 更新Vercel域名为实际地址\""
echo "  git push"
