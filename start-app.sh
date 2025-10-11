#!/bin/bash

# Reddit Lead Finder - Complete Startup Script
# This script starts both Python backend (server/) and React frontend (frontend/) in parallel

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory (current directory)
PROJECT_ROOT="$(pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SERVER_DIR="$PROJECT_ROOT/server"

echo -e "${BLUE}🚀 Reddit Lead Finder - Starting Complete System${NC}"
echo "=================================================================="
echo "📁 Project Root: $PROJECT_ROOT"
echo "📁 Server Dir: $SERVER_DIR"
echo "📁 Frontend Dir: $FRONTEND_DIR"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    echo -e "${YELLOW}🔄 Checking port $port...${NC}"
    if check_port $port; then
        echo -e "${YELLOW}⚠️  Port $port is in use, killing existing processes...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to start...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $((max_attempts * 2)) seconds${NC}"
    return 1
}

# Step 1: Clean up existing processes
echo -e "${BLUE}📋 Step 1: Cleaning up existing processes${NC}"
kill_port 6070  # Backend API
kill_port 3050  # Frontend

# Kill any remaining processes
pkill -f "api_server.py" 2>/dev/null || true
pkill -f "tsx.*server/index.ts" 2>/dev/null || true
sleep 2

# Step 2: Check dependencies
echo -e "${BLUE}📋 Step 2: Checking dependencies${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found${NC}"

# Step 3: Check directories exist
echo -e "${BLUE}📋 Step 3: Checking project structure${NC}"
if [ ! -d "$SERVER_DIR" ]; then
    echo -e "${RED}❌ Server directory not found: $SERVER_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server directory found${NC}"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend directory found${NC}"

# Step 4: Install Python dependencies
echo -e "${BLUE}📋 Step 4: Installing Python dependencies${NC}"
cd "$SERVER_DIR"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  No requirements.txt found, skipping Python deps${NC}"
fi

# Step 5: Install Node.js dependencies
echo -e "${BLUE}📋 Step 5: Installing Node.js dependencies${NC}"
cd "$FRONTEND_DIR"
if [ -f "package.json" ]; then
    npm install --silent
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${RED}❌ No package.json found in frontend directory${NC}"
    exit 1
fi

# Step 6: Check database setup
echo -e "${BLUE}📋 Step 6: Checking database setup${NC}"
cd "$SERVER_DIR"
if python3 -c "from database import Database; db = Database(); db.get_active_keywords()" 2>/dev/null; then
    echo -e "${GREEN}✅ Database is set up and accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Database not set up, initializing...${NC}"
    python3 setup_database.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database initialized successfully${NC}"
    else
        echo -e "${RED}❌ Database initialization failed${NC}"
        echo -e "${YELLOW}💡 Make sure PostgreSQL is running and check your .env file${NC}"
        exit 1
    fi
fi

# Step 7: Start Backend API Server (Python)
echo -e "${BLUE}📋 Step 7: Starting Python Backend Server${NC}"
cd "$SERVER_DIR"
echo -e "${YELLOW}🔄 Starting Python backend on port 6070...${NC}"
python3 api_server.py > api_server.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Step 8: Start Frontend Server (React) in parallel
echo -e "${BLUE}📋 Step 8: Starting React Frontend Server${NC}"
cd "$FRONTEND_DIR"
echo -e "${YELLOW}🔄 Starting React frontend on port 3050...${NC}"
PORT=3050 npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Step 9: Wait for both services to be ready
echo -e "${BLUE}📋 Step 9: Waiting for services to start${NC}"

# Wait for backend
if wait_for_service "http://localhost:6070/" "Python Backend API"; then
    echo -e "${GREEN}✅ Python Backend is running on http://localhost:6070${NC}"
else
    echo -e "${RED}❌ Python Backend failed to start${NC}"
    echo -e "${YELLOW}📋 Backend log:${NC}"
    tail -10 "$SERVER_DIR/api_server.log"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

# Wait for frontend
if wait_for_service "http://localhost:3050/" "React Frontend"; then
    echo -e "${GREEN}✅ React Frontend is running on http://localhost:3050${NC}"
else
    echo -e "${RED}❌ React Frontend failed to start${NC}"
    echo -e "${YELLOW}📋 Frontend log:${NC}"
    tail -10 "$FRONTEND_DIR/frontend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Step 10: Final system check
echo -e "${BLUE}📋 Step 10: Running system health check${NC}"
cd "$PROJECT_ROOT"

# Check backend API
if curl -s http://localhost:6070/api/dashboard | grep -q "totalReplies"; then
    TOTAL_LEADS=$(curl -s http://localhost:6070/api/dashboard | python3 -c "import sys, json; print(json.load(sys.stdin)['metrics']['totalReplies'])")
    echo -e "${GREEN}✅ Backend API health check passed - $TOTAL_LEADS leads in database${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API health check had issues${NC}"
fi

# Check frontend proxy
if curl -s http://localhost:3050/api/reddit/leads | grep -q "leads"; then
    PROXY_LEADS=$(curl -s http://localhost:3050/api/reddit/leads | python3 -c "import sys, json; print(len(json.load(sys.stdin)['leads']))")
    echo -e "${GREEN}✅ Frontend-Backend connection working - $PROXY_LEADS leads via proxy${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend-Backend proxy had issues${NC}"
fi

# Success message
echo ""
echo "=================================================================="
echo -e "${GREEN}🎉 SUCCESS! Reddit Lead Finder is now running!${NC}"
echo ""
echo -e "${BLUE}🌐 URLs:${NC}"
echo -e "   Frontend:     ${GREEN}http://localhost:3050${NC}"
echo -e "   Reddit Leads: ${GREEN}http://localhost:3050/reddit-leads${NC}"
echo -e "   Dashboard:    ${GREEN}http://localhost:3050/dashboard${NC}"
echo -e "   Backend API:  ${GREEN}http://localhost:6070${NC}"
echo -e "   API Docs:     ${GREEN}http://localhost:6070/docs${NC}"
echo ""
echo -e "${BLUE}📊 Process IDs:${NC}"
echo -e "   Python Backend PID:  $BACKEND_PID"
echo -e "   React Frontend PID:  $FRONTEND_PID"
echo ""
echo -e "${BLUE}📋 Management:${NC}"
echo -e "   Backend logs: ${YELLOW}tail -f $SERVER_DIR/api_server.log${NC}"
echo -e "   Frontend logs: ${YELLOW}tail -f $FRONTEND_DIR/frontend.log${NC}"
echo -e "   Stop all:     ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "   Or use:       ${YELLOW}./stop-app.sh${NC}"
echo ""
echo -e "${GREEN}🚀 Ready to find Reddit leads! Visit http://localhost:3050/reddit-leads${NC}"
echo "=================================================================="

# Keep script running and show logs
echo -e "${YELLOW}📋 Showing live logs from both services (Ctrl+C to stop):${NC}"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Show logs from both services
tail -f "$SERVER_DIR/api_server.log" "$FRONTEND_DIR/frontend.log" &
TAIL_PID=$!

# Wait for user to stop
wait $TAIL_PID