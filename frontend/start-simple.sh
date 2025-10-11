#!/bin/bash

# Simple startup script for Reddit Lead Finder
# Just starts the services without all the checks

PROJECT_ROOT="/Users/chrisjohansson/Google Drive/Mild Media/Projekt/Egna Projekt/ongoing/leadreplies"

echo "🚀 Starting Reddit Lead Finder..."

# Kill existing processes
pkill -f "api_server.py" 2>/dev/null || true
pkill -f "tsx.*server/index.ts" 2>/dev/null || true
sleep 2

# Start backend
echo "📡 Starting backend..."
cd "$PROJECT_ROOT/server"
python3 api_server.py > api_server.log 2>&1 &
echo "Backend started (PID: $!)"

# Wait a moment
sleep 5

# Start frontend
echo "🌐 Starting frontend..."
cd "$PROJECT_ROOT/frontend"
PORT=3050 npm run dev > frontend.log 2>&1 &
echo "Frontend started (PID: $!)"

# Wait a moment
sleep 5

echo ""
echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3050"
echo "📡 Backend:  http://localhost:6070"
echo ""
echo "📋 Check status: python3 $PROJECT_ROOT/check_status.py"