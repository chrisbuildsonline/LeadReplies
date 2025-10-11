#!/bin/bash

# Reddit Lead Finder - Complete Startup Script
# This script starts both backend and frontend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="/Users/chrisjohansson/Google Drive/Mild Media/Projekt/Egna Projekt/ongoing/leadreplies"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SERVER_DIR="$PROJECT_ROOT/server"

echo -e "${BLUE}🚀 Reddit Lead Finder - Starting Complete System${NC}"
echo "=================================================================="

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

# Step 3: Install Python dependencies
echo -e "${BLUE}📋 Step 3: Installing Python dependencies${NC}"
cd "$SERVER_DIR"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  No requirements.txt found, skipping Python deps${NC}"
fi

# Step 4: Install Node.js dependencies
echo -e "${BLUE}📋 Step 4: Installing Node.js dependencies${NC}"
cd "$FRONTEND_DIR"
if [ -f "package.json" ]; then
    npm install --silent
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${RED}❌ No package.json found in frontend directory${NC}"
    exit 1
fi

# Step 5: Check database setup
echo -e "${BLUE}📋 Step 5: Checking database setup${NC}"
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

# Step 6: Start Backend API Server
echo -e "${BLUE}📋 Step 6: Starting Backend API Server${NC}"
cd "$SERVER_DIR"
echo -e "${YELLOW}🔄 Starting backend on port 6070...${NC}"
python3 api_server.py > api_server.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
if wait_for_service "http://localhost:6070/" "Backend API"; then
    echo -e "${GREEN}✅ Backend API is running on http://localhost:6070${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "${YELLOW}📋 Backend log:${NC}"
    tail -10 "$SERVER_DIR/api_server.log"
    exit 1
fi

# Step 7: Start Frontend Server
echo -e "${BLUE}📋 Step 7: Starting Frontend Server${NC}"
cd "$FRONTEND_DIR"
echo -e "${YELLOW}🔄 Starting frontend on port 3050...${NC}"
PORT=3050 npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
if wait_for_service "http://localhost:3050/" "Frontend"; then
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3050${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo -e "${YELLOW}📋 Frontend log:${NC}"
    tail -10 "$FRONTEND_DIR/frontend.log"
    exit 1
fi

# Step 8: Final system check
echo -e "${BLUE}📋 Step 8: Running system health check${NC}"
cd "$PROJECT_ROOT"
if python3 check_status.py | grep -q "SUCCESS"; then
    echo -e "${GREEN}✅ System health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  System health check had issues, but services are running${NC}"
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
echo -e "   Backend PID:  $BACKEND_PID"
echo -e "   Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${BLUE}📋 Management:${NC}"
echo -e "   View logs:    ${YELLOW}tail -f $SERVER_DIR/api_server.log${NC}"
echo -e "   View logs:    ${YELLOW}tail -f $FRONTEND_DIR/frontend.log${NC}"
echo -e "   Stop all:     ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "   Check status: ${YELLOW}python3 $PROJECT_ROOT/check_status.py${NC}"
echo ""
echo -e "${GREEN}🚀 Ready to find Reddit leads! Visit http://localhost:3050/reddit-leads${NC}"
echo "=================================================================="

# Keep script running and show logs
echo -e "${YELLOW}📋 Showing live logs (Ctrl+C to stop):${NC}"
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