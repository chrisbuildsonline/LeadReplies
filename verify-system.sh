#!/bin/bash

echo "🔍 Reddit Lead Finder - System Verification"
echo "=========================================="
echo "📁 Project Root: $(pwd)"

# Check Python backend
echo "📡 Python Backend (server/ on port 6070):"
if curl -s http://localhost:6070/ | grep -q "Reddit Lead Finder API"; then
    echo "✅ Python backend API is running"
    LEADS=$(curl -s http://localhost:6070/api/dashboard | python3 -c "import sys, json; print(json.load(sys.stdin)['metrics']['totalReplies'])" 2>/dev/null || echo "0")
    echo "✅ Total leads in database: $LEADS"
else
    echo "❌ Python backend API is not responding"
    exit 1
fi

# Check React frontend
echo ""
echo "🌐 React Frontend (frontend/ on port 3050):"
if curl -s http://localhost:3050/ | grep -q "html"; then
    echo "✅ React frontend is running"
    PROXY_LEADS=$(curl -s http://localhost:3050/api/reddit/leads | python3 -c "import sys, json; print(len(json.load(sys.stdin)['leads']))" 2>/dev/null || echo "0")
    echo "✅ Frontend can access leads: $PROXY_LEADS leads via proxy"
else
    echo "❌ React frontend is not responding"
    exit 1
fi

echo ""
echo "🎉 SUCCESS! Both services are operational"
echo ""
echo "🌐 Access your app:"
echo "   Main App:      http://localhost:3050"
echo "   Reddit Leads:  http://localhost:3050/reddit-leads"
echo "   Dashboard:     http://localhost:3050/dashboard"
echo "   Backend API:   http://localhost:6070"
echo ""
echo "📊 Current Status:"
echo "   Total Leads: $LEADS"
echo "   Available via API: $PROXY_LEADS"
echo ""
echo "📋 Project Structure:"
echo "   server/     - Python backend (FastAPI + Reddit scraper)"
echo "   frontend/   - React frontend (TypeScript + UI)"