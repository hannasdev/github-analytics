# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# GitHub API configuration
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "v3"

# Cache configuration
CACHE_MAX_SIZE = 100
CACHE_TTL = 300  # Time-to-live in seconds (5 minutes)

# Rate limiting
RATE_LIMIT_THRESHOLD = 10  # Number of remaining requests before waiting

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
