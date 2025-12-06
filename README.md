# S3 Access Manager

A secure web application for managing multi-user S3 access without distributing AWS credentials. Built for HIPAA-compliant environments.

## Features

- 🔐 Secure authentication with JWT tokens
- 👥 User management with role-based access
- 📁 Fine-grained S3 bucket/prefix permissions
- 📊 Admin dashboard with user and permission management
- 📤 Direct S3 uploads using presigned URLs
- 📝 Complete audit logging
- 🔒 HIPAA-compliant architecture

## Architecture

```
Frontend (React) → Backend (FastAPI) → AWS S3
                         ↓
                   PostgreSQL (User/Permissions)
                         ↓
                   CloudWatch Logs (Audit Trail)
```

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL (User/Permission storage)
- boto3 (AWS SDK)
- JWT authentication
- Alembic (Database migrations)

**Frontend:**
- React 18
- Material-UI (MUI)
- Axios for API calls
- React Router for navigation
- Context API for state management

**Infrastructure:**
- Docker & Docker Compose
- AWS IAM Roles
- S3 with KMS encryption
- CloudWatch for logging

## Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS Account with appropriate permissions
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Setup

```bash
# Environment setup
cp .env.example .env
# Edit .env with your AWS credentials and settings
```

### 2. Start with Docker

```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Create Admin User

```bash
docker-compose exec backend python scripts/create_admin.py
```

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://s3manager:password@db:5432/s3manager

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_REGION=us-east-1
AWS_ROLE_ARN=arn:aws:iam::ACCOUNT:role/S3AccessManagerRole

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### AWS IAM Role Policy

The application needs an IAM role with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket/*",
        "arn:aws:s3:::your-bucket"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:region:account:key/your-key-id"
    }
  ]
}
```

## Project Structure

```
s3-access-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security, dependencies
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py
│   ├── alembic/          # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── contexts/     # React contexts
│   │   └── App.js
│   └── package.json
├── terraform/            # Infrastructure as Code
├── docker-compose.yml
└── README.md
```

## Usage

### Admin Workflow

1. **Login** as admin
2. **Add Users** - Create user accounts with email/password
3. **Assign Permissions** - Map users to S3 buckets/prefixes
4. **Monitor Activity** - View audit logs and user activity

### User Workflow

1. **Login** with credentials
2. **View Accessible Buckets** - See permitted S3 locations
3. **Upload Files** - Drag & drop or browse files
4. **Download Files** - Browse and download from permitted locations

## Security Features

- ✅ No AWS credentials exposed to users
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Presigned URLs with expiration
- ✅ Complete audit trail
- ✅ HTTPS enforcement
- ✅ Session timeout
- ✅ Rate limiting

## HIPAA Compliance

- ✅ Encryption in transit (TLS 1.2+)
- ✅ Encryption at rest (S3 KMS)
- ✅ Access logging
- ✅ Audit trail
- ✅ User authentication & authorization
- ✅ Automatic session timeout
- ✅ No PHI in application logs

## Deployment

### Production Deployment (AWS)

1. **Setup RDS PostgreSQL**
2. **Deploy to ECS/EKS** or EC2 with Auto Scaling
3. **Configure ALB** with SSL certificate
4. **Setup CloudWatch** for monitoring
5. **Configure IAM Roles Anywhere** for certificate-based auth

See `terraform/` directory for IaC templates.

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
docker-compose exec backend python scripts/check_db.py
```

### View Logs

```bash
# Application logs
docker-compose logs -f backend

# Audit logs
docker-compose exec backend python scripts/view_audit_logs.py
```

### Database Backup

```bash
docker-compose exec db pg_dump -U s3manager s3manager > backup.sql
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔐 Credential Security

Your AWS credentials are stored with **maximum security** using industry-standard encryption:

1. **Encryption at Rest**:
   - Access Keys and Secret Keys are **encrypted** before being stored in the database.
   - We use **Fernet symmetric encryption** (AES-128 in CBC mode with SHA256 HMAC).
   - The encryption key is derived from your `SECRET_KEY` environment variable.

2. **Zero-Knowledge Database**:
   - Even if someone gains access to the database, they **cannot read** your AWS credentials.
   - They will only see random encrypted strings (e.g., `gAAAA...`).

3. **In-Memory Decryption**:
   - Keys are decrypted **only in memory** when needed (e.g., to list files).
   - Plain text keys are **never written** to disk or logs.

**⚠️ IMPORTANT:**
- **Protect your `.env` file!** It contains the `SECRET_KEY` required to decrypt your credentials.
- If you lose your `SECRET_KEY`, all stored S3 connections will become permanently unreadable.
- **NEVER commit your `.env` file** to version control.

## Troubleshooting

### Common Issues

**1. "Failed to upload files" / "Network Error"**
- **Cause:** Missing CORS configuration on S3 bucket.
- **Fix:** Apply CORS policy to your bucket:
  ```bash
  aws s3api put-bucket-cors --bucket your-bucket --cors-configuration file://cors.json
  ```

**2. "InvalidAccessKeyId" Error**
- **Cause:** The S3 Connection has invalid credentials, or the Permission is using the "Default" connection which has placeholder values.
- **Fix:**
  1. Go to **S3 Connections** in Admin Dashboard.
  2. Create/Update a connection with valid AWS keys.
  3. Go to **Permissions**.
  4. Edit the user's permission and select the correct **S3 Connection**.

**3. Audit Logs Not Showing**
- **Cause:** Backend serialization issue (Fixed in v1.1).
- **Fix:** Ensure you are running the latest backend version.
- **Check:** Open browser console (F12) to see debug logs.

**4. Database connection errors:**
```bash
docker-compose down -v
docker-compose up -d
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review API documentation: http://localhost:8000/docs
3. Check AWS CloudWatch logs

## License

Proprietary - Radiology Partners Internal Use
