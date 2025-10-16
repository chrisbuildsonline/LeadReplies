# 🚀 Coolify Deployment Guide for Reddit Lead Finder

This guide will help you deploy your Reddit Lead Finder app to a self-hosted Coolify instance.

## 📋 Prerequisites

1. **Coolify Server**: A running Coolify instance (v4.0+)
2. **Domain**: A domain name pointing to your Coolify server
3. **API Keys**: Anthropic API key for AI analysis
4. **Git Repository**: Your code pushed to a Git repository (GitHub, GitLab, etc.)

## 🔧 Step 1: Prepare Your Repository

1. **Push your code** to a Git repository that Coolify can access
2. **Ensure all files are committed**:
   ```bash
   git add .
   git commit -m "Add Coolify deployment configuration"
   git push origin main
   ```

## 🎯 Step 2: Create Project in Coolify

1. **Login to your Coolify dashboard**
2. **Create a new project**:
   - Click "New Project"
   - Name: "Reddit Lead Finder"
   - Description: "AI-powered Reddit lead generation system"

3. **Add your Git repository**:
   - Click "New Resource" → "Application"
   - Select your Git provider (GitHub/GitLab/etc.)
   - Choose your repository
   - Branch: `main`
   - Build Pack: `Docker Compose`

## 🗄️ Step 3: Set Up Database

### Option A: Use Coolify's Managed PostgreSQL (Recommended)

1. **Create PostgreSQL service**:
   - In your project, click "New Resource" → "Database"
   - Select "PostgreSQL"
   - Version: 15
   - Name: `reddit-leads-db`
   - Database: `reddit_leads`
   - Username: `postgres`
   - Password: Generate a secure password

2. **Note the connection details** - Coolify will provide:
   - Host: `reddit-leads-db`
   - Port: `5432`
   - Database: `reddit_leads`
   - Username: `postgres`
   - Password: [generated password]

### Option B: External PostgreSQL

If you prefer to use an external PostgreSQL instance, prepare the connection details.

## 🔐 Step 4: Configure Environment Variables

In your Coolify application settings, add these environment variables:

### Required Variables
```bash
# AI API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Database Configuration (adjust based on your setup)
DB_HOST=reddit-leads-db
DB_NAME=reddit_leads
DB_USER=postgres
DB_PASSWORD=your-secure-database-password
DB_PORT=5432
DATABASE_URL=postgresql://postgres:your-password@reddit-leads-db:5432/reddit_leads

# Application Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
BACKEND_URL=http://backend:8001
FRONTEND_URL=http://frontend:3000
SCRAPING_INTERVAL_MINUTES=120
```

### Optional Variables
```bash
# Reddit API (for enhanced scraping)
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=Chrome

# Alternative AI Provider
OPENROUTER_KEY=sk-or-v1-your-openrouter-key
```

## 🌐 Step 5: Configure Domains

1. **Set up your domain**:
   - In application settings, go to "Domains"
   - Add your domain (e.g., `leads.yourdomain.com`)
   - Enable SSL/TLS (Let's Encrypt)

2. **Configure DNS**:
   - Point your domain to your Coolify server's IP
   - Wait for DNS propagation (5-30 minutes)

## 🚀 Step 6: Deploy

1. **Start deployment**:
   - Click "Deploy" in your Coolify application
   - Monitor the build logs
   - Wait for all services to start (2-5 minutes)

2. **Verify deployment**:
   - Check that all containers are running
   - Visit your domain to test the frontend
   - Check `/api/health` endpoint for backend status

## 📊 Step 7: Post-Deployment Setup

### Initialize Database
The database will be automatically set up on first run, but you can verify:

1. **Check database connection**:
   - Look at backend logs in Coolify
   - Should see "Database setup completed" message

2. **Verify data**:
   - Visit your app at `https://yourdomain.com/reddit-leads`
   - The system should start collecting leads automatically

### Monitor Services

1. **Check logs**:
   - Backend: Monitor API server logs
   - Frontend: Check for any client-side errors
   - Background: Verify scraping service is running

2. **Health checks**:
   - Frontend: `https://yourdomain.com/`
   - Backend API: `https://yourdomain.com/api/health`

## 🔧 Step 8: Configure Backups (Optional)

1. **Database backups**:
   - In PostgreSQL service settings
   - Enable automatic backups
   - Set retention period (7-30 days)

2. **Application data**:
   - Coolify automatically handles container persistence
   - Consider backing up environment variables

## 🎯 Success! Your App is Live

Your Reddit Lead Finder should now be running at:
- **Main App**: `https://yourdomain.com`
- **Reddit Leads**: `https://yourdomain.com/reddit-leads`
- **Dashboard**: `https://yourdomain.com/dashboard`

## 🛠️ Troubleshooting

### Common Issues

1. **Build fails**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Check build logs in Coolify

2. **Database connection errors**:
   - Verify DATABASE_URL format
   - Check PostgreSQL service is running
   - Confirm network connectivity between services

3. **Frontend not loading**:
   - Check if backend is responding
   - Verify environment variables
   - Check browser console for errors

4. **Background service not working**:
   - Check API keys are valid
   - Verify scraping interval settings
   - Monitor background service logs

### Getting Help

1. **Check Coolify logs**: Each service has detailed logs
2. **Review environment variables**: Ensure all required vars are set
3. **Test locally**: Use `docker-compose up` to test locally first
4. **Coolify community**: Join Coolify Discord for support

## 🔄 Updates and Maintenance

### Deploying Updates
1. Push changes to your Git repository
2. Coolify will auto-deploy (if enabled) or click "Deploy"
3. Monitor deployment logs

### Scaling
- Adjust resource limits in Coolify settings
- Consider horizontal scaling for high traffic
- Monitor CPU and memory usage

### Security
- Regularly update dependencies
- Rotate API keys periodically
- Monitor access logs
- Keep Coolify updated

---

🎉 **Congratulations!** Your Reddit Lead Finder is now running on Coolify and automatically discovering high-quality business leads from Reddit!