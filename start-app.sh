#!/bin/bash

echo "🚀 Reddit Lead Finder (Multi-tenant) - Complete System"
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
if lsof -Pi :6070 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 6070 is already in use. Stopping existing process..."
    kill $(lsof -t -i:6070) 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :3050 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3050 is already in use. Stopping existing process..."
    kill $(lsof -t -i:3050) 2>/dev/null || true
    sleep 2
fi

# Setup backend
echo "🐍 Setting up backend..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r server/requirements.txt

# Run setup
echo "🔧 Running database setup..."
python3 server/setup.py

# Start backend API server
echo "🚀 Starting API server..."
python3 server/api_server.py &
BACKEND_PID=$!

# Start background service for hourly lead scraping
echo "⏰ Starting background service (hourly lead scraping)..."
python3 server/background_service.py &
BACKGROUND_PID=$!

# Setup frontend
echo "🌐 Setting up frontend..."

# Install npm dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    cd frontend && npm install && cd ..
fi

# Start frontend (includes its own server)
echo "🚀 Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for servers to start
sleep 3

echo ""
echo "✅ Reddit Lead Finder is now running!"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3050"
echo "🔧 API Server: http://localhost:6070"
echo "📚 API Docs: http://localhost:6070/docs"
echo "⏰ Background Service: Running (fetches leads every hour)"
echo ""
echo "🔐 Authentication: Powered by Supabase"
echo "   Create an account or login at the frontend URL above"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKGROUND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait