from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # -----------------------------
    # Application Core Config
    # -----------------------------
    APP_NAME: str = "FastAPI Backend"
    DEBUG: bool = True

    # -----------------------------
    # Database Configuration
    # -----------------------------
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/mydatabase"

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
