from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.database.base import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, index=True, nullable=False)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=False)
    classroom_code = Column(String(20), index=True, default="TIN10HP")
    difficulty = Column(String(20), default="Cơ bản")
    points = Column(Integer, default=100)
    due_date = Column(String(40), default="Không giới hạn")
    starter_code = Column(Text, default="")
    test_cases_json = Column(Text, default="[]")
    created_by = Column(String(80), default="giaovien")
    created_at = Column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), index=True, nullable=False)
    student_name = Column(String(120), default="")
    classroom_code = Column(String(20), index=True, default="")
    assignment_code = Column(String(40), index=True, nullable=False)
    source_code = Column(Text, nullable=False)
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    score = Column(Integer, default=0)
    teacher_feedback = Column(Text, default="")
    submitted_at = Column(DateTime, default=datetime.utcnow)
