from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(256), nullable=False)
    # Vai trò lớp học: none | teacher | student | admin
    role = Column(String(30), default="none", nullable=False)
    # Nguồn đăng nhập: local | google | facebook | github
    auth_provider = Column(String(30), default="local", nullable=False)
    avatar_url = Column(String(300), default="")
    school_name = Column(String(150), default="THCS & THPT Hòa Phú")
    class_name = Column(String(80), default="")
    xp_points = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
