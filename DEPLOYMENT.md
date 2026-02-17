# PneumoNet AI - Deployment Guide

This guide covers deployment strategies for different environments and platforms.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Google Cloud Run](#google-cloud-run)
5. [Heroku](#heroku)
6. [DigitalOcean](#digitalocean)
7. [Azure](#azure)
8. [Production Best Practices](#production-best-practices)

---

## Local Development

### Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

The API will be available at `http://localhost:5000`

### Testing

```bash
# Run test suite
python test_api.py

# Or test manually with curl
curl http://localhost:5000/health
curl -X POST -F "image=@test_image.jpg" http://localhost:5000/predict
```

---

## Docker Deployment

### Prerequisites
- Docker installed and running
- Docker Compose (optional but recommended)

### Build Image

```bash
# Build Docker image
docker build -t pneumonet-api:latest .

# View image info
docker images pneumonet-api
```

### Run Container

```bash
# Basic run
docker run -p 5000:5000 pneumonet-api:latest

# Run with volume for uploads
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads pneumonet-api:latest

# Run in background
docker run -d -p 5000:5000 --name pneumonet-api pneumonet-api:latest

# View logs
docker logs -f pneumonet-api
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild image
docker-compose up -d --build
```

### Docker on Different Architectures

```bash
# Build for ARM64 (M1/M2 Macs, ARM servers)
docker buildx build --platform linux/arm64 -t pneumonet-api:latest .

# Build for AMD64 and ARM64
docker buildx build --platform linux/amd64,linux/arm64 -t pneumonet-api:latest .
```

---

## AWS Deployment

### Option 1: EC2 Instance

#### Setup

```bash
# 1. Launch Ubuntu 20.04+ EC2 instance
# 2. Connect via SSH

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y git

# Clone repository
git clone your-repo-url
cd PneumoNet-AI

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Nginx
sudo apt install -y nginx

# Start API with Gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app &
```

#### Configure Nginx as Reverse Proxy

Create `/etc/nginx/sites-available/pneumonet`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pneumonet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: AWS Elastic Beanstalk

#### Setup

```bash
# Install EB CLI
pip install awsebcli

# Initialize application
eb init -p python-3.10 pneumonet-api

# Create environment
eb create pneumonet-env

# Deploy
eb deploy

# View logs
eb logs
```

Create `.ebextensions/app_config.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current:$PYTHONPATH
  aws:autoscaling:launchconfiguration:
    EC2KeyName: your-keypair
```

### Option 3: AWS Lambda with API Gateway

Create `lambda_handler.py`:

```python
from mangum import Mangum
from app import app

handler = Mangum(app)
```

Deploy:
```bash
pip install mangum
zip -r lambda.zip .
aws lambda create-function --runtime python3.10 --handler lambda_handler.handler \
    --zip-file fileb://lambda.zip --function-name pneumonet-api
```

---

## Google Cloud Run

### Deployment

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project your-project-id

# Deploy to Cloud Run
gcloud run deploy pneumonet-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --cpu 2 \
  --memory 2Gi \
  --timeout 120 \
  --allow-unauthenticated

# View deployment status
gcloud run services list
gcloud run services describe pneumonet-api --region us-central1
```

### Using Cloud Build

Create `cloudbuild.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/pneumonet-api:$SHORT_SHA', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/pneumonet-api:$SHORT_SHA']
  
  - name: 'gcr.io/cloud-builders/run'
    args: 
      - 'deploy'
      - 'pneumonet-api'
      - '--image=gcr.io/$PROJECT_ID/pneumonet-api:$SHORT_SHA'
      - '--platform=managed'
      - '--region=us-central1'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/pneumonet-api:$SHORT_SHA'
```

Deploy:
```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## Heroku

### Setup

```bash
# Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Add Procfile (already created)
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT app:app" > Procfile

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Environment Variables

```bash
heroku config:set FLASK_ENV=production
heroku config:set CLASSIFICATION_THRESHOLD=0.45
```

### Scaling

```bash
# Scale dynos
heroku ps:scale web=2

# View current setup
heroku ps
```

---

## DigitalOcean

### Deployment with App Platform

```bash
# 1. Push code to GitHub
# 2. Connect GitHub to DigitalOcean
# 3. Create new App
# 4. Select repository and branch
# 5. Configure build command: pip install -r requirements.txt
# 6. Configure run command: gunicorn -w 4 -b 0.0.0.0:5000 app:app
# 7. Set HTTP port to 5000
# 8. Deploy
```

### Deployment with Droplet + Docker

```bash
# 1. Create Ubuntu droplet
# 2. SSH into droplet
# 3. Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
# 4. Clone repository
# 5. Run: docker-compose up -d
```

---

## Azure

### Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name pneumonet-rg --location eastus

# Create container
az container create \
  --resource-group pneumonet-rg \
  --name pneumonet-api \
  --image pneumonet-api:latest \
  --ports 5000 \
  --cpu 2 --memory 2
```

### Azure App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name pneumonet-plan \
  --resource-group pneumonet-rg \
  --sku B2 --is-linux

# Create Web App
az webapp create \
  --resource-group pneumonet-rg \
  --plan pneumonet-plan \
  --name pneumonet-api \
  --runtime "PYTHON|3.10"

# Deploy
az webapp deployment source config-zip \
  --resource-group pneumonet-rg \
  --name pneumonet-api \
  --src deployment.zip
```

---

## Production Best Practices

### Security

1. **Use HTTPS**
   ```bash
   # With Let's Encrypt/Certbot
   sudo apt install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d your-domain.com
   ```

2. **API Authentication** (Optional enhancement)
   ```python
   from functools import wraps
   from flask import request
   
   @app.before_request
   def check_api_key():
       if request.endpoint != 'health':
           key = request.headers.get('X-API-Key')
           if key != os.environ.get('API_KEY'):
               return {'error': 'Unauthorized'}, 401
   ```

3. **Rate Limiting**
   ```bash
   pip install Flask-Limiter
   ```

4. **CORS Configuration**
   ```python
   from flask_cors import CORS
   CORS(app, origins=['https://yourdomain.com'])
   ```

### Monitoring

- **Uptime Monitoring**: Use UptimeRobot, Pingdom, or cloud provider's monitoring
- **Logs**: Aggregate with ELK Stack, Datadog, or CloudWatch
- **Metrics**: Track response time, error rates, prediction counts

### Scaling

1. **Vertical Scaling**: Use larger instances/machines
2. **Horizontal Scaling**: Deploy multiple instances with load balancer

```bash
# Example: Nginx load balancing
upstream pneumonet_api {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://pneumonet_api;
    }
}
```

### Database/Caching (if needed)

Add Redis for caching predictions:

```python
import redis
cache = redis.Redis(host='localhost', port=6379)

# In predict endpoint:
cache_key = hashlib.md5(image_bytes).hexdigest()
cached = cache.get(cache_key)
if cached:
    return json.loads(cached)
```

### Backup & Disaster Recovery

```bash
# Backup model
aws s3 cp pneumonia_model.keras s3://your-bucket/backup/

# Backup uploads
aws s3 sync uploads/ s3://your-bucket/uploads/
```

### Performance Optimization

1. **Enable Caching Headers**
2. **Compress Responses**: Add Gzip
3. **Use CDN**: CloudFront, Cloudflare
4. **GPU Acceleration**: Deploy on GPU instances

### Configuration Management

Use environment variables instead of hardcoding:

```bash
# Set in deployment platform
export FLASK_ENV=production
export MODEL_PATH=/opt/models/pneumonia_model.keras
export CLASSIFICATION_THRESHOLD=0.45
```

---

## Monitoring & Logging

### Application Logging

```python
import logging
logging.basicConfig(filename='api.log', level=logging.INFO)
```

### System Monitoring

```bash
# CPU/Memory usage
htop

# Disk usage
df -h

# Network
netstat -an | grep LISTEN
```

### Health Checks

Most cloud platforms support health checks:

- **Google Cloud Run**: Uses `/health` endpoint
- **AWS ECS**: Configure in task definition
- **Heroku**: Add Dynos Metadata

---

## Troubleshooting Deployment

### Model Not Found

```bash
# Verify file exists
ls -la pneumonia_model.keras

# Check path in app.py
MODEL_PATH = 'pneumonia_model.keras'  # or use absolute path
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
gunicorn -b 0.0.0.0:8000 app:app
```

### Out of Memory

```bash
# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### High Latency

- Check network connectivity
- Monitor model inference time: `time curl -X POST -F "image=@test.jpg" http://localhost:5000/predict`
- Reduce image size or batch size
- Enable GPU if available

---

## Cost Optimization

| Platform | Estimated Monthly Cost |
|----------|----------------------|
| AWS EC2 (t3.small) | $20-30 |
| Google Cloud Run | $1-10 (pay-per-use) |
| Heroku (Eco) | $7-50 |
| DigitalOcean Droplet | $5-20 |

Choose based on:
- Traffic patterns (Cloud Run for spikey, EC2 for sustained)
- Budget constraints
- Compliance requirements
- Team expertise

---

**Created**: February 2024  
**Last Updated**: February 2024  
**Version**: 1.0.0
