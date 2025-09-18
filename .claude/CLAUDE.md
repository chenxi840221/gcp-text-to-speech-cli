# Google Cloud AI Development Environment

This template is configured for building AI systems exclusively using Google VertexAI and Google Cloud Platform services. No external APIs (OpenAI, Claude, AWS, Azure) are permitted.

## AI Models & Services

### Large Language Models (LLMs)
- **Gemini 2.5 Pro**: Advanced reasoning model for complex problems
- **Gemini 2.5 Flash**: Best price-performance model
- **Gemini 2.5 Flash-Lite**: Cost-effective for high throughput
- **Gemini 2.0 Flash**: Latest multimodal with next-gen features
- **Gemini 2.0 Flash-Lite**: Optimized for cost efficiency and low latency

### Open Source Models
- **Gemma 3n**: Multimodal (text, image, video, audio), 140+ languages
- **Gemma 3**: Wide task solving, 128K context window
- **CodeGemma**: Specialized for coding tasks (20+ languages)
- **PaliGemma**: Vision-language model

### Medical & Specialized Models
- **MedGemma**: Medical text and image comprehension
- **MedSigLIP**: Medical image/text encoding
- **TxGemma**: Therapeutic data predictions
- **ShieldGemma**: Safety evaluation

### Embedding Models
- **text-embedding-004**: Text embeddings with customizable dimensions
- **multimodalembedding@001**: 1408-dimension vectors for image, text, video
- **gemini-embedding-001**: 3072-dimensional text vectors

### Computer Vision & Image Processing
- **Imagen 4**: Ultra, Fast Generate, Generate variants
- **Imagen 3**: Generation, Editing, Fast Generation
- **Virtual Try-On**: Product visualization
- **Product Recontextualization**: E-commerce imaging

### Video Generation
- **Veo 2 & 3**: Advanced video generation
- **Veo 3 Fast**: Optimized video generation

### Speech & Language
- **Text-to-Speech**: SSML support, multiple voices
- **Speech-to-Text (Chirp)**: 100+ languages support
- **Cloud Translation API**: Thousands of language pairs
- **Cloud Natural Language**: Text analysis with deep learning

## Google Cloud Platform Services

### Compute Services
- **Compute Engine**: Virtual machines with GPU/TPU support
- **Google Kubernetes Engine (GKE)**: Container orchestration
- **Cloud Run**: Serverless containers
- **Cloud Functions**: Event-driven serverless functions
- **App Engine**: Platform-as-a-Service
- **Cloud Batch**: Batch computing workloads

### Storage & Databases
- **Cloud Storage**: Object storage with global CDN
- **Cloud SQL**: Managed MySQL, PostgreSQL, SQL Server
- **Cloud Spanner**: Globally distributed relational database
- **AlloyDB**: High-performance PostgreSQL
- **Firestore**: NoSQL document database
- **Bigtable**: NoSQL for massive scale
- **BigQuery**: Data warehouse and analytics
- **Memorystore**: In-memory data store (Redis/Memcached)
- **Filestore**: High-performance file storage

### Networking
- **Virtual Private Cloud (VPC)**: Software-defined networking
- **Cloud Load Balancing**: Global load distribution
- **Cloud CDN**: Content delivery network
- **Cloud DNS**: Managed DNS service
- **Cloud Armor**: Web application firewall
- **Cloud Interconnect**: Hybrid connectivity
- **Private Service Connect**: Private service access

### Security & Identity
- **Identity Platform**: Authentication and user management
- **Secret Manager**: Secure credential storage
- **Security Command Center**: Security management
- **Confidential Computing**: Encrypted data processing
- **reCAPTCHA**: Bot protection
- **Access Transparency**: Access logging
- **Assured Workloads**: Compliance controls

### AI/ML Platform
- **Vertex AI**: Unified ML platform
- **Generative AI Studio**: Model experimentation
- **Document AI**: Document processing
- **Video Intelligence**: Video analysis
- **AutoML**: Custom model training

