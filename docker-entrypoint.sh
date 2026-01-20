#!/bin/bash
# Entrypoint script to run both FastAPI backend and Streamlit frontend

set -e

echo "🚀 Starting FastAPI backend on port 8000..."
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Wait a moment for backend to start
sleep 2

echo "🚀 Starting Streamlit frontend on port 8501..."
echo "👉 From your browser, open:"
echo "   - Frontend: http://localhost:8501"
echo "   - API docs: http://localhost:8000/docs"
uv run streamlit run src/frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
