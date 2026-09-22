# Deployment Guide

## Overview

This guide covers deploying the GeoPilot Traffic Surveillance system to production.

## Prerequisites

- Python 3.9+
- Domain name (for production)
- SSL certificate
- Server with 4GB+ RAM
- GPU (optional, for faster inference)

## Deployment Options

### Option 1: Traditional Server

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.9 python3.9-venv -y

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

#### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/your-org/geopilot.git
cd geopilot/voice-traffic-surveillance

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values
```

#### 3. Systemd Service

Create `/etc/systemd/system/geopilot-traffic.service`:

```ini
[Unit]
Description=GeoPilot Traffic Surveillance Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/geopilot/voice-traffic-surveillance
Environment="PATH=/opt/geopilot/voice-traffic-surveillance/venv/bin"
ExecStart=/opt/geopilot/voice-traffic-surveillance/venv/bin/uvicorn tools.traffic_server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/geopilot-browser.service`:

```ini
[Unit]
Description=GeoPilot Voice Agent Browser Server
After=network.target geopilot-traffic.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/geopilot/voice-traffic-surveillance
Environment="PATH=/opt/geopilot/voice-traffic-surveillance/venv/bin"
ExecStart=/opt/geopilot/voice-traffic-surveillance/venv/bin/uvicorn deployment.browser.server:app --host 0.0.0.0 --port 3000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 4. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable geopilot-traffic geopilot-browser
sudo systemctl start geopilot-traffic geopilot-browser
```

### Option 2: Docker

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 3000

# Start script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
```

#### docker-entrypoint.sh

```bash
#!/bin/bash
set -e

# Start traffic server
uvicorn tools.traffic_server:app --host 0.0.0.0 --port 8000 --workers 4 &

# Start browser server
uvicorn deployment.browser.server:app --host 0.0.0.0 --port 3000 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  geopilot:
    build: .
    ports:
      - "8000:8000"
      - "3000:3000"
    environment:
      - ASSEMBLYAI_API_KEY=${ASSEMBLYAI_API_KEY}
      - TRAFFIC_SERVER_URL=http://localhost:8000
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Option 3: Cloud Deployment

#### AWS EC2

```bash
# Launch EC2 instance (t3.medium or larger)
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow "Traditional Server" setup above
```

#### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/geopilot', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/geopilot']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'geopilot'
      - '--image'
      - 'gcr.io/$PROJECT_ID/geopilot'
      - '--region'
      - 'us-central1'
      - '--port'
      - '8000'
```

## SSL Configuration

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name geopilot.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name geopilot.com;

    ssl_certificate /etc/letsencrypt/live/geopilot.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/geopilot.com/privkey.pem;

    # Traffic Server
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Browser Server
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Let's Encrypt SSL

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d geopilot.com
```

## Monitoring

### Health Checks

```bash
# Traffic Server
curl http://localhost:8000/health

# Browser Server
curl http://localhost:3000/health
```

### Logs

```bash
# View logs
sudo journalctl -u geopilot-traffic -f
sudo journalctl -u geopilot-browser -f

# Log files
tail -f logs/traffic_surveillance.log
```

### Prometheus Metrics

Add to `traffic_server.py`:

```python
from prometheus_client import make_aspricorn_app

app.mount("/metrics", make_asgi_app())
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  geopilot:
    deploy:
      replicas: 3
    ports:
      - "8000-8002:8000"
```

### Load Balancer

```nginx
upstream geopilot {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    location /api/ {
        proxy_pass http://geopilot;
    }
}
```

## Backup

### Database Backup

```bash
# If using PostgreSQL
pg_dump -U postgres geopilot > backup.sql
```

### Configuration Backup

```bash
tar -czf config-backup.tar.gz config/ agents/ .env
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

#### Permission Denied

```bash
sudo chown -R www-data:www-data /opt/geopilot
```

#### Memory Issues

```bash
# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Related Pages

- [[Getting Started]]
- [[Configuration Guide]]
- [[Troubleshooting]]

## Tags

#deployment #production #docker #nginx #ssl

---

*Part of [[GeoPilot Traffic Surveillance]]*