### DevOps & Monitoring
- **Cloud Build**: CI/CD pipelines
- **Cloud Deploy**: Deployment management
- **Cloud Logging**: Centralized logging
- **Cloud Monitoring**: Performance monitoring
- **Cloud Trace**: Distributed tracing
- **Cloud Profiler**: Performance profiling
- **Workflows**: Orchestration service
- **Error Reporting**: Error tracking

### API Documentation & Management
- **Cloud Endpoints**: API management with Swagger/OpenAPI support
- **API Gateway**: Fully managed API gateway with OpenAPI specifications
- **Cloud Console API Explorer**: Interactive API documentation
- **Swagger UI**: Auto-generated API documentation from OpenAPI specs

### Analytics & Data Processing
- **Dataflow**: Stream and batch processing
- **Dataproc**: Managed Spark and Hadoop
- **Pub/Sub**: Messaging and event streaming
- **Data Fusion**: Visual data integration
- **Composer**: Managed Apache Airflow
- **Dataplex**: Data lake management
- **Analytics Hub**: Data sharing

## Development Guidelines

### Architecture: VIPER Pattern

This template follows the VIPER (View, Interactor, Presenter, Entity, Router) architecture pattern for clean, testable, and maintainable AI applications.

#### VIPER Components

**View**: UI components and user interface logic
- Frontend frameworks (React, Vue, Angular) deployed on Cloud Run
- Mobile apps connecting to GCP APIs
- Web interfaces served via Cloud CDN

**Interactor**: Business logic and use cases
- AI model interactions and data processing
- Deployed as Cloud Functions or Cloud Run services
- Handles VertexAI API calls and data transformations

**Presenter**: Data formatting and presentation logic
- Formats AI model outputs for display
- Handles user input validation
- Manages UI state and error handling

**Entity**: Data models and structures
- Stored in Cloud SQL, Firestore, or BigQuery
- Cached in Memorystore for performance
- Defines data contracts between layers

**Router**: Navigation and flow control
- API Gateway and Load Balancer routing
- Cloud Endpoints for API management
- Authentication flow via Identity Platform

#### VIPER + Google Cloud Mapping

```
View Layer (Frontend)
├── Cloud Run (React/Vue/Angular apps)
├── Cloud CDN (Static assets)
└── Firebase Hosting (Web apps)

Interactor Layer (Business Logic)
├── Cloud Functions (Event-driven AI processing)
├── Cloud Run (Containerized AI services)
├── Vertex AI (Model inference)
└── Pub/Sub (Async processing)

Presenter Layer (Data Formatting)
├── Cloud Functions (Response formatting)
├── Cloud Run (API middleware)
└── API Gateway (Response transformation)

Entity Layer (Data)
├── Cloud SQL (Relational data)
├── Firestore (Document data)
├── BigQuery (Analytics data)
├── Cloud Storage (Files/artifacts)
└── Memorystore (Caching)

Router Layer (Navigation)
├── Cloud Load Balancer (Traffic routing)
├── Cloud Endpoints (API management)
├── Identity Platform (Authentication)
└── Cloud Armor (Security routing)
```

### API Integration
- Use Google Cloud Client Libraries for your preferred language
- Authenticate using Google Cloud service accounts
- Implement proper error handling and retry logic
- Use Cloud Logging for application logs

### Swagger/OpenAPI Documentation
- **API-First Design**: Define APIs using OpenAPI 3.0 specifications
- **Cloud Endpoints Integration**: Deploy APIs with built-in Swagger documentation
- **Automatic Documentation**: Generate interactive API docs from OpenAPI specs
- **Version Management**: Maintain API versions through OpenAPI specifications
- **Schema Validation**: Enforce request/response validation using OpenAPI schemas

### Model Selection
- **Text Generation**: Gemini 2.5 Flash for balanced performance
- **Code Generation**: CodeGemma for programming tasks
- **Multimodal Tasks**: Gemini 2.0 Flash for image/text/video
- **Embeddings**: text-embedding-004 for semantic search
- **Image Generation**: Imagen 4 for high-quality images
- **Video Generation**: Veo 3 for video content

