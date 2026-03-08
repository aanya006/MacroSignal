import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/macrosignal')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
