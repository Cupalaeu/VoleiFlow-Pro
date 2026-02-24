# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Aponta para um arquivo local SQLite. 
# Quando formos para o Supabase, mudaremos apenas esta string.
SQLALCHEMY_DATABASE_URL = "sqlite:///./voleiflow.db"

# O argumento check_same_thread é uma exigência específica do SQLite para trabalhar com o FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()