### Architecture Patterns
- Use Cloud Run for containerized AI services
- Implement Cloud Functions for event-driven processing
- Store models and artifacts in Cloud Storage
- Use Pub/Sub for asynchronous AI workflows
- Deploy via Cloud Build CI/CD pipelines

### Cost Optimization
- Use Gemini Flash-Lite models for high-volume requests
- Implement request caching with Memorystore
- Use Cloud CDN for static AI-generated content
- Monitor costs with Cloud Billing APIs

### Security Best Practices
- Store API keys in Secret Manager
- Use IAM for fine-grained access control
- Enable VPC Service Controls for data protection
- Implement Cloud Armor for web application security

## VIPER Project Structure

```
project/
├── src/
│   ├── view/                           # View Layer
│   │   ├── components/
│   │   │   ├── chat_interface.py
│   │   │   ├── image_viewer.py
│   │   │   └── dashboard.py
│   │   ├── web/
│   │   │   ├── static/
│   │   │   └── templates/
│   │   └── mobile/
│   │       └── flutter_app/
│   ├── interactor/                     # Interactor Layer
│   │   ├── ai_services/
│   │   │   ├── gemini_interactor.py
│   │   │   ├── embedding_interactor.py
│   │   │   ├── imagen_interactor.py
│   │   │   └── veo_interactor.py
│   │   ├── business_logic/
│   │   │   ├── conversation_manager.py
│   │   │   ├── content_processor.py
│   │   │   └── workflow_orchestrator.py
│   │   └── data_processing/
│   │       ├── text_processor.py
│   │       ├── image_processor.py
│   │       └── video_processor.py
│   ├── presenter/                      # Presenter Layer
│   │   ├── formatters/
│   │   │   ├── response_formatter.py
│   │   │   ├── error_formatter.py
│   │   │   └── data_validator.py
│   │   ├── transformers/
│   │   │   ├── model_output_transformer.py
│   │   │   └── ui_state_manager.py
│   │   └── middleware/
│   │       ├── request_middleware.py
│   │       └── auth_middleware.py
│   ├── entity/                         # Entity Layer
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── ai_response.py
│   │   │   └── media_asset.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── conversation_repository.py
│   │   │   └── asset_repository.py
│   │   └── database/
│   │       ├── firestore_client.py
│   │       ├── sql_client.py
│   │       └── cache_client.py
│   ├── router/                         # Router Layer
│   │   ├── api_gateway/
│   │   │   ├── endpoints.py
│   │   │   ├── route_config.py
│   │   │   ├── middleware_chain.py
│   │   │   └── openapi_spec.py
│   │   ├── authentication/
│   │   │   ├── auth_router.py
│   │   │   ├── token_validator.py
│   │   │   └── permission_manager.py
│   │   ├── load_balancing/
│   │   │   ├── traffic_router.py
│   │   │   └── health_checker.py
│   │   └── swagger/
│   │       ├── swagger_config.py
│   │       ├── api_documentation.py
│   │       └── schema_validator.py
│   └── shared/                         # Shared Components
│       ├── config/
│       │   ├── gcp_config.py
│       │   └── environment.py
│       ├── utils/
│       │   ├── gcp_auth.py
│       │   ├── logging_utils.py
│       │   └── error_handler.py
│       └── constants/
│           ├── model_constants.py
│           └── api_constants.py
├── infrastructure/                     # Infrastructure as Code
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── vertex_ai/
│   │   │   ├── cloud_run/
│   │   │   ├── cloud_functions/
│   │   │   ├── databases/
│   │   │   └── networking/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── main.tf
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   └── ingress/
│   └── cloudbuild/
│       ├── cloudbuild.yaml
│       ├── deploy-dev.yaml
│       └── deploy-prod.yaml
├── tests/                              # Test Structure
│   ├── unit/
│   │   ├── view/
│   │   ├── interactor/
│   │   ├── presenter/
│   │   ├── entity/
│   │   └── router/
│   ├── integration/
│   │   ├── ai_services/
│   │   ├── database/
│   │   └── api/
│   └── e2e/
│       ├── user_flows/
│       └── performance/
├── docs/                               # Documentation
│   ├── architecture/
│   │   ├── viper_design.md
│   │   └── gcp_integration.md
│   ├── api/
│   │   ├── openapi.yaml
│   │   ├── swagger.yaml
│   │   ├── api_specs/
│   │   │   ├── gemini_api.yaml
│   │   │   ├── imagen_api.yaml
│   │   │   ├── veo_api.yaml
│   │   │   └── embedding_api.yaml
│   │   └── postman/
│   │       ├── ai_collection.json
│   │       └── environment.json
│   └── deployment/
│       └── setup_guide.md
├── config/
│   ├── development.yaml
│   ├── staging.yaml
│   ├── production.yaml
│   └── model_configs.yaml
├── scripts/
│   ├── deploy.sh
│   ├── setup_env.sh
│   └── run_tests.sh
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## Environment Variables

```bash
# Required GCP Configuration
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export VERTEX_AI_LOCATION="us-central1"

