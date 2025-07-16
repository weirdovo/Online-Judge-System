from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

DATABASE = "sqlite:///./data.db"
engine = create_engine(
    DATABASE, connect_args={"check_same_thread": False}, poolclass=NullPool
)
Localsession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
