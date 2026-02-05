"""Configuration centralisée de l'application."""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "heyi"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str = Field(..., alias="REDIS_URL")
    redis_ttl: int = 300
    
    # Deepgram
    deepgram_api_key: str = Field(default="", alias="DEEPGRAM_API_KEY")
    deepgram_model: str = "nova-2"
    deepgram_language: str = "fr-FR"
    
    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 1000
    
    # ElevenLabs
    elevenlabs_api_key: str = Field(default="", alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field(default="", alias="ELEVENLABS_VOICE_ID")
    elevenlabs_model: str = "eleven_turbo_v2_5"

    # Telnyx (remplace Twilio)
    telnyx_api_key: str = Field(..., alias="TELNYX_API_KEY")
    telnyx_phone_number: str = Field(..., alias="TELNYX_PHONE_NUMBER")
    telnyx_connection_id: str = Field(..., alias="TELNYX_CONNECTION_ID")
    telnyx_public_key: str = Field(default="", alias="TELNYX_PUBLIC_KEY")
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection: str = "products"
    
    # ERP
    erp_api_url: str = Field(default="http://localhost:8080", alias="ERP_API_URL")
    erp_api_key: str = Field(default="", alias="ERP_API_KEY")
    erp_timeout: int = 5
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Performance
    max_concurrent_calls: int = 10
    audio_buffer_size: int = 320
    vad_aggressiveness: int = 2

    # Brevo Email
    brevo_api_key: str = Field(default="", alias="BREVO_API_KEY")
    brevo_sender_email: str = Field(default="noreply@heyi.local", alias="BREVO_SENDER_EMAIL")
    brevo_sender_name: str = Field(default="HEYI", alias="BREVO_SENDER_NAME")

    # Mode démo
    demo_mode: bool = Field(default=False, alias="DEMO_MODE")
    demo_notification_emails: str = Field(default="", alias="DEMO_NOTIFICATION_EMAILS")
    demo_notification_whatsapp: str = Field(default="", alias="DEMO_NOTIFICATION_WHATSAPP")

    @property
    def demo_emails_list(self) -> List[str]:
        '''Parser les emails de notification démo.'''
        if not self.demo_notification_emails:
            return []
        return [email.strip() for email in self.demo_notification_emails.split(",")]


settings = Settings()
