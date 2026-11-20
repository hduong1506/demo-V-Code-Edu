from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.database.base import Base

class SharedSnippet(Base):
    __tablename__ = "shared_snippets"

    id = Column(Integer, primary_key=True, index=True)
    share_code = Column(String(32), unique=True, index=True, nullable=False)
    author = Column(String(80), default="Học sinh V-Code Edu")
    title = Column(String(150), default="Dự án Python")
    code = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
