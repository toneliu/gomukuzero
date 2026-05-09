#!/bin/bash

echo "🚀 启动 GomokuZero..."

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🔨 构建前端..."
npm run build

cd ..

echo "🌐 启动后端服务..."
python app/main.py
