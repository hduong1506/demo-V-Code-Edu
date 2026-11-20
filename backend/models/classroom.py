from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from backend.database.base import Base

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    grade_subject = Column(String(80), default="Tin học THPT • Python")
    description = Column(Text, default="")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClassroomMember(Base):
    __tablename__ = "classroom_members"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

class StudentLiveSession(Base):
    __tablename__ = "student_live_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_username = Column(String(80), unique=True, index=True, nullable=False)
    student_name = Column(String(120), nullable=False)
    class_code = Column(String(20), default="TIN10HP")
    current_problem = Column(String(180), default="")
    status = Column(String(30), default="coding")
    progress_percent = Column(Integer, default=0)
    current_code = Column(Text, default="")
    error_count = Column(Integer, default=0)
    teacher_hint = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)
