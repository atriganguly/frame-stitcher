import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    API_KEY = os.getenv("FRAMESTITCHER_API_KEY", "default_dev_key")
    MAX_DOWNLOAD_CONCURRENCY = int(os.getenv("MAX_DOWNLOAD_CONCURRENCY", 10))

settings = Config()