from pydantic_settings import BaseSettings
import os

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

class Settings(BaseSettings):
    # -----------------------------
    # Application Core Config
    # -----------------------------
    APP_NAME: str = "FastAPI Backend"
    DEBUG: bool = True

    # -----------------------------
    # Database Configuration
    # -----------------------------
    DATABASE_URL: str = "postgresql://mpita_admin:ZdPfoG4xvhvaWQDTqY5YpNqEtTnJxIy7@dpg-d3goj6ili9vc73faa8a0-a:5432/mpita_medical"

    # -----------------------------
    # Security & JWT Configuration
    # -----------------------------
    SECRET_KEY: str = "supersecretaccesskey"           # for access tokens
    REFRESH_SECRET_KEY: str = "supersecretrefreshkey"  # for refresh tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -----------------------------
    # CORS / Allowed Origins
    # -----------------------------
    ALLOWED_ORIGINS: list[str] = ["*"]  # Update for production


# Instantiate once so you can import it app-wide
settings = Settings()
