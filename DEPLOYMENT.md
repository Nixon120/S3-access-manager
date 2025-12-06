# Production Deployment Guide (EC2)

This guide explains how to deploy the KGS S3 Manager to a single AWS EC2 instance.

## Prerequisites
1.  **AWS Account**
2.  **EC2 Instance**: Ubuntu 22.04 LTS (t3.small or t3.medium recommended)
3.  **Domain Name** (Optional, but recommended for SSL)

## Step 1: Prepare the EC2 Instance

1.  **Launch Instance**: Launch an Ubuntu 22.04 instance.
2.  **Security Group**: Open ports:
    *   22 (SSH) - Your IP only
    *   80 (HTTP) - Anywhere
    *   443 (HTTPS) - Anywhere (if using SSL)

3.  **SSH into the instance**:
    ```bash
    ssh -i key.pem ubuntu@your-ec2-ip
    ```

4.  **Install Docker & Docker Compose**:
    ```bash
    # Update packages
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg

    # Install Docker
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add user to docker group (avoid sudo)
    sudo usermod -aG docker $USER
    # Log out and back in for this to take effect
    exit
    ```

## Step 2: Deploy the Application

1.  **Clone the Repository** (or copy files):
    ```bash
    git clone <your-repo-url> app
    cd app
    ```

2.  **Create Production Environment Config**:
    Create a `.env` file with your production secrets.
    ```bash
    nano .env
    ```
    Paste your `.env` content (ensure `DEBUG=False` and `ENVIRONMENT=production`).

3.  **Start the Application**:
    Use the production compose file.
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build
    ```

4.  **Verify**:
    Visit `http://your-ec2-ip` in your browser. You should see the KGS Login page.

## Step 3: Database Backups (Crucial!)

Since the database lives on the EC2 instance, you MUST back it up.

1.  **Create a backup script** `backup.sh`:
    ```bash
    #!/bin/bash
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    docker compose -f /home/ubuntu/app/docker-compose.prod.yml exec -T db pg_dump -U s3manager s3manager > /home/ubuntu/backups/db_backup_$TIMESTAMP.sql
    # Optional: Upload to S3
    # aws s3 cp /home/ubuntu/backups/db_backup_$TIMESTAMP.sql s3://your-backup-bucket/
    ```

2.  **Add to Crontab**:
    ```bash
    crontab -e
    # Run every day at 2 AM
    0 2 * * * /bin/bash /home/ubuntu/app/backup.sh
    ```

## Step 4: SSL with AWS ACM (Recommended)

Since you have a certificate in **AWS Certificate Manager (ACM)**, you **cannot** install it directly on the EC2 instance. You must use an **Application Load Balancer (ALB)** to handle the SSL encryption.

### Architecture
`User (HTTPS)` -> `AWS ALB (SSL Termination)` -> `EC2 Instance (HTTP port 80)`

### Configuration Steps

1.  **Create a Target Group**:
    *   Go to EC2 Console -> **Target Groups** -> **Create target group**.
    *   Choose **Instances**.
    *   **Protocol**: HTTP, **Port**: 80.
    *   **VPC**: Select your VPC.
    *   **Health Check**: Path `/health` (or `/`).
    *   **Register Targets**: Select your EC2 instance and click "Include as pending below".
    *   Click **Create**.

2.  **Create an Application Load Balancer (ALB)**:
    *   Go to EC2 Console -> **Load Balancers** -> **Create Load Balancer**.
    *   Select **Application Load Balancer**.
    *   **Scheme**: Internet-facing.
    *   **Network**: Select your VPC and at least two subnets (availability zones).
    *   **Security Group**: Create a new SG for the ALB (e.g., `alb-sg`) allowing:
        *   Inbound HTTP (80) from `0.0.0.0/0`
        *   Inbound HTTPS (443) from `0.0.0.0/0`

3.  **Configure Listeners**:
    *   **Listener 1 (HTTPS)**:
        *   Protocol: HTTPS, Port: 443.
        *   **Default Action**: Forward to your Target Group.
        *   **Secure Listener Settings**: Select your **ACM Certificate**.
    *   **Listener 2 (HTTP)**:
        *   Protocol: HTTP, Port: 80.
        *   **Default Action**: Redirect to HTTPS (Port 443).

4.  **Update EC2 Security Group**:
    *   Go to your **EC2 Instance's Security Group**.
    *   Edit Inbound Rules.
    *   **Remove** the rule allowing Port 80 from `0.0.0.0/0`.
    *   **Add** a rule allowing Port 80 from **Source: Custom -> Select your ALB Security Group** (`alb-sg`).
    *   *This ensures only the Load Balancer can talk to your app.*

5.  **Update DNS (Route 53)**:
    *   Go to Route 53.
    *   Create an **A Record** for your domain (e.g., `app.yourdomain.com`).
    *   Toggle **Alias** to Yes.
    *   Route traffic to: **Alias to Application and Classic Load Balancer**.
    *   Select your region and the ALB you just created.

6.  **Verify**:
    *   Visit `https://app.yourdomain.com`.
    *   It should load securely with the lock icon!
