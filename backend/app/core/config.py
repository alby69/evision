from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/evadvisor"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    EV_CATALOG_API_KEY: str = ""
    EV_CATALOG_API_URL: str = "https://api.api-ninjas.com/v1/electricvehicle"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
