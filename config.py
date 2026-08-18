import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
