class Settings:
    # --- Database ---
    DB_USER: str = "suan"
    DB_PASSWORD: str = "suan"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3501
    DB_NAME: str = "suan"

    # --- JWT ---
    SECRET_KEY: str = "..."
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"

settings = Settings()
