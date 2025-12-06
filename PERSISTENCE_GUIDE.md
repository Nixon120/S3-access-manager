# Data Persistence Guide

## ✅ What is Persistent (Survives Container Restarts)

All data in the S3 Access Manager is **automatically persistent** thanks to Docker volumes and the PostgreSQL database.

### Persistent Data:

1. ✅ **Users** - All user accounts and passwords
2. ✅ **Permissions** - All bucket/folder access permissions
3. ✅ **S3 Connections** - All AWS account connections with **encrypted credentials**
4. ✅ **Audit Logs** - Complete history of all actions
5. ✅ **Database** - Stored in Docker volume `postgres_data`

---

## 🔐 Critical: SECRET_KEY

The `SECRET_KEY` in your `.env` file is **CRITICAL** for data persistence:

### Why It Matters:

- **Encrypts S3 credentials** stored in the database
- **Signs JWT tokens** for authentication
- **Must remain constant** across deployments

### ⚠️ WARNING:

**If you change the SECRET_KEY after creating S3 Connections, you will NOT be able to decrypt existing credentials!**

### Current SECRET_KEY:

```bash
SECRET_KEY=I0YrIQtYrN8yd4gIvdrMFMeC4_VhJw3cSorfzCNkjz8
```

**DO NOT CHANGE THIS VALUE** unless you:
1. Have no S3 Connections created yet, OR
2. Are prepared to delete and recreate all S3 Connections

---

## 📁 Docker Volumes

### Database Volume

```yaml
volumes:
  postgres_data:  # Stores all PostgreSQL data
```

**Location**: Docker manages this volume automatically

**What's stored**:
- All database tables (users, permissions, s3_connections, audit_logs)
- Encrypted S3 credentials
- All application data

### How to Verify Volume Exists:

```bash
docker volume ls | findstr postgres_data
```

Should show: `s3-access-manager_postgres_data`

---

## 🔄 Restart Scenarios

### Scenario 1: Restart Containers (Data Persists)

```bash
docker-compose restart
```

**Result**: ✅ All data persists (users, permissions, connections, logs)

### Scenario 2: Stop and Start (Data Persists)

```bash
docker-compose down
docker-compose up -d
```

**Result**: ✅ All data persists

### Scenario 3: Rebuild Containers (Data Persists)

```bash
docker-compose down
docker-compose up -d --build
```

**Result**: ✅ All data persists (volume is not deleted)

### Scenario 4: Delete Volumes (Data LOST!)

```bash
docker-compose down -v  # ⚠️ DANGER: Deletes volumes!
```

**Result**: ❌ ALL data is deleted (users, permissions, connections, logs)

**Only use this if you want to start completely fresh!**

---

## 💾 Backup Strategy

### Backup Database

To backup all your data (users, permissions, S3 connections):

```bash
# Create backup
docker-compose exec db pg_dump -U s3manager s3manager > backup_$(date +%Y%m%d).sql

# Or on Windows:
docker-compose exec db pg_dump -U s3manager s3manager > backup.sql
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T db psql -U s3manager s3manager < backup.sql
```

### Backup .env File

**CRITICAL**: Also backup your `.env` file, especially the `SECRET_KEY`!

```bash
# Copy .env to safe location
copy .env .env.backup
```

---

## 🔒 S3 Connections Persistence

### How S3 Connections Are Stored:

1. **Created via Admin Panel** → Stored in database
2. **Credentials Encrypted** → Using SECRET_KEY from .env
3. **Stored in `s3_connections` table** → In PostgreSQL
4. **Persists across restarts** → Thanks to Docker volume

### Example Flow:

```
1. Admin creates S3 Connection:
   - Name: "Production AWS"
   - Access Key: AKIA...
   - Secret Key: abc123...

2. Backend encrypts credentials:
   - Uses SECRET_KEY from .env
   - Stores encrypted values in database

3. Container restarts:
   - Database volume persists
   - Encrypted credentials still there
   - Backend decrypts using same SECRET_KEY
   - ✅ Connection works!

4. If SECRET_KEY changes:
   - Decryption fails
   - ❌ Connection broken!
```

---

## 📊 Verify Persistence

### Check Database Volume:

```bash
docker volume inspect s3-access-manager_postgres_data
```

### Check Database Size:

```bash
docker-compose exec db psql -U s3manager -d s3manager -c "\l+"
```

### Check Tables:

```bash
docker-compose exec db psql -U s3manager -d s3manager -c "\dt"
```

Should show:
- `users`
- `permissions`
- `s3_connections`
- `audit_logs`
- `alembic_version`

### Check S3 Connections:

```bash
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT id, name, account_id, is_active FROM s3_connections;"
```

---

## 🚀 Production Deployment

### For Production, You Should:

1. **Use a strong SECRET_KEY** (already done ✅)
2. **Backup the SECRET_KEY** securely
3. **Use environment-specific .env files**
4. **Set up regular database backups**
5. **Use external PostgreSQL** (not Docker container)
6. **Store .env in secure vault** (e.g., AWS Secrets Manager)

### Example Production .env:

```bash
# Production Configuration
ENVIRONMENT=production
DEBUG=false

# Database (External)
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/s3manager

# Security (From Vault)
SECRET_KEY=${VAULT_SECRET_KEY}

# AWS (From IAM Role - no keys needed)
AWS_REGION=us-east-1
```

---

## 📝 Summary

### ✅ What Persists Automatically:

- All users and passwords
- All permissions
- All S3 connections (with encrypted credentials)
- All audit logs
- Database schema

### ⚠️ What You Must Protect:

- **SECRET_KEY** in .env (critical for decryption!)
- **.env file** itself (contains configuration)
- **Docker volume** `postgres_data` (contains all data)

### 🔄 Safe Operations:

- `docker-compose restart` ✅
- `docker-compose down` + `docker-compose up -d` ✅
- `docker-compose up -d --build` ✅

### ⚠️ Dangerous Operations:

- `docker-compose down -v` ❌ (deletes volumes!)
- Changing SECRET_KEY ❌ (breaks encryption!)
- Deleting postgres_data volume ❌ (loses all data!)

---

## 🆘 Recovery Scenarios

### Lost SECRET_KEY:

**Problem**: Changed SECRET_KEY, can't decrypt S3 connections

**Solution**:
1. Restore old SECRET_KEY from backup
2. OR delete all S3 connections and recreate them

### Lost Database:

**Problem**: Deleted postgres_data volume

**Solution**:
1. Restore from backup: `docker-compose exec -T db psql -U s3manager s3manager < backup.sql`
2. OR start fresh and recreate everything

### Container Won't Start:

**Problem**: Docker Desktop not running

**Solution**:
1. Start Docker Desktop
2. Wait for it to be ready
3. Run `docker-compose up -d`

---

**Your data is now persistent and secure!** 🎉

Just remember:
1. ✅ Don't change SECRET_KEY
2. ✅ Backup .env file
3. ✅ Regular database backups
4. ✅ Don't use `docker-compose down -v`
