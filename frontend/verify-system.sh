#!/bin/bash

echo "🔍 Reddit Lead Finder - System Verification"
echo "=========================================="

# Check backend
echo "📡 Backend (port 6070):"
if curl -s http://localhost:6070/ | grep -q "Reddit Lead Finder API"; then
    echo "✅ Backend API is running"
    LEADS=$(curl -s http://localhost:6070/api/dashboard | jq -r '.metrics.totalReplies')
    echo "✅ Total leads in database: $LEADS"
else
    echo "❌ Backend API is not responding"
    exit 1
fi

# Check frontend
echo ""
echo "🌐 Frontend (port 3050):"
if curl -s http://localhost:3050/ | grep -q "html"; then
    echo "✅ Frontend is running"
    PROXY_LEADS=$(curl -s http://localhost:3050/api/reddit/leads | jq -r '.leads | length')
    echo "✅ Frontend can access leads: $PROXY_LEADS leads via proxy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

echo ""
echo "🎉 SUCCESS! System is fully operational"
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