#!/bin/bash

# Google Cloud Text-to-Speech Application Deployment Script
# Deploys the VIPER-based TTS application to Google Cloud Platform

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${VERTEX_AI_LOCATION:-"us-central1"}
SERVICE_NAME="tts-api"
TTS_BUCKET_NAME="${PROJECT_ID}-tts-audio"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi

    # Check if authenticated with gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi

    # Set project
    gcloud config set project $PROJECT_ID
    log_success "Prerequisites check completed"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs..."

    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        storage-component.googleapis.com \
        firestore.googleapis.com \
        texttospeech.googleapis.com \
        apigateway.googleapis.com \
        servicecontrol.googleapis.com \
        servicemanagement.googleapis.com

    log_success "APIs enabled successfully"
}

# Create Cloud Storage bucket for audio files
create_storage_bucket() {
    log_info "Creating Cloud Storage bucket: $TTS_BUCKET_NAME"

    if gsutil ls -b gs://$TTS_BUCKET_NAME &> /dev/null; then
        log_warning "Bucket $TTS_BUCKET_NAME already exists"
    else
        gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$TTS_BUCKET_NAME
        gsutil iam ch allUsers:objectViewer gs://$TTS_BUCKET_NAME
        log_success "Bucket created successfully"
    fi
}

# Initialize Firestore database
initialize_firestore() {
    log_info "Initializing Firestore database..."

    # Check if Firestore is already initialized
    if gcloud firestore databases describe --database="(default)" &> /dev/null; then
        log_warning "Firestore database already exists"
    else
        gcloud firestore databases create --database="(default)" --location=$REGION
        log_success "Firestore database initialized"
    fi
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."

    # Build the image
    docker build -t $IMAGE_NAME .

    # Configure Docker to use gcloud as credential helper
    gcloud auth configure-docker

    # Push the image
    docker push $IMAGE_NAME

    log_success "Docker image built and pushed successfully"
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    log_info "Deploying to Cloud Run..."

    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
        --set-env-vars TTS_BUCKET_NAME=$TTS_BUCKET_NAME \
        --set-env-vars VERTEX_AI_LOCATION=$REGION \
        --memory 2Gi \
        --cpu 2 \
        --concurrency 50 \
        --timeout 30 \
        --max-instances 10

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

    log_success "Service deployed successfully to: $SERVICE_URL"
}

# Deploy API Gateway
deploy_api_gateway() {
    log_info "Deploying API Gateway..."

    # Create API
    gcloud api-gateway apis create tts-api || log_warning "API already exists"

    # Create API config
    gcloud api-gateway api-configs create tts-config \
        --api=tts-api \
        --openapi-spec=docs/api/openapi.yaml \
        --backend-auth-service-account=${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com || log_warning "API config already exists"

    # Create gateway
    gcloud api-gateway gateways create tts-gateway \
        --api=tts-api \
        --api-config=tts-config \
        --location=$REGION || log_warning "Gateway already exists"

    # Get gateway URL
    GATEWAY_URL=$(gcloud api-gateway gateways describe tts-gateway --location=$REGION --format='value(defaultHostname)')

    log_success "API Gateway deployed successfully: https://$GATEWAY_URL"
}

# Set up IAM permissions
setup_iam() {
    log_info "Setting up IAM permissions..."

    # Create service account if it doesn't exist
    gcloud iam service-accounts create $SERVICE_NAME \
        --display-name="TTS API Service Account" || log_warning "Service account already exists"

    # Grant necessary permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin"

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/datastore.user"

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudtts.synthesizer"

    log_success "IAM permissions configured"
}

# Create Cloud Build configuration
setup_cloud_build() {
    log_info "Setting up Cloud Build for CI/CD..."

    cat > cloudbuild.yaml << 'EOF'
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/tts-api:$COMMIT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/tts-api:$COMMIT_SHA']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'tts-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/tts-api:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/tts-api:$COMMIT_SHA'
EOF

    log_success "Cloud Build configuration created"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f cloudbuild.yaml
}

# Main deployment function
main() {
    log_info "Starting deployment of Google Cloud Text-to-Speech application..."
    log_info "Project ID: $PROJECT_ID"
    log_info "Region: $REGION"
    log_info "Service Name: $SERVICE_NAME"

    check_prerequisites
    enable_apis
    create_storage_bucket
    initialize_firestore
    setup_iam
    build_and_push_image
    deploy_to_cloud_run
    deploy_api_gateway
    setup_cloud_build

    log_success "Deployment completed successfully!"
    log_info "Service URL: $SERVICE_URL"
    log_info "API Gateway URL: https://$GATEWAY_URL"
    log_info "Storage Bucket: gs://$TTS_BUCKET_NAME"

    cleanup
}

# Handle script interruption
trap cleanup EXIT

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Environment variables:"
    echo "  GOOGLE_CLOUD_PROJECT  - GCP Project ID (required)"
    echo "  VERTEX_AI_LOCATION    - GCP Region (default: us-central1)"
    echo ""
    echo "This script will:"
    echo "  1. Check prerequisites (gcloud, docker)"
    echo "  2. Enable required GCP APIs"
    echo "  3. Create Cloud Storage bucket"
    echo "  4. Initialize Firestore database"
    echo "  5. Set up IAM permissions"
    echo "  6. Build and push Docker image"
    echo "  7. Deploy to Cloud Run"
    echo "  8. Deploy API Gateway"
    echo "  9. Set up Cloud Build CI/CD"
    exit 0
fi

# Run main function
main "$@"