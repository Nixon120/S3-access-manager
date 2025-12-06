# S3 Access Manager - Architecture Documentation

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         AWS Cloud                             │
│                                                               │
│  ┌─────────────┐         ┌──────────────┐                   │
│  │   Route 53  │────────▶│     ALB      │                   │
│  │     DNS     │         │  (Load       │                   │
│  └─────────────┘         │  Balancer)   │                   │
│                          └──────┬───────┘                    │
│                                 │                             │
│                    ┌────────────┼────────────┐               │
│                    │            │            │               │
│                    ▼            ▼            ▼               │
│              ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│              │   ECS   │  │   ECS   │  │   ECS   │          │
│              │  Task   │  │  Task   │  │  Task   │          │
│              │         │  │         │  │         │          │
│              │Backend 1│  │Backend 2│  │Frontend │          │
│              └────┬────┘  └────┬────┘  └─────────┘          │
│                   │            │                             │
│                   └─────┬──────┘                             │
│                         │                                    │
│                         ▼                                    │
│                  ┌─────────────┐                             │
│                  │     RDS     │                             │
│                  │ PostgreSQL  │                             │
│                  └─────────────┘                             │
│                                                               │
│  ┌───────────────────────────────────────────────┐          │
│  │              S3 Buckets                        │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │          │
│  │  │ Bucket A │  │ Bucket B │  │ Bucket C │   │          │
│  │  └──────────┘  └──────────┘  └──────────┘   │          │
│  └───────────────────────────────────────────────┘          │
│                                                               │
│  ┌────────────────┐                                          │
│  │   CloudWatch   │ ← Logs & Metrics                        │
│  │   Logs/Alarms  │                                          │
│  └────────────────┘                                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React Application)

**Technology Stack:**
- React 18
- Material-UI (MUI)
- React Router
- Axios for API calls
- React Dropzone for file uploads

**Key Features:**
- Responsive design
- Role-based UI (Admin vs User views)
- Real-time file upload progress
- Drag-and-drop file uploads
- Session management with JWT

**Components:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.js           # Main layout with navigation
│   │   ├── FileBrowser.js      # S3 file listing
│   │   └── FileUploadDialog.js # Upload interface
│   ├── pages/
│   │   ├── LoginPage.js        # Authentication
│   │   ├── DashboardPage.js    # Main dashboard
│   │   ├── UsersPage.js        # User management (admin)
│   │   ├── PermissionsPage.js  # Permission management (admin)
│   │   └── AuditPage.js        # Audit logs (admin)
│   ├── contexts/
│   │   └── AuthContext.js      # Authentication state
│   └── services/
│       └── api.js              # API client
```

### 2. Backend (FastAPI Application)

**Technology Stack:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- PostgreSQL
- boto3 (AWS SDK)
- JWT authentication
- Alembic for migrations

**API Architecture:**
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── security.py        # Authentication/Authorization
│   │   └── database.py        # Database connection
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── permission.py      # Permission model
│   │   └── audit_log.py       # Audit log model
│   ├── schemas.py             # Pydantic schemas
│   ├── services/
│   │   ├── s3_service.py      # S3 operations
│   │   ├── permission_service.py  # Permission checks
│   │   └── audit_service.py   # Audit logging
│   ├── api/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management
│   │   ├── permissions.py     # Permission management
│   │   ├── s3.py              # S3 operations
│   │   └── audit.py           # Audit logs
│   └── main.py                # Application entry point
```

**API Endpoints:**

**Authentication:**
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password

**Users (Admin Only):**
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user details
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

**Permissions (Admin Only):**
- `GET /api/v1/permissions` - List permissions
- `GET /api/v1/permissions/my-permissions` - Get current user permissions
- `POST /api/v1/permissions` - Create permission
- `PUT /api/v1/permissions/{id}` - Update permission
- `DELETE /api/v1/permissions/{id}` - Delete permission

