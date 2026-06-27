from pydantic_settings import BaseSettings


class ConfiguracoesApp(BaseSettings):
    # Banco de dados
    database_url: str = "sqlite:///database/auth.db"

    # JWT
    jwt_secret: str = "kapitour-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    jwt_expire_minutes: int = 60 * 24 * 7  # compatibilidade legado

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    cache_default_ttl: int = 300

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # CORS e segurança
    cors_origins: str = "*"
    internal_service_key: str = "kapitour-internal-dev-key"
    environment: str = "development"

    # Rate limiting
    rate_limit_default: str = "100/minute"
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"

    # URLs dos microserviços
    auth_service_url: str = "http://localhost:8001"
    content_service_url: str = "http://localhost:8002"
    engagement_service_url: str = "http://localhost:8003"
    commerce_service_url: str = "http://localhost:8004"
    kapipass_service_url: str = "http://localhost:8005"
    service_name: str = "kapitour"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@kapitour.com"
    app_base_url: str = "http://localhost:8000"

    # Banco — PostgreSQL em produção, SQLite em desenvolvimento
    db_pool_size: int = 5
    db_max_overflow: int = 10
    usar_alembic: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


configuracoes = ConfiguracoesApp()
