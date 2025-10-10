# Groq Speech Solution - Deployment Guide

> **⚠️ Important**: This deployment guide is for **demonstration and testing purposes**. For actual production deployments, additional security hardening, monitoring, scaling configuration, and thorough testing are required.

Complete guide for deploying the Groq Speech Solution in various environments.

## 📋 Table of Contents

1. [Deployment Options](#deployment-options)
2. [Docker Local Deployment](#docker-local-deployment)
3. [GCP Cloud Run Deployment](#gcp-cloud-run-deployment)
4. [GKE GPU Deployment](#gke-gpu-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## 🚀 Deployment Options

The Groq Speech Solution supports multiple deployment options:

| Option | Best For | GPU Support | Complexity | Cost |
|--------|----------|-------------|------------|------|
| **Docker Local** | Development, testing | Optional | Low | None |
| **GCP Cloud Run** | Production (CPU) | No | Low | Pay-per-use |
| **GKE GPU** | Production (GPU) | Yes | Medium | Higher |

### Quick Comparison

**Docker Local:**
- ✅ Quick setup for development
- ✅ Optional GPU support
- ✅ Hot reload for development
- ❌ Not suitable for production scale

**GCP Cloud Run:**
- ✅ Fast deployment
- ✅ Auto-scaling
- ✅ Pay-per-use pricing
- ❌ CPU only (slower diarization)

**GKE GPU:**
- ✅ GPU acceleration
- ✅ Full Kubernetes orchestration
- ✅ High availability
- ❌ More complex setup
- ❌ Higher cost

---

## 🐳 Docker Local Deployment

Deploy the Groq Speech Solution locally using Docker containers.

### Prerequisites

- Docker and Docker Compose installed
- NVIDIA Docker runtime (for GPU support)
- Groq API key and Hugging Face token

### Quick Start

#### 1. Set up environment variables

```bash
# From project root
cd groq-speech

# Option 1: Use automated setup script
./setup.sh

# Option 2: Manual setup
cp .env.api.template .env.api
cp .env.ui.template .env.ui

# Edit with your API keys
nano .env.api
```

**Required in `.env.api`:**
- `GROQ_API_KEY` - Your Groq API key (get from https://console.groq.com/keys)
- `HF_TOKEN` - Your Hugging Face token (optional, for diarization)

**Required in `.env.ui`:**
- `NEXT_PUBLIC_API_URL` - API URL (default: `http://groq-speech-api:8000`)

#### 2. Deploy with Docker Compose

```bash
# Standard deployment (CPU only)
docker-compose -f deployment/docker/docker-compose.yml up

# GPU-enabled deployment
docker-compose -f deployment/docker/docker-compose.gpu.yml up

# Development with hot reload
docker-compose -f deployment/docker/docker-compose.dev.yml up
```

#### 3. Access the services

- **API**: http://localhost:8000
- **UI**: https://localhost:3443
- **API Docs**: http://localhost:8000/docs

**Note**: The UI uses HTTPS for microphone access. Your browser will show a security warning for the self-signed certificate. Click "Advanced" and "Proceed to localhost" to continue.

#### 4. Check GPU support (if using GPU deployment)

```bash
docker-compose -f deployment/docker/docker-compose.gpu.yml exec api python test_gpu_support.py
```

### Docker Deployment Modes

#### Standard Deployment
Basic deployment with CPU processing:
```bash
docker-compose -f deployment/docker/docker-compose.yml up -d
```

**Features:**
- CPU-based processing
- Suitable for development
- Lower resource requirements

#### GPU-Enabled Deployment
Enhanced performance with GPU acceleration:
```bash
docker-compose -f deployment/docker/docker-compose.gpu.yml up -d
```

**Features:**
- CUDA acceleration for diarization
- Automatic GPU detection
- Falls back to CPU if GPU unavailable

#### Development Deployment
Hot reload for active development:
```bash
docker-compose -f deployment/docker/docker-compose.dev.yml up
```

**Features:**
- Code changes trigger automatic restarts
- Volume mounts for local development
- Enhanced logging and debugging

### Manual Docker Commands

```bash
# Build individual containers
docker build -f deployment/docker/Dockerfile.api -t groq-speech-api .
docker build -f deployment/docker/Dockerfile.ui -t groq-speech-ui .

# Run API
docker run -p 8000:8000 --env-file .env.api groq-speech-api

# Run UI (HTTPS)
docker run -p 3443:3443 --env-file .env.ui groq-speech-ui

# Run with GPU support
docker run --gpus all -p 8000:8000 --env-file .env.api groq-speech-api
```

### Docker Troubleshooting

#### Check container health
```bash
# Check API health
curl http://localhost:8000/health

# Check UI health (HTTPS)
curl -k https://localhost:3443
```

#### View container logs
```bash
# View all logs
docker-compose -f deployment/docker/docker-compose.yml logs

# View specific service logs
docker-compose -f deployment/docker/docker-compose.yml logs groq-speech-api
docker-compose -f deployment/docker/docker-compose.yml logs groq-speech-ui
```

#### Common Docker Issues

1. **API not starting**: Check `GROQ_API_KEY` is set in `.env.api`
2. **UI can't connect to API**: Check `NEXT_PUBLIC_API_URL` in `.env.ui`
3. **Build failures**: Ensure Docker has enough memory (4GB+)
4. **GPU not available**:
   ```bash
   # Check NVIDIA Docker runtime
   docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
   ```

---

## ☁️ GCP Cloud Run Deployment

Deploy to Google Cloud Platform using Cloud Run for serverless, auto-scaling deployment.

### Prerequisites

- Google Cloud Solution installed and authenticated
- GCP project with Cloud Run API enabled
- Working local Docker images
- Environment variables configured

### Quick Deployment

```bash
cd deployment/gcp
./deploy.sh
```

This will:
1. Build Docker images
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure environment variables
5. Display service URLs

### Manual Cloud Run Deployment

```bash
# Set environment variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export GROQ_API_KEY="your-groq-api-key"
export HF_TOKEN="your-hf-token"

# Build and push API image
docker build -f deployment/docker/Dockerfile.api -t gcr.io/$PROJECT_ID/groq-speech-api .
docker push gcr.io/$PROJECT_ID/groq-speech-api

# Build and push UI image
docker build -f deployment/docker/Dockerfile.ui -t gcr.io/$PROJECT_ID/groq-speech-ui .
docker push gcr.io/$PROJECT_ID/groq-speech-ui

# Deploy API
gcloud run deploy groq-speech-api \
  --image gcr.io/$PROJECT_ID/groq-speech-api \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=$GROQ_API_KEY,HF_TOKEN=$HF_TOKEN

# Deploy UI
gcloud run deploy groq-speech-ui \
  --image gcr.io/$PROJECT_ID/groq-speech-ui \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=$(gcloud run services describe groq-speech-api --region $REGION --format 'value(status.url)')
```

### Cloud Run Features

- **Auto-scaling**: Automatically scales based on demand (0 to N instances)
- **Pay-per-use**: Only pay for actual request processing time
- **Global deployment**: Deploy to multiple regions
- **Integrated monitoring**: Built-in logging and monitoring via Cloud Console
- **HTTPS by default**: Automatic SSL certificates

### Cloud Run Monitoring

```bash
# View deployment status
gcloud run services list --region=us-central1

# View logs
gcloud run services logs read groq-speech-api --region=us-central1
gcloud run services logs read groq-speech-ui --region=us-central1

# Get service URLs
gcloud run services describe groq-speech-api --region=us-central1 --format='value(status.url)'
gcloud run services describe groq-speech-ui --region=us-central1 --format='value(status.url)'
```

### Cloud Run Limitations

- **CPU only**: No GPU support (diarization will be slower)
- **Cold starts**: First request after idle may be slow
- **Request timeout**: Maximum 60 minutes per request
- **Memory limits**: Maximum 32GB RAM

---

## 🚀 GKE GPU Deployment

Deploy to Google Kubernetes Engine with GPU acceleration for production workloads.

### Prerequisites

- Google Cloud Solution installed and authenticated
- GCP project with GKE API enabled
- kubectl installed
- Docker images ready

### Quick Deployment

```bash
cd deployment/gcp
./deploy-simple-gke.sh
```

This will:
1. Create GKE cluster with GPU nodes
2. Install NVIDIA GPU drivers
3. Deploy API and UI services
4. Configure load balancer
5. Display access URLs

### GKE Features

- **GPU acceleration**: NVIDIA T4 GPUs for fast diarization
- **Kubernetes orchestration**: Full container orchestration
- **High availability**: Multi-zone deployment
- **Custom scaling**: Fine-grained control over resources
- **Advanced networking**: VPC, load balancing, ingress

### GKE Monitoring

```bash
# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=groq-speech-api
kubectl logs -l app=groq-speech-ui

# Check GPU usage
kubectl exec -it <api-pod-name> -- nvidia-smi

# Scale deployments
kubectl scale deployment groq-speech-api --replicas=3
kubectl scale deployment groq-speech-ui --replicas=2
```

### GKE Auto-scaling

```bash
# Configure horizontal pod autoscaling
kubectl autoscale deployment groq-speech-api \
  --min=1 --max=5 --cpu-percent=70

kubectl autoscale deployment groq-speech-ui \
  --min=1 --max=3 --cpu-percent=80
```

### GKE Cleanup

```bash
# Delete cluster
gcloud container clusters delete groq-speech-cluster --zone=us-central1-a

# Clean up secrets
kubectl delete secret groq-api-key
kubectl delete secret hf-token
```

---

## 🔧 Configuration

### Environment Variables

#### `.env.api` - Python/API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | **Required** Groq API key |
| `HF_TOKEN` | - | Hugging Face token for diarization |
| `GROQ_MODEL_ID` | whisper-large-v3 | Groq model to use |
| `GROQ_TEMPERATURE` | 0.0 | Model temperature |
| `AUDIO_SAMPLE_RATE` | 16000 | Audio sample rate |
| `MAX_AUDIO_FILE_SIZE` | 25000000 | Max file size (25MB) |
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8000 | API server port |

#### `.env.ui` - Next.js UI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | **Required** API URL for UI |
| `NEXT_PUBLIC_FRONTEND_URL` | http://localhost:3000 | Frontend URL |
| `NEXT_PUBLIC_VERBOSE` | false | Enable verbose logging |
| `NEXT_PUBLIC_DEBUG` | false | Enable debug mode |

### Resource Requirements

#### Development
- **API**: 1 CPU, 2GB RAM
- **UI**: 1 CPU, 1GB RAM

#### Production (CPU)
- **API**: 2 CPUs, 4GB RAM
- **UI**: 1 CPU, 1GB RAM

#### Production (GPU)
- **API**: 2 CPUs, 8GB RAM, 1 GPU (NVIDIA T4 or better)
- **UI**: 1 CPU, 1GB RAM

---

## 📊 Monitoring & Troubleshooting

### Health Checks

#### API Health Check
```bash
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

#### GPU Health Check
```bash
# Docker
docker-compose exec api python test_gpu_support.py

# GKE
kubectl exec -it <api-pod-name> -- python test_gpu_support.py

# Expected output
✅ CUDA available: True
✅ PyTorch CUDA: True
✅ GPU count: 1
✅ GPU name: NVIDIA Tesla T4
```

### Common Issues

#### 1. API Key Issues
```bash
# Docker
docker-compose exec api env | grep GROQ_API_KEY

# Verify API key format
docker-compose exec api python -c "import os; print('API Key set:', bool(os.getenv('GROQ_API_KEY')))"
```

#### 2. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :3443

# Change ports in docker-compose.yml or .env files if needed
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats

# For Docker, increase memory limits in docker-compose.yml:
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 4. GPU Not Available
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# If not available, install NVIDIA Container Toolkit:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Logging

#### Docker Logs
```bash
# View all logs
docker-compose logs -f

# View API logs only
docker-compose logs -f api | grep "ERROR"

# View frontend logs
docker-compose logs -f frontend
```

#### Cloud Run Logs
```bash
# Real-time logs
gcloud run services logs tail groq-speech-api --region=us-central1

# Filter by severity
gcloud run services logs read groq-speech-api \
  --region=us-central1 \
  --filter="severity>=ERROR"
```

#### GKE Logs
```bash
# Pod logs
kubectl logs -f deployment/groq-speech-api

# All API pods
kubectl logs -l app=groq-speech-api --all-containers=true

# Follow logs
kubectl logs -f -l app=groq-speech-api
```

### Performance Monitoring

- **API Response Times**: Available at `/health` endpoint
- **GPU Usage**: Monitor with `nvidia-smi` command
- **Memory Usage**: Monitor with `docker stats` or Kubernetes metrics
- **Request Metrics**: Available in Cloud Run/GKE dashboards

---

## 🔄 Updates and Maintenance

### Update Docker Images

```bash
# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Cloud Run Services

```bash
# Rebuild and deploy
docker build -f deployment/docker/Dockerfile.api -t gcr.io/$PROJECT_ID/groq-speech-api .
docker push gcr.io/$PROJECT_ID/groq-speech-api

gcloud run services update groq-speech-api \
  --image gcr.io/$PROJECT_ID/groq-speech-api \
  --region $REGION
```

### Update GKE Deployments

```bash
# Rebuild images
docker build -f deployment/docker/Dockerfile.api -t gcr.io/$PROJECT_ID/groq-speech-api .
docker push gcr.io/$PROJECT_ID/groq-speech-api

# Update deployment
kubectl set image deployment/groq-speech-api \
  api=gcr.io/$PROJECT_ID/groq-speech-api:latest

# Rollout status
kubectl rollout status deployment/groq-speech-api
```

---

## 📚 Additional Resources

- **Main README**: [../README.md](../README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Docker Files**: [../deployment/docker/](../deployment/docker/)
- **GCP Scripts**: [../deployment/gcp/](../deployment/gcp/)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Last Updated**: October 2025  
**Maintained By**: Groq Speech Solution Team

