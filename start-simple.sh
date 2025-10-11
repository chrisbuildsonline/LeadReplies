#!/bin/bash

# Simple startup script for Reddit Lead Finder
# Starts both Python backend (server/) and React frontend (frontend/) in parallel

PROJECT_ROOT="$(pwd)"
SERVER_DIR="$PROJECT_ROOT/server"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🚀 Starting Reddit Lead Finder..."
echo "📁 Server: $SERVER_DIR"
echo "📁 Frontend: $FRONTEND_DIR"

# Kill existing processes
echo "🔄 Stopping existing services..."
pkill -f "api_server.py" 2>/dev/null || true
pkill -f "tsx.*server/index.ts" 2>/dev/null || true
lsof -ti:6070 | xargs kill -9 2>/dev/null || true
lsof -ti:3050 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Python backend
echo "📡 Starting Python backend..."
cd "$SERVER_DIR"
python3 api_server.py > api_server.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Start React frontend
echo "🌐 Starting React frontend..."
cd "$FRONTEND_DIR"
PORT=3050 npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

echo ""
echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3050"
echo "📡 Backend:  http://localhost:6070"
echo ""
echo "📊 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📋 Management:"
echo "   Stop all: kill $BACKEND_PID $FRONTEND_PID"
echo "   Or use:   ./stop-app.sh"
echo ""
echo "🚀 Visit http://localhost:3050/reddit-leads to see your leads!"