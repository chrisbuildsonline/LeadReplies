#!/bin/bash

echo "🔄 Force rebuilding Docker containers..."

# Stop all containers
docker-compose down

# Remove old images
docker-compose build --no-cache

# Start fresh
docker-compose up -d

echo "✅ Containers rebuilt and started"
echo "🌐 Frontend: http://localhost:3050"
echo "🔧 Backend: http://localhost:6070"