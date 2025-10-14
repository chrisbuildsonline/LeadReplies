# PostgreSQL Migration Guide

This guide will help you migrate from SQLite to PostgreSQL for better performance and scalability.

## 🚀 Quick Migration (Recommended)

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from: https://www.postgresql.org/download/windows/

### 2. Install Python Dependencies

```bash
pip install psycopg2-binary
```

### 3. Run Automated Setup

```bash
cd server
python setup_postgres.py
```

This will:
- ✅ Check PostgreSQL installation
- ✅ Create the `reddit_leads` database
- ✅ Create all necessary tables
- ✅ Migrate your existing SQLite data
- ✅ Verify the migration

### 4. Start the Application

```bash
./start-app.sh
```

## 🔧 Manual Migration (Advanced)

If you prefer to do it manually:

### 1. Create Database

```bash
createdb reddit_leads
```

### 2. Update Environment Variables

Your `.env` file has been updated with:
```env
# Database Configuration (PostgreSQL)
DB_HOST=localhost
DB_NAME=reddit_leads
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432
DATABASE_URL=postgresql://postgres:password@localhost:5432/reddit_leads
```

### 3. Run Migration Script

```bash
cd server
python migrate_to_postgres.py
```

### 4. Test Reddit Scraper with PostgreSQL

```bash
cd f5bot_tests
python reddit_scrape.py
```

## 📊 What's Been Updated

### Files Modified:
- ✅ `server/.env` - PostgreSQL connection settings
- ✅ `server/database.py` - Now uses PostgreSQL instead of SQLite
- ✅ `server/api_server.py` - Updated SQL queries for PostgreSQL syntax
- ✅ `f5bot_tests/reddit_scrape.py` - Now saves to PostgreSQL

### New Files Created:
- ✅ `server/database_postgres.py` - PostgreSQL database class
- ✅ `server/migrate_to_postgres.py` - Migration script
- ✅ `server/setup_postgres.py` - Automated setup
- ✅ `server/database_sqlite_backup.py` - Backup of original SQLite code

## 🔍 Verification

After migration, verify everything works:

### 1. Check Database Tables
```bash
psql reddit_leads -c "\dt"
```

### 2. Check Data Migration
```bash
psql reddit_leads -c "SELECT COUNT(*) FROM business_leads;"
```

### 3. Test Dashboard
Visit: http://localhost:3050/dashboard

### 4. Test Reddit Scraper
```bash
cd f5bot_tests
python reddit_scrape.py
```

## 🎯 Benefits of PostgreSQL

- **Better Performance**: Faster queries on large datasets
- **Concurrent Access**: Multiple users can access simultaneously
- **Advanced Features**: Full-text search, JSON support, etc.
- **Scalability**: Can handle millions of records
- **ACID Compliance**: Better data integrity
- **Backup & Recovery**: Enterprise-grade backup options

## 🔧 Troubleshooting

### PostgreSQL Not Starting
```bash
# macOS
brew services restart postgresql

# Ubuntu
sudo systemctl restart postgresql
```

### Connection Issues
Check your PostgreSQL configuration:
```bash
# Check if PostgreSQL is running
pg_isready

# Check PostgreSQL version
psql --version
```

### Permission Issues
```bash
# Create PostgreSQL user (if needed)
createuser -s postgres
```

### Database Connection Test
```bash
cd server
python -c "from database import Database; db = Database(); print('✅ Connection successful!')"
```

## 📝 Configuration Options

You can customize PostgreSQL settings in `.env`:

```env
DB_HOST=localhost          # PostgreSQL host
DB_NAME=reddit_leads       # Database name
DB_USER=postgres           # PostgreSQL user
DB_PASSWORD=password       # PostgreSQL password
DB_PORT=5432              # PostgreSQL port
```

## 🚀 Production Deployment

For production, consider:

1. **Secure Password**: Change the default password
2. **SSL Connection**: Enable SSL for security
3. **Connection Pooling**: Use pgbouncer for better performance
4. **Backup Strategy**: Set up automated backups
5. **Monitoring**: Use tools like pgAdmin or DataDog

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f server/api_server.log`
2. Verify PostgreSQL is running: `pg_isready`
3. Test database connection: `python server/setup_postgres.py`
4. Check the migration: `python server/migrate_to_postgres.py`

Your SQLite data is safely backed up in `server/database_sqlite_backup.py` and the original `reddit_leads_v2.db` file.