**S3 Operations:**
- `POST /api/v1/s3/presigned-url` - Generate presigned URL
- `GET /api/v1/s3/list/{bucket}` - List objects
- `GET /api/v1/s3/buckets` - List accessible buckets
- `DELETE /api/v1/s3/object/{bucket}/{key}` - Delete object

**Audit Logs (Admin Only):**
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/audit/my-activity` - Get personal activity
- `GET /api/v1/audit/stats` - Get system statistics
- `GET /api/v1/audit/user-stats/{id}` - Get user statistics

### 3. Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    last_login TIMESTAMP
);
```

**Permissions Table:**
```sql
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bucket_name VARCHAR NOT NULL,
    prefix VARCHAR DEFAULT '',
    can_read BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_list BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**Audit Logs Table:**
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR NOT NULL,
    bucket_name VARCHAR NOT NULL,
    object_key VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    ip_address VARCHAR,
    user_agent TEXT,
    metadata JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Security Architecture

**Authentication Flow:**
```
1. User submits credentials
   ↓
2. Backend validates credentials
   ↓
3. Backend generates JWT token (expires in 30 min)
   ↓
4. Frontend stores token in localStorage
   ↓
5. Frontend includes token in all API requests
   ↓
6. Backend validates token on each request
```

**Authorization Flow:**
```
1. User requests S3 operation
   ↓
2. Backend checks user permissions in database
   ↓
3. If authorized:
   - Backend generates presigned S3 URL
   - URL is valid for 1 hour
   - User uploads/downloads directly to/from S3
   ↓
4. Backend logs action to audit_logs table
```

**Security Layers:**
1. **Network Level**: VPC, Security Groups, Private Subnets
2. **Application Level**: JWT tokens, Password hashing (bcrypt)
3. **Data Level**: Encryption at rest (S3 KMS), Encryption in transit (TLS)
4. **Audit Level**: Complete logging of all actions

### 5. S3 Access Pattern

**Presigned URL Flow:**
```
┌──────────┐                  ┌──────────┐
│  Browser │                  │  Backend │
└────┬─────┘                  └────┬─────┘
     │                             │
     │  1. Request upload URL      │
     │────────────────────────────▶│
     │                             │
     │                        2. Check
     │                        permissions
     │                             │
     │                        3. Generate
     │                        presigned URL
     │                             │
     │  4. Return presigned URL    │
     │◀────────────────────────────│
     │                             │
     │                             │
     │         ┌─────────────┐     │
     │         │   AWS S3    │     │
     │         └──────┬──────┘     │
     │                │            │
     │  5. Upload     │            │
     │  directly      │            │
     │───────────────▶│            │
     │                │            │
     │  6. Success    │            │
     │◀───────────────│            │
     │                             │
     │  7. Log action              │
     │────────────────────────────▶│
```

**Why Presigned URLs?**
- No AWS credentials exposed to users
- Direct S3 access (faster, no proxy)
- Time-limited access (1 hour default)
- Server-side permission enforcement
- Complete audit trail

### 6. Deployment Architecture

**Development (Docker Compose):**
```
┌─────────────────────────────────────┐
│         Docker Host                  │
│                                      │
│  ┌──────────┐  ┌──────────┐        │
│  │ Frontend │  │ Backend  │        │
│  │   :3000  │  │   :8000  │        │
│  └────┬─────┘  └────┬─────┘        │
│       │             │               │
│       └──────┬──────┘               │
│              │                      │
│      ┌───────▼────────┐             │
│      │   PostgreSQL   │             │
│      │      :5432     │             │
│      └────────────────┘             │
│                                      │
└─────────────────────────────────────┘
           │
           │ AWS API Calls
           ▼
      ┌─────────┐
      │ AWS S3  │
      └─────────┘
