"""
App settings. Secrets (the DB password and the JWT SECRET_KEY) are not in
this file: they come from environment variables, or from a `.env` file in
`Banking system/appserver/` (git-ignored). Copy `.env.example` to `.env`
and fill it in. A real environment variable wins over the same key in `.env`.
"""
import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def _load_env_file(path: Path) -> None:
    """Read KEY=value lines from .env into os.environ (without overriding real env vars)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _required(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"{key} is not set. Copy Banking system/appserver/.env.example to .env "
            f"and fill it in (or set the {key} environment variable)."
        )
    return value


_load_env_file(ENV_FILE)


class Settings:
    # --- Database ---
    DB_USER: str = os.environ.get("DB_USER", "admin")
    DB_PASSWORD: str = _required("DB_PASSWORD")
    DB_HOST: str = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME: str = os.environ.get("DB_NAME", "catarig")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT ---
    # Anyone who knows this key can create valid login tokens, so it must
    # stay out of git. Generate one with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = _required("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
