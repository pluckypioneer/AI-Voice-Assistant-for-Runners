# Configuration class for the application
from datetime import timedelta


class Config:
    # Debug mode for the application
    DEBUG = True
    # Port for the application
    PORT = 5000
    # Limit single upload to 10MB to avoid blocking
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    # JWT settings
    JWT_SECRET_KEY = "super-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    # Gzip compression threshold (bytes)
    COMPRESS_MIN_SIZE = 1024