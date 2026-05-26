# Leceil Morgan Corp - Deployment & Production Guide

## Overview
This guide covers deployment strategies for the Workflow Automation & Document Management System in production environments.

## Deployment Architectures

### 1. Monolithic Deployment (Single Server)

**Best for:** Small to medium organizations

```
┌─────────────────────────────────┐
│  Single Server (Linux/Windows)  │
│                                 │
│  ┌─────────────────────────────┐│
│  │  Python API (Gunicorn)      ││
│  │  - Workflow Engine          ││
│  │  - Form Processing          ││
│  │  - Document Management      ││
│  │  - Notifications            ││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │  PostgreSQL/MongoDB         ││
│  │  - Workflows                ││
│  │  - Forms                    ││
│  │  - Documents                ││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │  File Storage               ││
│  │  - Local /documents folder  ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

### 2. Microservices Deployment

**Best for:** Large enterprises with high availability needs

```
┌────────────────────────────────────────────┐
│         Kubernetes Cluster                 │
│                                            │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ Workflow    │  │ Form        │         │
│  │ Service     │  │ Service     │         │
│  └─────────────┘  └─────────────┘         │
│                                            │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ Document    │  │ Notification│         │
│  │ Service     │  │ Service     │         │
│  └─────────────┘  └─────────────┘         │
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │  Redis (Cache & Message Queue)      │  │
│  └─────────────────────────────────────┘  │
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │  PostgreSQL (Persistent Storage)    │  │
│  └─────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows Server 2019+, or macOS
- **Python**: 3.8+
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 20GB minimum (depending on document volume)
- **Database**: PostgreSQL 12+ or MongoDB 4.4+

### Required Packages
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql

# CentOS/RHEL
sudo yum install python3-pip postgresql-server

# Windows (using chocolatey)
choco install python postgresql
```

## Production Setup

### 1. Environment Configuration

Create `.env` file:
```env
# Application
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/workflow_db
MONGODB_URL=mongodb://localhost:27017/workflows

# Storage
DOCUMENTS_PATH=/var/www/documents
TEMP_PATH=/var/www/temp

# Cloud Integration
SHAREPOINT_SITE_URL=https://company.sharepoint.com
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-secret

ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-secret

# Email
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=notifications@company.com
SMTP_PASSWORD=your-password

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Teams Integration
TEAMS_WEBHOOK_URL=https://company.webhook.office.com/webhookb2/...

# Security
CORS_ORIGINS=https://company.com,https://portal.company.com
API_KEY_REQUIRED=True
API_KEY_HEADER=X-API-Key

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/workflow-automation/app.log

# Performance
WORKER_PROCESSES=4
MAX_UPLOAD_SIZE=104857600  # 100MB
REQUEST_TIMEOUT=300  # 5 minutes
```

### 2. Database Setup

#### PostgreSQL
```sql
-- Create database
CREATE DATABASE workflow_db;

-- Create user
CREATE USER workflow_user WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE workflow_db TO workflow_user;

