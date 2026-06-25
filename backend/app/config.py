from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///database/kapitour.db"
    jwt_secret: str = "kapitour-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
