from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///database/auth.db"
    jwt_secret: str = "kapitour-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "*"
    internal_service_key: str = "kapitour-internal-dev-key"
    auth_service_url: str = "http://localhost:8001"
    content_service_url: str = "http://localhost:8002"
    engagement_service_url: str = "http://localhost:8003"
    commerce_service_url: str = "http://localhost:8004"
    kapipass_service_url: str = "http://localhost:8005"
    service_name: str = "kapitour"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
