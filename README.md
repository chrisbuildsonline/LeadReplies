# 🚀 Reddit Lead Finder

A complete full-stack system that automatically finds potential customers on Reddit, analyzes them with AI, and presents them in a beautiful dashboard.

## 📁 Project Structure

```
leadreplies/
├── server/          # Python backend (FastAPI + Reddit scraper + AI)
├── frontend/        # React frontend (TypeScript + UI)
├── start-app.sh     # Complete startup with health checks
├── start-simple.sh  # Quick startup
├── stop-app.sh      # Stop all services
└── verify-system.sh # Check system status
```

## 🚀 Quick Start

### 1. Start Everything (Recommended)
```bash
./start-app.sh
```
This will:
- ✅ Install all dependencies
- ✅ Set up database if needed
- ✅ Start Python backend on port 6070
- ✅ Start React frontend on port 3050
- ✅ Run health checks
- ✅ Show live logs

### 2. Quick Start (No checks)
```bash
./start-simple.sh
```

### 3. Stop Everything
```bash
./stop-app.sh
```

### 4. Check Status
```bash
./verify-system.sh
```

## 🌐 URLs

Once started, access your app at:

- **Main App**: http://localhost:3050
- **Reddit Leads**: http://localhost:3050/reddit-leads
- **Dashboard**: http://localhost:3050/dashboard
- **Backend API**: http://localhost:6070
- **API Docs**: http://localhost:6070/docs

## 🎯 What It Does

1. **Scrapes Reddit** - Monitors Reddit for relevant keywords
2. **AI Analysis** - Claude 3 analyzes each post (0-100% probability)
3. **Database Storage** - PostgreSQL stores all leads with metadata
4. **Web Interface** - React dashboard to view and manage leads
5. **Real-time Updates** - Live data synchronization

## 📊 Current Status

The system already has **138 real Reddit leads** with AI analysis:
- High-quality leads (70%+): Ready for outreach
- Medium-quality leads (40-69%): Worth investigating
- Full conversation context and AI reasoning

## 🛠️ Requirements

- **Python 3.7+** with pip
- **Node.js 16+** with npm
- **PostgreSQL** database
- **Anthropic API key** (for AI analysis)

## 🔧 Configuration

Edit `server/.env` to configure:
- Database connection
- API keys
- Ports and URLs

## 📋 Management

### View Logs
```bash
# Backend logs
tail -f server/api_server.log

# Frontend logs
tail -f frontend/frontend.log
```

### Manual Operations
```bash
# Run scraping once
python3 server/scheduler.py once

# View leads in terminal
python3 server/view_leads.py

# Database setup
python3 server/setup_database.py
```

## 🎉 Success!

Your Reddit Lead Finder is now a complete, production-ready system that automatically discovers high-quality business leads from Reddit conversations!

Visit **http://localhost:3050/reddit-leads** to start exploring your leads! 🎯