import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def must_get_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


# Required individual parts
POSTGRES_USER = must_get_env("POSTGRES_USER")
POSTGRES_PASSWORD = must_get_env("POSTGRES_PASSWORD")
POSTGRES_DB = must_get_env("POSTGRES_DB")
POSTGRES_PORT = must_get_env("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # default to Docker service name

# Compose DATABASE_URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Secret for JWT
JWT_SECRET = must_get_env("JWT_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = must_get_env("ACCESS_TOKEN_EXPIRE_MINUTES")
