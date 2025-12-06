# Production Deployment Guide

## AWS Infrastructure Setup

### Prerequisites
- AWS Account with appropriate permissions
- Terraform installed
- Docker installed
- Domain name (optional, for HTTPS)

### 1. Database Setup (RDS PostgreSQL)

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

The Terraform configuration will create:
- RDS PostgreSQL instance
- VPC with public/private subnets
- Security groups
- IAM roles for ECS
- Application Load Balancer
- ECS cluster

### 2. Configure Secrets

Use AWS Secrets Manager or SSM Parameter Store:

```bash
aws secretsmanager create-secret \
  --name s3-manager/jwt-secret \
  --secret-string "your-random-secret-key"

aws secretsmanager create-secret \
  --name s3-manager/database-url \
  --secret-string "postgresql://user:pass@rds-endpoint:5432/s3manager"
```

### 3. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -t s3-manager-backend ./backend
docker tag s3-manager-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/s3-manager-backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/s3-manager-backend:latest

# Build and push frontend
docker build -t s3-manager-frontend ./frontend
docker tag s3-manager-frontend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/s3-manager-frontend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/s3-manager-frontend:latest
```

### 4. Deploy to ECS

Update ECS task definitions with your ECR image URIs and deploy:

```bash
aws ecs update-service \
  --cluster s3-manager-cluster \
  --service s3-manager-backend \
  --force-new-deployment

aws ecs update-service \
  --cluster s3-manager-cluster \
  --service s3-manager-frontend \
  --force-new-deployment
```

### 5. Create Initial Admin User

Connect to the ECS task:

```bash
aws ecs execute-command \
  --cluster s3-manager-cluster \
  --task TASK_ID \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside the container
python scripts/create_admin.py
```

### 6. Configure SSL/TLS

Use AWS Certificate Manager:

```bash
aws acm request-certificate \
  --domain-name s3manager.yourdomain.com \
  --validation-method DNS
```

Update ALB listener to use HTTPS (port 443) with the certificate.

## IAM Roles Anywhere Setup

For certificate-based authentication (recommended for partner access):

1. Create a Certificate Authority in AWS Certificate Manager Private CA

2. Create IAM role with S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket/*",
        "arn:aws:s3:::your-bucket"
      ]
    }
  ]
}
```

3. Create trust policy for IAM Roles Anywhere:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "rolesanywhere.amazonaws.com"
      },
      "Action": [
        "sts:AssumeRole",
        "sts:TagSession",
        "sts:SetSourceIdentity"
      ]
    }
  ]
}
```

4. Configure the application to use IAM Roles Anywhere:

```bash
export AWS_ROLE_ARN=arn:aws:iam::ACCOUNT:role/S3AccessManagerRole
```

## Monitoring and Logging

### CloudWatch Logs

All application logs are sent to CloudWatch Logs:
- `/aws/ecs/s3-manager-backend` - Backend application logs
- `/aws/ecs/s3-manager-frontend` - Frontend application logs

### CloudWatch Alarms

Set up alarms for:
- ECS service CPU/Memory usage
- RDS database connections
- ALB 5xx errors
- Failed authentication attempts

Example alarm:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name s3-manager-high-cpu \
  --alarm-description "ECS CPU usage > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## Backup and Disaster Recovery

### Database Backups

RDS automated backups are enabled by default (7-day retention).

For manual backups:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier s3-manager-db \
  --db-snapshot-identifier s3-manager-backup-$(date +%Y%m%d)
```

### Application State

The application is stateless. All state is in the database and S3.

## Security Best Practices

1. **Network Security**
   - Use VPC with private subnets for database
   - Restrict security groups to necessary ports
   - Use AWS WAF for ALB

2. **Encryption**
   - Enable RDS encryption at rest
   - Use KMS for S3 bucket encryption
   - Force TLS 1.2+ on ALB

3. **IAM**
   - Use least privilege principle
   - Rotate IAM credentials regularly
   - Enable MFA for admin users

4. **Audit**
   - Enable CloudTrail for all API calls
   - Review audit logs regularly
   - Set up alerts for suspicious activity

## Scaling

### Horizontal Scaling

Update ECS service desired count:

```bash
aws ecs update-service \
  --cluster s3-manager-cluster \
  --service s3-manager-backend \
  --desired-count 3
```

### Auto Scaling

Configure ECS auto scaling based on CPU/Memory:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/s3-manager-cluster/s3-manager-backend \
  --min-capacity 2 \
  --max-capacity 10
```

## Troubleshooting

### Check ECS task logs

```bash
aws logs tail /aws/ecs/s3-manager-backend --follow
```

### Check RDS connections

```bash
aws rds describe-db-instances \
  --db-instance-identifier s3-manager-db \
  --query 'DBInstances[0].Endpoint'
```

### Test S3 access

```bash
aws s3 ls s3://your-bucket/ --profile s3-manager-role
```

## Cost Optimization

1. Use t3/t4g instances for ECS
2. Enable RDS autoscaling storage
3. Use S3 Intelligent-Tiering
4. Set up budget alerts
5. Review CloudWatch Logs retention periods

## Maintenance

### Update application

1. Build new Docker images
2. Push to ECR
3. Update ECS service (force new deployment)
4. Monitor deployment in ECS console

### Database migrations

```bash
# Connect to ECS task
aws ecs execute-command --cluster s3-manager-cluster --task TASK_ID --interactive --command "/bin/bash"

# Run migrations
alembic upgrade head
```

## Support

For issues:
1. Check CloudWatch Logs
2. Review ECS task status
3. Verify RDS connectivity
4. Check IAM permissions
