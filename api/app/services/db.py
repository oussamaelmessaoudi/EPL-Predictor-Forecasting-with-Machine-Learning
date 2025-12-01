import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://mlflow:mlflow_secure_pwd@postgres:5432/mlflow"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
