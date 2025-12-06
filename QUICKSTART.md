# S3 Access Manager - Quick Start Guide

## Overview
This application provides secure, credential-less access to AWS S3 for external users without distributing AWS access keys. Perfect for healthcare and enterprise environments with HIPAA compliance requirements.

## Features Included

### Core Features
✅ User authentication with JWT tokens
✅ Admin dashboard with user management
✅ Fine-grained S3 permissions (bucket + prefix level)
✅ Presigned URL generation for secure uploads/downloads
✅ Complete audit logging of all actions
✅ File browser with drag-and-drop upload
✅ No AWS credentials exposed to end users

### Admin Features
- User management (create, edit, delete users)
- Permission assignment (map users to S3 buckets/prefixes)
- Audit log viewer with filtering
- System statistics dashboard

### User Features
- Browse accessible S3 buckets
- Upload files via drag-and-drop
- Download files
- View file listings
- Personal activity history

## Quick Start (Development)

### 1. Prerequisites
```bash
# Install required software
- Docker & Docker Compose
- Git
```

### 2. Clone and Setup

```bash
# Clone the repository
cd s3-access-manager

# Copy environment file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
```

Required environment variables:
```env
AWS_ACCESS_KEY_ID=your-key-here
AWS_SECRET_ACCESS_KEY=your-secret-here
AWS_REGION=us-east-1
SECRET_KEY=generate-random-key-here
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Create Admin User

```bash
# Run the admin creation script
docker-compose exec backend python scripts/create_admin.py
```

Enter your admin credentials when prompted.

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

Login with your admin credentials!

## Usage Guide

### For Administrators

#### 1. Add Users
1. Navigate to "Users" in the sidebar
2. Click "Add User"
3. Enter user details (email, name, password)
4. Check "Administrator" if you want to grant admin access
5. Click "Create"

#### 2. Assign Permissions
1. Navigate to "Permissions" in the sidebar
2. Click "Add Permission"
3. Select the user from dropdown
4. Enter S3 bucket name (e.g., `my-data-bucket`)
5. Enter prefix/folder path (optional, e.g., `partner-uploads/`)
6. Select permission types:
   - **Read**: Download files
   - **Write**: Upload files
   - **Delete**: Delete files
   - **List**: Browse files
7. Add a description (optional)
8. Click "Create"

#### 3. Monitor Activity
1. Navigate to "Audit Logs" in the sidebar
2. Filter by:
   - Action type (upload, download, delete, list)
   - Status (success, failure)
   - User
3. View detailed logs of all actions

### For Regular Users

#### 1. Browse Files
1. Login with your credentials
2. Click on a bucket from the left panel
3. Files in that location will appear on the right

#### 2. Upload Files
1. Select a bucket
2. Click "Upload" button
3. Drag and drop files or click to browse
4. Files will upload automatically

#### 3. Download Files
1. Browse to the file location
2. Click the download icon next to the file
3. File will download in a new tab

## Security Best Practices

### 1. Strong Passwords
- Use complex passwords for all accounts
- Minimum 8 characters
- Include numbers and special characters

### 2. Regular Audits
- Review audit logs weekly
- Check for suspicious activity
- Monitor failed login attempts

### 3. Principle of Least Privilege
- Only grant necessary permissions
- Use specific prefixes instead of root access
- Review permissions quarterly

### 4. AWS Security
- Use IAM Roles instead of access keys (in production)
- Enable S3 bucket encryption
- Use KMS for sensitive data
- Enable CloudTrail logging

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│   React     │ (Port 3000)
│  Frontend   │
└──────┬──────┘
       │ API Calls
       ▼
┌─────────────┐
│   FastAPI   │ (Port 8000)
│   Backend   │
└──────┬──────┘
       │
       ├────────────┐
       │            │
       ▼            ▼
┌──────────┐  ┌─────────┐
│PostgreSQL│  │  AWS S3 │
│    DB    │  │         │
└──────────┘  └─────────┘
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait 30 seconds and try again
# 2. Port 8000 in use - stop other services using that port
# 3. AWS credentials invalid - check .env file
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Common issues:
# 1. Port 3000 in use - stop other services
# 2. Node modules issue - rebuild container:
docker-compose down
docker-compose up --build frontend
```

### Cannot login
```bash
# Reset admin password
docker-compose exec backend python scripts/create_admin.py

# Check if user exists
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT * FROM users;"
```

### AWS S3 access errors
```bash
# Test AWS credentials
docker-compose exec backend python -c "import boto3; print(boto3.client('s3').list_buckets())"

# Check permissions on S3 bucket
aws s3 ls s3://your-bucket-name
```

### Upload not working
1. Check user has "Write" permission
2. Check bucket policy allows PutObject
3. Check object size < 5GB limit
4. View browser console for errors
5. Check backend logs for detailed errors

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment guide including:
- AWS ECS/Fargate deployment
- RDS PostgreSQL setup
- Application Load Balancer configuration
- IAM Roles Anywhere setup
- SSL/TLS configuration
- Monitoring and logging
- Backup and disaster recovery

## Common Use Cases

### Healthcare Partner Access
- Create users for each partner organization
- Grant access to specific folders (e.g., `partner-a/uploads/`)
- Monitor all file access for compliance
- Regular audit log reviews

### Multi-Department File Sharing
- Create users for each department
- Assign department-specific prefixes
- Read-only access for some departments
- Full access for content owners

### Temporary External Consultant Access
- Create time-limited user accounts
- Grant access to specific project folders
- Revoke access when project completes
- Full audit trail of all actions

## API Documentation

Interactive API documentation available at:
http://localhost:8000/docs

All endpoints require JWT authentication except `/login`.

Example API call:
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"yourpassword"}'

# Get presigned URL for upload
curl -X POST http://localhost:8000/api/v1/s3/presigned-url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bucket_name":"my-bucket","object_key":"file.pdf","operation":"upload"}'
```

## Support & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U s3manager s3manager > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U s3manager s3manager < backup.sql
```

### View Metrics
```bash
# Database size
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT pg_size_pretty(pg_database_size('s3manager'));"

# User count
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT COUNT(*) FROM users;"

# Total audit logs
docker-compose exec db psql -U s3manager -d s3manager -c "SELECT COUNT(*) FROM audit_logs;"
```

## Performance Tips

1. **Large File Uploads**: Files > 100MB should use multipart upload (already supported)
2. **Many Users**: Scale horizontally by running multiple backend instances
3. **Database Performance**: Add indexes if queries are slow
4. **S3 Performance**: Use Transfer Acceleration for large files

## License & Support

This is a proprietary application for internal use at Radiology Partners.
For support, contact DevOps team or open an internal ticket.

## Next Steps

1. ✅ Start the application
2. ✅ Create admin user
3. ✅ Login and explore
4. ✅ Create test users
5. ✅ Assign test permissions
6. ✅ Upload/download test files
7. ✅ Review audit logs
8. 📋 Plan production deployment
9. 🔒 Configure SSL certificates
10. 📊 Setup monitoring alerts

For questions or issues, check the troubleshooting section above or consult [DEPLOYMENT.md](DEPLOYMENT.md).
