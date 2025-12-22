from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import database_exists , create_database
DATABASE_URL = "mysql+aiomysql://root:admin@localhost:3306/ai_recruiter"

engine = create_async_engine(DATABASE_URL, echo=True)

if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
