"""Database connection and session management."""

import asyncpg
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Database setup
database = Database(settings.DATABASE_URL)
metadata = MetaData()

# SQLAlchemy setup for migrations
engine = create_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def get_database() -> Database:
    """Get database connection."""
    return database


async def connect_to_db():
    """Connect to database."""
    await database.connect()


async def close_db_connection():
    """Close database connection."""
    await database.disconnect()


async def get_db_pool():
    """Get asyncpg connection pool for raw SQL operations."""
    return await asyncpg.create_pool(settings.DATABASE_URL)