-- Connect and create tables
\c workflow_db
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) UNIQUE NOT NULL,
    definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    metadata JSONB,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE form_submissions (
    id SERIAL PRIMARY KEY,
    submission_id VARCHAR(255) UNIQUE NOT NULL,
    form_id VARCHAR(255) NOT NULL,
    form_data JSONB NOT NULL,
    submitter_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'submitted',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_submissions_form ON form_submissions(form_id);
```

### 3. Install & Configure

```bash
# Clone/download project
cd /var/www/workflow-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-production.txt

# Install production dependencies
pip install gunicorn psycopg2-binary pymongo redis celery

# Create directories
mkdir -p /var/www/documents /var/log/workflow-automation
chmod 755 /var/www/documents

# Initialize database
psql -U workflow_user -d workflow_db -f database_schema.sql
```

### 4. Web Server Configuration

#### Gunicorn Setup
Create `/etc/systemd/system/workflow-automation.service`:
```ini
[Unit]
Description=Leceil Morgan Workflow Automation
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/workflow-automation
Environment="PATH=/var/www/workflow-automation/venv/bin"
ExecStart=/var/www/workflow-automation/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile /var/log/workflow-automation/access.log \
    --error-logfile /var/log/workflow-automation/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable workflow-automation
sudo systemctl start workflow-automation
```

#### Nginx Configuration
Create `/etc/nginx/sites-available/workflow-automation`:
```nginx
upstream workflow_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.leceilmorgan.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.leceilmorgan.com;

    ssl_certificate /etc/letsencrypt/live/api.leceilmorgan.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.leceilmorgan.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://workflow_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /static/ {
        alias /var/www/workflow-automation/static/;
        expires 30d;
    }

    location /documents/ {
        alias /var/www/documents/;
        internal;  # Nginx serves files directly
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/workflow-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL/TLS Certificate

```bash
# Using Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.leceilmorgan.com

# Certificate will be at:
# /etc/letsencrypt/live/api.leceilmorgan.com/
```

### 6. Monitoring & Logging

#### ELK Stack (Elasticsearch, Logstash, Kibana)

Install Elasticsearch, Logstash, and Kibana for centralized logging:

```yaml
# logstash.conf
input {
  file {
    path => "/var/log/workflow-automation/*.log"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{WORD:level} - %{GREEDYDATA:message}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "workflow-automation-%{+YYYY.MM.dd}"
  }
}
```

#### Prometheus Metrics

```python
# Add to main app
from prometheus_client import Counter, Histogram, generate_latest

workflow_executions = Counter('workflow_executions_total', 'Total workflow executions')
workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution duration')
form_submissions = Counter('form_submissions_total', 'Total form submissions')
```

### 7. Backup & Disaster Recovery

#### Database Backups
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/workflow-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump -U workflow_user workflow_db | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Document backup
tar -czf "$BACKUP_DIR/documents_$TIMESTAMP.tar.gz" /var/www/documents/

# Upload to S3
aws s3 cp "$BACKUP_DIR/" "s3://company-backups/workflow-automation/" --recursive

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete
```

Schedule with cron:
```
0 2 * * * /var/www/workflow-automation/backup.sh
```

### 8. Security Hardening

```bash
# File permissions
sudo chown -R www-data:www-data /var/www/workflow-automation
sudo chmod 750 /var/www/workflow-automation
sudo chmod 700 /var/www/documents

# Firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Fail2ban (prevent brute force)
sudo apt-get install fail2ban
sudo systemctl enable fail2ban

# SELinux (optional)
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/var/www/documents(/.*)?"
sudo restorecon -R /var/www/documents
```

### 9. Health Checks & Monitoring

```bash
# health_check.sh
#!/bin/bash

API_URL="https://api.leceilmorgan.com/health"

response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ $response -eq 200 ]; then
    echo "✓ API is healthy"
    exit 0
else
    echo "✗ API is unhealthy (HTTP $response)"
    # Send alert
    mail -s "Workflow API Alert" ops@company.com <<< "API health check failed"
    exit 1
fi
```

Schedule checks:
```
*/5 * * * * /var/www/workflow-automation/health_check.sh
```

## Performance Tuning

### Database Optimization
```sql
-- Enable query optimization
ANALYZE;

-- Create indexes for common queries
CREATE INDEX idx_workflows_status ON workflow_executions(status);
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_submissions_form_date ON form_submissions(form_id, created_at);
```

### Caching
```python
# Configure Redis cache
from functools import lru_cache
import redis

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

@lru_cache(maxsize=128)
def get_form_schema(form_id):
    cached = cache.get(f"form:{form_id}")
    if cached:
        return json.loads(cached)
    # Load from DB and cache
    ...
```

### Async Processing
```python
# Use Celery for long-running tasks
from celery import Celery

app = Celery('workflow_automation')

@app.task
def process_large_document(document_id):
    # Long-running task executed asynchronously
    ...
```

## Troubleshooting

### Common Issues

**API Won't Start:**
```bash
# Check logs
journalctl -u workflow-automation -n 50

# Check port availability
sudo lsof -i :8000
```

**Database Connection Issues:**
```bash
# Test connection
psql -U workflow_user -d workflow_db -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql
```

**Disk Space Issues:**
```bash
# Check disk usage
df -h

# Clean up old documents
find /var/www/documents -mtime +365 -delete

# Compress old logs
gzip /var/log/workflow-automation/*.log.?*
```

## Updates & Maintenance

```bash
# Backup before updating
/var/www/workflow-automation/backup.sh

# Update code
cd /var/www/workflow-automation
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements-production.txt

# Restart service
sudo systemctl restart workflow-automation
```

---

**Last Updated:** May 26, 2026  
**Version:** 1.0.0
