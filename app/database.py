# app/database.py

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from utils.log_utils.logger_instances import app_logger

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
    f"?sslmode={settings.sslmode}"
)
print(settings.database_name)
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        app_logger.log('Started')
        yield db
    finally:
        app_logger.log('DB Close')
        db.close()

def init_db():
    """Create all tables defined on Base.metadata."""

    Base.metadata.create_all(bind=engine)





##### TEST
def test_db_connection():
    """Try a simple SELECT 1 to verify connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("❌ DB connection test failed:", e)
        return False