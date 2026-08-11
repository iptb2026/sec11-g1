class Setting:
    # --- Database ---
    DB_USER: str = "salomon"
    DB_PASSWORD: str = "salomon"
    DB_HOST: str = "0.0.0.0"
    DB_PORT: int = 3306
    DB_NAME: str = "db"

    # --- JWT ---
    SECRET_KEY: str = "..."
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Bankign System API"
    APP_VERSION: str = "1.0.0"