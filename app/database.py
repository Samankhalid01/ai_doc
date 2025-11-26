# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
try:
    from .config import DATABASE_URL
except ImportError:
    from config import DATABASE_URL
import datetime
import json

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    doc_type = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    extracted = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_document(filename: str, doc_type: str, raw_text: str, extracted: dict):
    db = SessionLocal()
    doc = Document(filename=filename, doc_type=doc_type, raw_text=raw_text, extracted=extracted)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()
    return doc.id
