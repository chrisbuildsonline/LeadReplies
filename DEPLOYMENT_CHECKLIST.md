# 🚀 Coolify Deployment Checklist

## Pre-Deployment ✅

- [ ] **Coolify server** is running and accessible
- [ ] **Domain name** is configured and pointing to Coolify server
- [ ] **API keys** are ready (Anthropic/DeepSeek)
- [ ] **Code is committed** and pushed to Git repository
- [ ] **Environment variables** are prepared

## Coolify Setup ⚙️

### 1. Create Project
- [ ] New project created in Coolify
- [ ] Git repository connected
- [ ] Build pack set to "Docker Compose"

### 2. Database Setup
- [ ] PostgreSQL service created (version 15)
- [ ] Database name: `reddit_leads`
- [ ] Secure password generated
- [ ] Connection details noted

### 3. Environment Variables
Copy these from `.env.production.example`:

**Required:**
- [ ] `ANTHROPIC_API_KEY`
- [ ] `DB_HOST` (usually the PostgreSQL service name)
- [ ] `DB_PASSWORD` (from PostgreSQL service)
- [ ] `DATABASE_URL` (full connection string)
- [ ] `JWT_SECRET` (generate a secure random string)

**Optional:**
- [ ] `DEEPSEEK_API_KEY`
- [ ] `REDDIT_CLIENT_ID`
- [ ] `REDDIT_CLIENT_SECRET`
- [ ] `OPENROUTER_KEY`

### 4. Domain Configuration
- [ ] Domain added in Coolify
- [ ] DNS configured (A record pointing to Coolify server)
- [ ] SSL/TLS enabled (Let's Encrypt)

## Deployment 🚀

- [ ] Click "Deploy" in Coolify
- [ ] Monitor build logs for errors
- [ ] Wait for all services to start (2-5 minutes)
- [ ] Verify deployment health

## Post-Deployment Testing 🧪

### Health Checks
- [ ] Frontend loads: `https://yourdomain.com`
- [ ] Backend API responds: `https://yourdomain.com/api/health`
- [ ] Database connection working (check backend logs)

### Functionality Tests
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard loads with data
- [ ] Reddit leads page accessible
- [ ] Background scraping service running

### Monitor Logs
- [ ] Backend logs show no errors
- [ ] Frontend logs clean
- [ ] Background service logs show scraping activity
- [ ] PostgreSQL logs show successful connections

## Troubleshooting 🔧

### Common Issues

**Build Fails:**
- [ ] Check Dockerfile syntax
- [ ] Verify all files are committed
- [ ] Check build logs in Coolify

**Database Connection Errors:**
- [ ] Verify `DATABASE_URL` format
- [ ] Check PostgreSQL service is running
- [ ] Confirm network connectivity

**Frontend Not Loading:**
- [ ] Check if backend is responding
- [ ] Verify environment variables
- [ ] Check browser console for errors

**Background Service Issues:**
- [ ] Verify API keys are valid
- [ ] Check scraping interval settings
- [ ] Monitor background service logs

## Success Metrics 📊

Your deployment is successful when:

- [ ] **Frontend accessible** at your domain
- [ ] **API health check** returns 200 OK
- [ ] **User registration/login** works
- [ ] **Database queries** execute successfully
- [ ] **Background scraping** runs automatically
- [ ] **No error logs** in any service

## Maintenance 🔄

### Regular Tasks
- [ ] Monitor resource usage
- [ ] Check logs for errors
- [ ] Update dependencies periodically
- [ ] Backup database regularly
- [ ] Rotate API keys as needed

### Scaling Considerations
- [ ] Monitor CPU/memory usage
- [ ] Consider horizontal scaling for high traffic
- [ ] Optimize database queries if needed
- [ ] Set up monitoring/alerting

---

## Quick Commands

**Local Testing:**
```bash
./deploy.sh
```

**Check Deployment Status:**
```bash
curl https://yourdomain.com/api/health
```

**View Logs in Coolify:**
- Go to your application → Logs tab
- Select service (frontend/backend/background)

---

🎉 **Success!** Your Reddit Lead Finder is now live and automatically discovering business leads from Reddit!