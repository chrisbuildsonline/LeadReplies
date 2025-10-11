#!/bin/bash

# Stop script for Reddit Lead Finder

echo "🛑 Stopping Reddit Lead Finder services..."

# Kill backend processes
echo "📡 Stopping backend..."
pkill -f "api_server.py" 2>/dev/null && echo "✅ Backend stopped" || echo "ℹ️  Backend not running"

# Kill frontend processes  
echo "🌐 Stopping frontend..."
pkill -f "tsx.*server/index.ts" 2>/dev/null && echo "✅ Frontend stopped" || echo "ℹ️  Frontend not running"

# Kill any remaining processes on the ports
echo "🔄 Cleaning up ports..."
lsof -ti:6070 | xargs kill -9 2>/dev/null || true
lsof -ti:3050 | xargs kill -9 2>/dev/null || true

echo ""
echo "✅ All services stopped!"
echo "🚀 To restart: ./start-app.sh or ./start-simple.sh"