# AI Model Configuration
export GEMINI_MODEL="gemini-2.5-flash"
export EMBEDDING_MODEL="text-embedding-004"
export IMAGE_MODEL="imagen-4"

# Swagger/OpenAPI Configuration
export SWAGGER_ENABLED="true"
export API_DOCS_PATH="/docs"
export OPENAPI_VERSION="3.0.3"
export API_TITLE="Google Cloud AI API"
export API_VERSION="v1"
export API_DESCRIPTION="AI services powered by Google VertexAI and Cloud Platform"
```

## VIPER Deployment Commands

```bash
# Deploy each VIPER layer separately

# 1. Deploy Entity Layer (Databases)
gcloud sql instances create ai-database \
  --database-version=POSTGRES_15 \
  --region=us-central1

# 2. Deploy Interactor Layer (AI Services)
gcloud run deploy ai-interactor \
  --source ./src/interactor \
  --platform managed \
  --region us-central1 \
  --set-env-vars VERTEX_AI_LOCATION=us-central1

# 3. Deploy Presenter Layer (API Middleware)
gcloud functions deploy response-formatter \
  --source ./src/presenter \
  --runtime python312 \
  --trigger-http \
  --entry-point format_response

# 4. Deploy Router Layer (API Gateway with OpenAPI)
gcloud api-gateway api-configs create ai-config \
  --api=ai-api \
  --openapi-spec=docs/api/openapi.yaml \
  --backend-auth-service-account=ai-service@your-project.iam.gserviceaccount.com

gcloud api-gateway gateways create ai-gateway \
  --api=ai-api \
  --api-config=ai-config \
  --location=us-central1

# 5. Deploy View Layer (Frontend)
gcloud run deploy ai-frontend \
  --source ./src/view \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Set up CI/CD with Cloud Build for VIPER layers
gcloud builds submit --config infrastructure/cloudbuild/cloudbuild.yaml

# Deploy infrastructure with Terraform
cd infrastructure/terraform
terraform init
terraform plan -var-file="environments/production/terraform.tfvars"
terraform apply
```

## VIPER Testing Strategy

```bash
# Unit tests for each layer
python -m pytest tests/unit/view/
python -m pytest tests/unit/interactor/
python -m pytest tests/unit/presenter/
python -m pytest tests/unit/entity/
python -m pytest tests/unit/router/

# Integration tests
python -m pytest tests/integration/ai_services/
python -m pytest tests/integration/database/
python -m pytest tests/integration/api/

# End-to-end tests
python -m pytest tests/e2e/user_flows/
python -m pytest tests/e2e/performance/
```

## VIPER Development Workflow

1. **Entity First**: Define data models and repositories
2. **Interactor**: Implement business logic and AI integrations
3. **Presenter**: Build data formatters and transformers
4. **Router**: Configure API endpoints and authentication
5. **View**: Develop UI components and user interfaces

## Swagger/OpenAPI Implementation

### OpenAPI Specification Example

```yaml
# docs/api/openapi.yaml
openapi: 3.0.3
info:
  title: Google Cloud AI API
  description: AI services powered by Google VertexAI and Cloud Platform
  version: 1.0.0
  contact:
    name: AI Team
    email: ai-team@company.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://ai-gateway-{project}.uc.gateway.dev
    description: Production API Gateway
  - url: https://ai-staging-{project}.uc.gateway.dev
    description: Staging API Gateway

