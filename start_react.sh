#!/bin/bash
# 启动 React 版海报工具（四步核心流程）
# 后端 API: http://localhost:8000  ·  前端: http://localhost:7100
# Streamlit 原版不受影响，仍可用 streamlit run main.py 启动。
cd "$(dirname "$0")"
.venv/bin/python -m uvicorn api_server:app --reload --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null' EXIT
npm --prefix web run dev -- --port 7100
