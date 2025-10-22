# Coolify Deployment Fix

## Issue Fixed
Coolify was looking for `/docker-compose.yaml` but the file was named `docker-compose.yml`.

## Changes Made

### 1. Created docker-compose.yaml
- Copied `docker-compose.yml` to `docker-compose.yaml` (with .yaml extension)
- Removed volume mounts that could cause issues in Coolify
- Simplified the configuration for cloud deployment

### 2. Updated Dockerfile.frontend
- Fixed the build process to match the actual frontend structure
- Removed unnecessary client directory copying
- Streamlined the production build

### 3. Deployment Structure
```
├── docker-compose.yaml     # Main deployment file (Coolify compatible)
├── docker-compose.yml      # Original file (kept for local development)
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container (fixed)
└── server/                 # Backend code
    ├── api_server.py       # Main API with /health endpoint
    ├── background_service.py # Reddit scraping service
    └── ...
```

## Next Steps for Coolify

1. **Push Changes to Git**
   ```bash
   git add .
   git commit -m "Fix Coolify deployment - add docker-compose.yaml"
   git push origin main
   ```

2. **In Coolify Dashboard:**
   - Go to your application
   - Click "Deploy" to trigger a new deployment
   - Monitor the build logs

3. **Environment Variables to Set in Coolify:**
   ```
   ANTHROPIC_API_KEY=your-key-here
   DEEPSEEK_API_KEY=your-deepseek-key
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   DB_NAME=reddit_leads
   DB_USER=postgres
   DB_PASSWORD=your-secure-password
   SCRAPING_INTERVAL_MINUTES=120
   ```

4. **Database Setup:**
   - Create a PostgreSQL service in Coolify
   - Update the DB_* environment variables with the connection details

## Health Checks
- Backend: `http://your-domain:8001/health`
- Frontend: `http://your-domain:3000`

## Services
- **Frontend**: Port 3000 (public)
- **Backend**: Port 8001 (internal)
- **Background**: Reddit scraping service
- **Database**: PostgreSQL 15

The deployment should now work correctly with Coolify!