security:
  - BearerAuth: []

paths:
  /api/v1/chat:
    post:
      summary: Generate text using Gemini models
      tags: [Text Generation]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/InternalError'

  /api/v1/embeddings:
    post:
      summary: Generate text embeddings
      tags: [Embeddings]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EmbeddingRequest'
      responses:
        '200':
          description: Embedding vectors
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EmbeddingResponse'

  /api/v1/images/generate:
    post:
      summary: Generate images using Imagen
      tags: [Image Generation]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ImageGenerationRequest'
      responses:
        '200':
          description: Generated image URLs
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ImageGenerationResponse'

  /api/v1/videos/generate:
    post:
      summary: Generate videos using Veo
      tags: [Video Generation]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VideoGenerationRequest'
      responses:
        '200':
          description: Generated video URLs
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VideoGenerationResponse'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ChatRequest:
      type: object
      required: [message, model]
      properties:
        message:
          type: string
          description: Input text for the AI model
          example: "Explain quantum computing"
        model:
          type: string
          enum: [gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash]
          default: gemini-2.5-flash
        temperature:
          type: number
          minimum: 0
          maximum: 2
          default: 0.7
        max_tokens:
          type: integer
          minimum: 1
          maximum: 8192
          default: 1024

    ChatResponse:
      type: object
      properties:
        response:
          type: string
          description: AI-generated text response
        model:
          type: string
          description: Model used for generation
        usage:
          $ref: '#/components/schemas/Usage'
        timestamp:
          type: string
          format: date-time

    EmbeddingRequest:
      type: object
      required: [text]
      properties:
        text:
          type: string
          description: Text to embed
        model:
          type: string
          enum: [text-embedding-004, multimodalembedding@001]
          default: text-embedding-004

    EmbeddingResponse:
      type: object
      properties:
        embeddings:
          type: array
          items:
            type: number
        dimensions:
          type: integer
        model:
          type: string

    ImageGenerationRequest:
      type: object
      required: [prompt]
      properties:
        prompt:
          type: string
          description: Text description for image generation
        model:
          type: string
          enum: [imagen-4, imagen-3]
          default: imagen-4
        size:
          type: string
          enum: [256x256, 512x512, 1024x1024]
          default: 512x512

    ImageGenerationResponse:
      type: object
      properties:
        images:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                format: uri
              size:
                type: string

    VideoGenerationRequest:
      type: object
      required: [prompt]
      properties:
        prompt:
          type: string
          description: Text description for video generation
        model:
          type: string
          enum: [veo-3, veo-2]
          default: veo-3
        duration:
          type: integer
          minimum: 1
          maximum: 60
          default: 10

    VideoGenerationResponse:
      type: object
      properties:
        videos:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                format: uri
              duration:
                type: integer

    Usage:
      type: object
      properties:
        prompt_tokens:
          type: integer
        completion_tokens:
          type: integer
        total_tokens:
          type: integer

    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
        code:
          type: integer

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    InternalError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

### Swagger Integration Commands

```bash
# Generate API documentation
swagger-codegen generate -i docs/api/openapi.yaml -l html2 -o docs/api/generated

# Validate OpenAPI specification
swagger-codegen validate -i docs/api/openapi.yaml

# Generate client SDKs
swagger-codegen generate -i docs/api/openapi.yaml -l python -o clients/python
swagger-codegen generate -i docs/api/openapi.yaml -l javascript -o clients/javascript

# Deploy with Cloud Endpoints
gcloud endpoints services deploy docs/api/openapi.yaml

# Update API Gateway configuration
gcloud api-gateway api-configs create config-v2 \
  --api=ai-api \
  --openapi-spec=docs/api/openapi.yaml
```

This VIPER-based template with comprehensive Swagger/OpenAPI support ensures clean architecture, testability, maintainability, and excellent API documentation while leveraging Google Cloud's AI and infrastructure services exclusively.