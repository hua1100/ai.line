#!/bin/bash

echo "🚀 啟動 AI Messenger Agent..."

# 檢查虛擬環境
if [ ! -d "ai_line_env" ]; then
    echo "❌ 虛擬環境不存在，請先運行 python3 -m venv ai_line_env"
    exit 1
fi

# 激活虛擬環境
source ai_line_env/bin/activate

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，請先設定環境變數"
    exit 1
fi

echo "✅ 環境檢查完成"
echo "🌐 啟動 API 伺服器於 http://localhost:8000"
echo "📋 API 文檔可在 http://localhost:8000/docs 查看"
echo ""
echo "停止伺服器請按 Ctrl+C"
echo ""

# 啟動伺服器
python -m src.api
