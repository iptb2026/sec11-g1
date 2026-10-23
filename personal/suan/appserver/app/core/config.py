class Settings:
    # --- Database ---
    # MySQL inside the ipt-g1 Docker container (docker-compose.g1.yml maps 3501 -> 3306)
    DB_USER: str = "admin"
    DB_PASSWORD: str = "1234"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3501
    DB_NAME: str = "suan"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT ---
    SECRET_KEY: str = "f5f6cfcb44c92deaffbeae47dca73bb6b209f35ad226df224af0c235a33090c6"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
