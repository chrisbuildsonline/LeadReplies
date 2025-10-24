#!/bin/bash

echo "🚀 LeadReplier - Complete System Startup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "server/api_server.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Node.js/npm is required but not installed"
    exit 1
fi

# Check if ports are available
echo "🔍 Checking port availability..."
if lsof -Pi :6070 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 6070 is already in use. Stopping existing process..."
    kill $(lsof -t -i:6070) 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :3050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 3050 is already in use. Stopping existing process..."
    kill $(lsof -t -i:3050) 2>/dev/null || true
    sleep 2
fi

# Setup backend
echo "🐍 Setting up backend..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r server/requirements.txt

# Start backend API server using the new start-app.py
echo "� RStarting API server..."
cd server
python3 start-app.py &
BACKEND_PID=$!
cd ..

# Start background service for hourly lead scraping (optional)
if [ -f "server/background_service.py" ]; then
    echo "⏰ Starting background service (hourly lead scraping)..."
    python3 server/background_service.py &
    BACKGROUND_PID=$!
else
    echo "ℹ️  Background service not found, skipping..."
    BACKGROUND_PID=""
fi

# Setup frontend
echo "🌐 Setting up frontend..."

# Install npm dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend (includes its own server)
echo "🚀 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for servers to start
echo "⏳ Waiting for servers to initialize..."
sleep 5

# Check if servers started successfully
echo "🔍 Checking server status..."

# Check backend
if curl -s http://localhost:6070 > /dev/null 2>&1; then
    echo "✅ Backend API server is running on port 6070"
else
    echo "❌ Backend API server failed to start"
fi

# Check frontend
if curl -s http://localhost:3050 > /dev/null 2>&1; then
    echo "✅ Frontend server is running on port 3050"
else
    echo "❌ Frontend server failed to start"
fi

echo ""
echo "✅ LeadReplier is now running!"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3050"
echo "🔧 API Server: http://localhost:6070"
echo "📚 API Docs: http://localhost:6070/docs"
if [ -n "$BACKGROUND_PID" ]; then
    echo "⏰ Background Service: Running (fetches leads every hour)"
fi
echo ""
echo "🔐 Authentication: Powered by Supabase"
echo "   Create an account or login at the frontend URL above"
echo ""
echo "📖 API Documentation: http://localhost:3050/api"
echo "💰 API Pricing: http://localhost:3050/api/pricing"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ -n "$BACKGROUND_PID" ]; then
        kill $BACKGROUND_PID 2>/dev/null || true
    fi
    
    # Also kill any remaining processes on these ports
    kill $(lsof -t -i:6070) 2>/dev/null || true
    kill $(lsof -t -i:3050) 2>/dev/null || true
    
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait