from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from backend.database.base import Base

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    course_name = Column(String(120), default="Python Cơ Bản - GDPT 2018")
    order_index = Column(Integer, default=1)
    title = Column(String(180), nullable=False)
    summary = Column(Text, default="")
    content_html = Column(Text, default="")
    starter_code = Column(Text, default="")
    difficulty = Column(String(20), default="Cơ bản")

class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_slug = Column(String(60), nullable=False)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
