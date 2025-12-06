# 🔐 Persistence Quick Reference

## ✅ Your Data is Persistent!

All data (users, permissions, S3 connections, audit logs) is **automatically saved** in a Docker volume and **survives container restarts**.

---

## 🔑 CRITICAL: SECRET_KEY

**Current SECRET_KEY**: `I0YrIQtYrN8yd4gIvdrMFMeC4_VhJw3cSorfzCNkjz8`

⚠️ **DO NOT CHANGE THIS VALUE!**

This key encrypts all S3 credentials in the database. If you change it, you won't be able to decrypt existing S3 connections!

**Location**: `c:\Users\User\Downloads\s3-access-manager\.env`

---

## 💾 What Persists

| Data Type | Persists? | Where Stored |
|-----------|-----------|--------------|
| Users | ✅ Yes | PostgreSQL → Docker Volume |
| Permissions | ✅ Yes | PostgreSQL → Docker Volume |
| S3 Connections | ✅ Yes | PostgreSQL → Docker Volume (encrypted) |
| Audit Logs | ✅ Yes | PostgreSQL → Docker Volume |
| .env Settings | ✅ Yes | File on disk |

---

## 🔄 Safe Operations

```bash
# Restart containers (data persists)
docker-compose restart

# Stop and start (data persists)
docker-compose down
docker-compose up -d

# Rebuild (data persists)
docker-compose up -d --build
```

---

## ⚠️ DANGEROUS Operations

```bash
# ❌ DON'T DO THIS unless you want to delete ALL data!
docker-compose down -v  # Deletes volumes = loses all data!
```

---

## 💾 Backup Commands

### Backup Database:
```bash
docker-compose exec db pg_dump -U s3manager s3manager > backup.sql
```

### Backup .env:
```bash
copy .env .env.backup
```

### Restore Database:
```bash
docker-compose exec -T db psql -U s3manager s3manager < backup.sql
```

---

## 🔍 Verify Persistence

### Check if volume exists:
```bash
docker volume ls | findstr postgres_data
```

### Check S3 connections in database:
```bash
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT id, name, is_active FROM s3_connections;"
```

---

## 📝 Summary

✅ **All data persists** across container restarts
✅ **SECRET_KEY is set** and should never change
✅ **Docker volume** stores all database data
✅ **S3 credentials** are encrypted and persistent

**Just remember**: Don't change SECRET_KEY and don't use `docker-compose down -v`!

---

For detailed information, see: `PERSISTENCE_GUIDE.md`
