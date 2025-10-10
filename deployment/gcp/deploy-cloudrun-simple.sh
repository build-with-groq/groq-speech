#!/bin/bash

# Simple Cloud Run Deployment using Local Docker Images
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

echo -e "${BLUE}[INFO]${NC} Deploying using local Docker images to Cloud Run"
echo -e "${BLUE}[INFO]${NC} Project: $PROJECT_ID, Region: $REGION"
echo -e "${BLUE}[INFO]${NC} API replicas: $API_REPLICAS, UI replicas: $UI_REPLICAS"

# Enable required APIs
echo -e "${BLUE}[INFO]${NC} Enabling required APIs..."
gcloud services enable run.googleapis.com secretmanager.googleapis.com

# Create secrets
echo -e "${BLUE}[INFO]${NC} Creating secrets..."
if gcloud secrets describe groq-secrets >/dev/null 2>&1; then
    echo -e "${YELLOW}[WARNING]${NC} Secret already exists, updating..."
    gcloud secrets versions add groq-secrets --data-file=- <<EOF
{
  "groq-api-key": "$GROQ_API_KEY",
  "hf-token": "$HF_TOKEN"
}
EOF
else
    gcloud secrets create groq-secrets --data-file=- <<EOF
{
  "groq-api-key": "$GROQ_API_KEY",
  "hf-token": "$HF_TOKEN"
}
EOF
fi

# Deploy API
echo -e "${BLUE}[INFO]${NC} Deploying API..."
gcloud run deploy groq-speech-api \
    --image gcr.io/$PROJECT_ID/groq-speech-api:local \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 8Gi \
    --cpu 4 \
    --min-instances $API_REPLICAS \
    --max-instances 10 \
    --set-secrets="GROQ_API_KEY=groq-secrets:groq-api-key,HF_TOKEN=groq-secrets:hf-token" \
    --set-env-vars="GROQ_API_BASE=$GROQ_API_BASE,GROQ_MODEL_ID=$GROQ_MODEL_ID,DIARIZATION_ENABLED_BY_DEFAULT=true"

# Get API URL
API_URL=$(gcloud run services describe groq-speech-api --platform managed --region $REGION --format 'value(status.url)')
echo -e "${GREEN}[SUCCESS]${NC} API deployed at: $API_URL"

# Deploy UI
echo -e "${BLUE}[INFO]${NC} Deploying UI..."
gcloud run deploy groq-speech-ui \
    --image gcr.io/$PROJECT_ID/groq-speech-ui:local \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 3443 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances $UI_REPLICAS \
    --max-instances 10 \
    --set-env-vars="NEXT_PUBLIC_API_URL=$API_URL,NODE_ENV=production"

# Get UI URL
UI_URL=$(gcloud run services describe groq-speech-ui --platform managed --region $REGION --format 'value(status.url)')
echo -e "${GREEN}[SUCCESS]${NC} UI deployed at: $UI_URL"

echo -e "${GREEN}[SUCCESS]${NC} Deployment complete!"
echo -e "${BLUE}[INFO]${NC} API URL: $API_URL"
echo -e "${BLUE}[INFO]${NC} UI URL: $UI_URL"
echo -e "${YELLOW}[NOTE]${NC} Using exact same Docker images that work locally"
echo -e "${YELLOW}[NOTE]${NC} API will use CPU (Cloud Run limitation) - diarization will be slower"
echo -e "${YELLOW}[NOTE]${NC} Both services are publicly accessible"
