#!/bin/bash

# Reddit Lead Finder - Coolify Deployment Helper Script
# This script helps prepare and deploy your app to Coolify

set -e

echo "🚀 Reddit Lead Finder - Coolify Deployment Helper"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists git; then
    echo "❌ Git is required but not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker is required for local testing"
    echo "ℹ️  You can skip local testing and deploy directly to Coolify"
fi

# Check git status
echo "📋 Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Commit them before deploying:"
    git status --short
    echo ""
    read -p "Do you want to commit all changes now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_message
        git commit -m "$commit_message"
        echo "✅ Changes committed"
    else
        echo "⚠️  Proceeding with uncommitted changes (not recommended)"
    fi
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "⚠️  No .env.production file found"
    echo "📝 Creating from template..."
    cp .env.production.example .env.production
    echo "✅ Created .env.production from template"
    echo "🔧 Please edit .env.production with your actual values before deploying"
    echo ""
fi

# Offer to test locally
if command_exists docker && command_exists docker-compose; then
    echo "🐳 Docker is available for local testing"
    read -p "Do you want to test the deployment locally first? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "🧪 Testing deployment locally..."
        
        # Stop any existing containers
        docker-compose down 2>/dev/null || true
        
        # Build and start services
        echo "🔨 Building containers..."
        docker-compose build
        
        echo "🚀 Starting services..."
        docker-compose up -d
        
        # Wait for services to start
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Test health endpoints
        echo "🔍 Testing health endpoints..."
        
        # Test backend health
        if curl -f http://localhost:6070/health >/dev/null 2>&1; then
            echo "✅ Backend health check passed"
        else
            echo "❌ Backend health check failed"
            echo "📋 Backend logs:"
            docker-compose logs backend | tail -20
        fi
        
        # Test frontend
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            echo "✅ Frontend health check passed"
        else
            echo "❌ Frontend health check failed"
            echo "📋 Frontend logs:"
            docker-compose logs frontend | tail -20
        fi
        
        echo ""
        echo "🌐 Local test URLs:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:6070"
        echo "   API Health: http://localhost:6070/health"
        echo ""
        
        read -p "Press Enter to stop local test and continue with deployment preparation..."
        docker-compose down
    fi
fi

# Push to git
echo "📤 Pushing to git repository..."
current_branch=$(git branch --show-current)
git push origin "$current_branch"
echo "✅ Code pushed to $current_branch branch"

echo ""
echo "🎯 Deployment Preparation Complete!"
echo "=================================="
echo ""
echo "Next steps for Coolify deployment:"
echo ""
echo "1. 📋 Copy environment variables from .env.production to Coolify:"
echo "   - Go to your Coolify project settings"
echo "   - Add all variables from .env.production"
echo "   - Make sure to use secure passwords!"
echo ""
echo "2. 🗄️ Set up PostgreSQL database in Coolify:"
echo "   - Create a new PostgreSQL service"
echo "   - Note the connection details"
echo "   - Update DB_* variables in Coolify accordingly"
echo ""
echo "3. 🌐 Configure your domain:"
echo "   - Set up DNS to point to your Coolify server"
echo "   - Add domain in Coolify application settings"
echo "   - Enable SSL/TLS"
echo ""
echo "4. 🚀 Deploy:"
echo "   - Click 'Deploy' in your Coolify application"
echo "   - Monitor the build logs"
echo "   - Test your live application"
echo ""
echo "📚 For detailed instructions, see COOLIFY_SETUP.md"
echo ""
echo "🎉 Your Reddit Lead Finder is ready for Coolify deployment!"