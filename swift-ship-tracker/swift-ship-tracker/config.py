import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'swift_ship_tracker.db'))
