#!/bin/bash

# Stop script for Reddit Lead Finder
# Stops both Python backend and React frontend

echo "🛑 Stopping Reddit Lead Finder services..."

# Kill Python backend processes
echo "📡 Stopping Python backend..."
pkill -f "api_server.py" 2>/dev/null && echo "✅ Python backend stopped" || echo "ℹ️  Python backend not running"

# Kill React frontend processes  
echo "🌐 Stopping React frontend..."
pkill -f "tsx.*server/index.ts" 2>/dev/null && echo "✅ React frontend stopped" || echo "ℹ️  React frontend not running"

# Kill any remaining processes on the ports
echo "🔄 Cleaning up ports..."
lsof -ti:6070 | xargs kill -9 2>/dev/null || true  # Backend port
lsof -ti:3050 | xargs kill -9 2>/dev/null || true  # Frontend port

echo ""
echo "✅ All services stopped!"
echo "🚀 To restart:"
echo "   Full startup: ./start-app.sh"
echo "   Quick start:  ./start-simple.sh"