import os
from typing import Optional
from dotenv import load_dotenv


class GCPConfig:
    def __init__(self, env_file: Optional[str] = None):
        # Load environment variables from .env file
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from default locations
            for env_path in ['.env', '../.env', '../../.env']:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    break

        # Core GCP Configuration
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
        self.location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        # Environment-specific project IDs
        self.project_id_staging = os.getenv('GOOGLE_CLOUD_PROJECT_STAGING')
        self.project_id_prod = os.getenv('GOOGLE_CLOUD_PROJECT_PROD')

        # Environment mode
        self.environment = os.getenv('ENVIRONMENT', 'development')

        # Text-to-Speech specific settings
        self.tts_bucket_name = self._get_bucket_name()
        self.tts_audio_prefix = os.getenv('TTS_AUDIO_PREFIX', 'tts-audio')
        self.tts_storage_class = os.getenv('TTS_STORAGE_CLASS', 'STANDARD')

        # Firestore settings
        self.firestore_database = os.getenv('FIRESTORE_DATABASE', '(default)')
        self.firestore_collection_prefix = os.getenv('FIRESTORE_COLLECTION_PREFIX', 'dev_')

        # API settings
        self.api_version = os.getenv('API_VERSION', 'v1')
        self.max_text_length = int(os.getenv('MAX_TEXT_LENGTH', '5000'))
        self.default_language = os.getenv('DEFAULT_LANGUAGE', 'en-US')
        self.default_voice_gender = os.getenv('DEFAULT_VOICE_GENDER', 'NEUTRAL')
        self.default_audio_encoding = os.getenv('DEFAULT_AUDIO_ENCODING', 'MP3')
        self.default_speaking_rate = float(os.getenv('DEFAULT_SPEAKING_RATE', '1.0'))
        self.default_pitch = float(os.getenv('DEFAULT_PITCH', '0.0'))

        # Performance settings
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'

        # Security settings
        self.allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        self.rate_limit_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
        self.auth_required = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'
        self.api_key_validation = os.getenv('API_KEY_VALIDATION', 'false').lower() == 'true'

        # Application settings
        self.port = int(os.getenv('PORT', '8080'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.structured_logging = os.getenv('STRUCTURED_LOGGING', 'false').lower() == 'true'

        # CLI settings
        self.cli_verbose = os.getenv('CLI_VERBOSE', 'false').lower() == 'true'
        self.cli_auto_play = os.getenv('CLI_AUTO_PLAY', 'false').lower() == 'true'
        self.cli_output_dir = os.getenv('CLI_OUTPUT_DIR', './tts-output')
        self.cli_workers = int(os.getenv('CLI_WORKERS', '3'))

        # Batch processing settings
        self.batch_chunk_size = int(os.getenv('BATCH_CHUNK_SIZE', '4500'))
        self.batch_preserve_sentences = os.getenv('BATCH_PRESERVE_SENTENCES', 'true').lower() == 'true'
        self.batch_continue_on_error = os.getenv('BATCH_CONTINUE_ON_ERROR', 'true').lower() == 'true'

        # Team credentials (for documentation/testing purposes)
        self.team_lead_email = os.getenv('TEAM_LEAD_EMAIL')
        self.team_lead_password = os.getenv('TEAM_LEAD_PASSWORD')

    def _get_bucket_name(self) -> str:
        """Get appropriate bucket name based on environment"""
        # First check if TTS_BUCKET_NAME is explicitly set
        bucket_name = os.getenv('TTS_BUCKET_NAME')
        if bucket_name:
            return bucket_name

        # Otherwise, determine based on environment and project
        if self.environment == 'staging' and self.project_id_staging:
            return os.getenv('TTS_BUCKET_NAME_STAGING', f'{self.project_id_staging}-tts-audio')
        elif self.environment == 'production' and self.project_id_prod:
            return os.getenv('TTS_BUCKET_NAME_PROD', f'{self.project_id_prod}-tts-audio')
        else:
            return f'{self.project_id}-tts-audio'

    def get_project_id_for_environment(self, env: Optional[str] = None) -> str:
        """Get project ID for specific environment"""
        env = env or self.environment

        if env == 'staging' and self.project_id_staging:
            return self.project_id_staging
        elif env == 'production' and self.project_id_prod:
            return self.project_id_prod
        else:
            return self.project_id

    def validate(self) -> bool:
        required_vars = [
            'GOOGLE_CLOUD_PROJECT',
            'TTS_BUCKET_NAME'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return True

    def get_storage_url(self, blob_name: str) -> str:
        return f"gs://{self.tts_bucket_name}/{blob_name}"

    def get_public_url(self, blob_name: str) -> str:
        return f"https://storage.googleapis.com/{self.tts_bucket_name}/{blob_name}"