#!/bin/bash

# Simple GKE Deployment using Local Docker Images
# This uses the exact same images that work locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}[INFO]${NC} Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults
API_REPLICAS=${API_REPLICAS:-1}
UI_REPLICAS=${UI_REPLICAS:-1}
CLUSTER_NAME=${CLUSTER_NAME:-groq-speech-gpu}

echo -e "${BLUE}[INFO]${NC} Deploying using local Docker images to GKE"
echo -e "${BLUE}[INFO]${NC} Project: $PROJECT_ID, Zone: $ZONE"
echo -e "${BLUE}[INFO]${NC} API replicas: $API_REPLICAS, UI replicas: $UI_REPLICAS"

# Tag and push local images to GCP
echo -e "${BLUE}[INFO]${NC} Tagging and pushing local Docker images..."

# Tag local images for GCP
docker tag docker-groq-speech-api gcr.io/$PROJECT_ID/groq-speech-api:local
docker tag docker-groq-speech-ui gcr.io/$PROJECT_ID/groq-speech-ui:local

# Push to GCP Container Registry
echo -e "${BLUE}[INFO]${NC} Pushing API image..."
docker push gcr.io/$PROJECT_ID/groq-speech-api:local

echo -e "${BLUE}[INFO]${NC} Pushing UI image..."
docker push gcr.io/$PROJECT_ID/groq-speech-ui:local

# Create GKE cluster if it doesn't exist
echo -e "${BLUE}[INFO]${NC} Checking if GKE cluster exists..."
if ! gcloud container clusters describe $CLUSTER_NAME --zone=$ZONE >/dev/null 2>&1; then
    echo -e "${BLUE}[INFO]${NC} Creating GKE cluster with GPU support..."
    gcloud container clusters create $CLUSTER_NAME \
        --zone=$ZONE \
        --machine-type=n1-standard-4 \
        --num-nodes=1 \
        --enable-autoscaling \
        --min-nodes=0 \
        --max-nodes=3 \
        --accelerator type=$GPU_TYPE,count=$GPU_COUNT \
        --enable-autoupgrade \
        --disk-size=50GB \
        --disk-type=pd-ssd \
        --image-type=COS_CONTAINERD
else
    echo -e "${YELLOW}[WARNING]${NC} Cluster already exists, using existing cluster"
fi

# Get cluster credentials
echo -e "${BLUE}[INFO]${NC} Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

# Create secrets
echo -e "${BLUE}[INFO]${NC} Creating secrets..."
kubectl create secret generic groq-secrets \
    --from-literal=groq-api-key="$GROQ_API_KEY" \
    --from-literal=hf-token="$HF_TOKEN" \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy API with GPU support
echo -e "${BLUE}[INFO]${NC} Deploying API with GPU support..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: groq-speech-api
  labels:
    app: groq-speech-api
spec:
  replicas: $API_REPLICAS
  selector:
    matchLabels:
      app: groq-speech-api
  template:
    metadata:
      labels:
        app: groq-speech-api
    spec:
      containers:
      - name: api
        image: gcr.io/$PROJECT_ID/groq-speech-api:local
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: groq-secrets
              key: groq-api-key
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: groq-secrets
              key: hf-token
        - name: GROQ_API_BASE
          value: "$GROQ_API_BASE"
        - name: GROQ_MODEL_ID
          value: "$GROQ_MODEL_ID"
        - name: DIARIZATION_ENABLED_BY_DEFAULT
          value: "true"
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "2"
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "4"
---
apiVersion: v1
kind: Service
metadata:
  name: groq-speech-api
spec:
  selector:
    app: groq-speech-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
EOF

# Wait for API to be ready
echo -e "${BLUE}[INFO]${NC} Waiting for API to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/groq-speech-api

# Get API internal URL
API_URL="http://groq-speech-api:8000"
echo -e "${GREEN}[SUCCESS]${NC} API deployed at: $API_URL"

# Deploy UI
echo -e "${BLUE}[INFO]${NC} Deploying UI..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: groq-speech-ui
  labels:
    app: groq-speech-ui
spec:
  replicas: $UI_REPLICAS
  selector:
    matchLabels:
      app: groq-speech-ui
  template:
    metadata:
      labels:
        app: groq-speech-ui
    spec:
      containers:
      - name: ui
        image: gcr.io/$PROJECT_ID/groq-speech-ui:local
        ports:
        - containerPort: 3443
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "$API_URL"
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "1Gi"
            cpu: "1"
          limits:
            memory: "2Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: groq-speech-ui
spec:
  selector:
    app: groq-speech-ui
  ports:
  - port: 80
    targetPort: 3443
  type: LoadBalancer
EOF

# Wait for UI to be ready
echo -e "${BLUE}[INFO]${NC} Waiting for UI to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/groq-speech-ui

# Get UI external URL
echo -e "${BLUE}[INFO]${NC} Getting UI external URL..."
UI_URL=$(kubectl get service groq-speech-ui -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$UI_URL" ]; then
    UI_URL=$(kubectl get service groq-speech-ui -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

echo -e "${GREEN}[SUCCESS]${NC} Deployment complete!"
echo -e "${BLUE}[INFO]${NC} API URL (internal): $API_URL"
echo -e "${BLUE}[INFO]${NC} UI URL (external): http://$UI_URL"
echo -e "${YELLOW}[NOTE]${NC} API uses GPU for fast diarization"
echo -e "${YELLOW}[NOTE]${NC} UI is accessible from the internet"
