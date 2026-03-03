import os
from pathlib import Path
from dotenv import load_dotenv

current_file = Path(__file__).resolve()
ENV_PATH = None

for parent in current_file.parents:
    candidate = parent / ".env"
    if candidate.exists():
        ENV_PATH = candidate
        break

if ENV_PATH is None:
    raise RuntimeError(".env file not found in parent directories")

load_dotenv(dotenv_path=ENV_PATH)

def get_env(name: str, default=None, cast=None):
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable '{name}' is not set")
    if cast:
        try:
            return cast(value)
        except Exception:
            raise RuntimeError(f"Cannot cast '{name}' to {cast}")

    return value

DATABASE_URL = get_env("DATABASE_URL")

SECRET_KEY = get_env("SECRET_KEY")
ALGORITHM = get_env("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = get_env("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
REFRESH_TOKEN_EXPIRE_DAYS = get_env("REFRESH_TOKEN_EXPIRE_DAYS", cast=int)

CORS_ORIGINS = get_env("CORS_ORIGINS")
VEREFI_EMAIL_URL = get_env("VEREFI_EMAIL_URL")

REDIS_HOST = get_env("REDIS_HOST")
REDIS_PORT = get_env("REDIS_PORT")

CELERY_BROKER_URL = get_env("CELERY_BROKER_URL")

MAIL_USERNAME = get_env("MAIL_USERNAME")
MAIL_PASSWORD = get_env("MAIL_PASSWORD")
MAIL_FROM = get_env("MAIL_FROM")
MAIL_SERVER = get_env("MAIL_SERVER")
MAIL_PORT = get_env("MAIL_PORT", cast=int)
