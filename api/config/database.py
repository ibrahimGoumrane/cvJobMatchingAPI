import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import database_exists, create_database

# Load .env from the api directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Sync URL for sqlalchemy_utils (create_database/database_exists do not support async engines directly mostly)
SYNC_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)

if not database_exists(SYNC_DATABASE_URL):
    create_database(SYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