```

**Production (AWS ECS):**
```
┌───────────────────────────────────────────┐
│                AWS ECS                     │
│                                            │
│  ┌────────────────────────────────────┐  │
│  │      ALB (Port 80/443)             │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
│      ┌────────┴────────┐                 │
│      │                 │                 │
│  ┌───▼───┐        ┌───▼───┐             │
│  │Backend│        │Backend│             │
│  │ Task  │        │ Task  │             │
│  └───┬───┘        └───┬───┘             │
│      │                │                  │
│      └────────┬───────┘                  │
│               │                           │
│               ▼                           │
│       ┌──────────────┐                   │
│       │  RDS         │                   │
│       │ PostgreSQL   │                   │
│       └──────────────┘                   │
│                                            │
└───────────────────────────────────────────┘
               │
               │ AWS API
               ▼
         ┌──────────┐
         │  S3      │
         │ Buckets  │
         └──────────┘
```

### 7. Monitoring & Observability

**Logging Stack:**
- Application logs → CloudWatch Logs
- S3 access logs → S3 Access Logging
- AWS API calls → CloudTrail

**Metrics:**
- ECS CPU/Memory utilization
- RDS connections and queries
- ALB request count and latency
- S3 request metrics

**Alerts:**
- High CPU/Memory usage
- Database connection errors
- Failed authentication attempts
- 5xx errors on ALB

### 8. Data Flow Examples

**File Upload Flow:**
1. User drags file to browser
2. Frontend requests presigned URL from backend
3. Backend checks user permissions
4. Backend generates presigned POST URL
5. Frontend uploads file directly to S3
6. S3 returns success
7. Backend logs action to audit_logs

**File Download Flow:**
1. User clicks download button
2. Frontend requests presigned URL from backend
3. Backend checks user permissions
4. Backend generates presigned GET URL
5. Frontend opens URL in new tab
6. Browser downloads file from S3
7. Backend logs action to audit_logs

**Permission Check:**
1. User requests access to `bucket-a/folder-b/file.pdf`
2. Backend queries permissions table for user
3. Backend finds permission for `bucket-a` with prefix `folder-b/`
4. Backend checks if `file.pdf` starts with `folder-b/`
5. Backend checks if user has required action (read/write/delete)
6. If all checks pass, operation proceeds

## Performance Considerations

### Scalability
- **Horizontal scaling**: Add more ECS tasks
- **Database**: RDS read replicas for read-heavy workloads
- **S3**: Transfer Acceleration for large files
- **Caching**: CloudFront for static assets

### Optimization
- Use connection pooling for database
- Implement pagination for large lists
- Lazy load file listings
- Compress API responses
- Use S3 multipart upload for files > 100MB

## Security Considerations

### HIPAA Compliance Checklist
✅ Encryption in transit (TLS 1.2+)
✅ Encryption at rest (S3 KMS, RDS encryption)
✅ Access controls (IAM, application permissions)
✅ Audit logging (all actions logged)
✅ User authentication (JWT with password hashing)
✅ Session management (30-minute timeout)
✅ No PHI in logs

### Additional Security Measures
- Regular security updates
- Penetration testing
- Vulnerability scanning
- DDoS protection (AWS Shield)
- Web Application Firewall (AWS WAF)

## Disaster Recovery

### Backup Strategy
- RDS automated backups (7-day retention)
- S3 versioning enabled
- Database snapshots before major changes
- Configuration in version control

### Recovery Procedures
1. **Database failure**: Restore from RDS snapshot
2. **Application failure**: Deploy previous version
3. **S3 data loss**: Restore from versioning
4. **Region failure**: Deploy to secondary region

## Cost Optimization

### Cost Breakdown
- ECS Fargate: $40-100/month (2 tasks)
- RDS t3.micro: $15-30/month
- ALB: $20-40/month
- S3 storage: Variable (based on usage)
- Data transfer: Variable (based on usage)

**Estimated monthly cost**: $75-170 + storage/transfer

### Cost Reduction Strategies
- Use Spot instances for non-critical tasks
- S3 Intelligent-Tiering for infrequent access
- CloudWatch Logs retention policies
- Right-size RDS instance
- Use Reserved Instances for predictable workloads
