# -*- coding: utf-8 -*-
"""
V-CODE EDU — NÂNG CẤP TOÀN DIỆN AUTH CHUYÊN NGHIỆP (GOOGLE/FACEBOOK) + LỚP HỌC CHUẨN OLM.VN + DATABASE THẬT
Chạy trong Terminal VS Code tại thư mục V-Code Edu:
    python upgrade_auth_olm_classroom.py
"""
import os
import sys
import subprocess

# ==============================================================================
# PHẦN 1: CẬP NHẬT DATABASE MODELS, SCHEMAS & ROUTERS (BACKEND CHẠY ONLINE THẬT)
# ==============================================================================
BACKEND_FILES = {
    "backend/models/user.py": """from datetime import datetime
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
""",

    "backend/models/classroom.py": """from datetime import datetime
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
""",

    "backend/models/assessment.py": """from datetime import datetime
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
""",

    "backend/schemas/user_schema.py": """from pydantic import BaseModel

class RegisterSchema(BaseModel):
    full_name: str
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

class SocialAuthSchema(BaseModel):
    provider: str  # google | facebook | github
    email: str
    full_name: str
    avatar_url: str = ""

class SetRoleSchema(BaseModel):
    email: str
    role: str  # teacher | student
    school_name: str = "THCS & THPT Hòa Phú"
    class_name: str = ""
""",

    "backend/routers/auth.py": """import re
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.schemas.user_schema import RegisterSchema, LoginSchema, SocialAuthSchema, SetRoleSchema
from backend.services.auth_service import hash_password, verify_password, create_session_token

router = APIRouter(prefix="/api/auth", tags=["Xác thực & Tài khoản"])

def serialize_user(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "auth_provider": u.auth_provider,
        "avatar_url": u.avatar_url,
        "school_name": u.school_name,
        "class_name": u.class_name,
        "xp": u.xp_points
    }

def build_unique_username(email: str, db: Session) -> str:
    base = re.sub(r"[^a-zA-Z0-9_]", "", email.split("@")[0].lower()) or "user"
    candidate = base[:30]
    while db.query(User).filter(User.username == candidate).first():
        candidate = f"{base[:24]}_{secrets.token_hex(2)}"
    return candidate

@router.post("/register")
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký. Vui lòng đăng nhập.")

    user = User(
        username=build_unique_username(email, db),
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role="none",
        auth_provider="local",
        xp_points=100
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "ok", "token": create_session_token(user.username, user.role), "user": serialize_user(user)}

@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    ident = payload.email.strip().lower()
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu.")
    return {"status": "ok", "token": create_session_token(user.username, user.role), "user": serialize_user(user)}

@router.post("/social")
def social_auth(payload: SocialAuthSchema, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    provider = payload.provider.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            username=build_unique_username(email, db),
            email=email,
            full_name=payload.full_name.strip() or email.split("@")[0],
            password_hash=hash_password(secrets.token_hex(16)),
            role="none",
            auth_provider=provider,
            avatar_url=payload.avatar_url,
            xp_points=150
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"status": "ok", "token": create_session_token(user.username, user.role), "user": serialize_user(user)}

@router.post("/set-role")
def set_classroom_role(payload: SetRoleSchema, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter((User.email == email) | (User.username == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    if payload.role not in ("teacher", "student"):
        raise HTTPException(status_code=400, detail="Vai trò chỉ nhận 'teacher' hoặc 'student'.")
    user.role = payload.role
    if payload.school_name.strip():
        user.school_name = payload.school_name.strip()
    if payload.class_name.strip():
        user.class_name = payload.class_name.strip()
    db.commit()
    db.refresh(user)
    return {"status": "ok", "user": serialize_user(user)}
""",

    "backend/routers/classrooms.py": """import json
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.classroom import Classroom, ClassroomMember
from backend.models.assessment import Assignment, Submission

router = APIRouter(prefix="/api/classes", tags=["Quản lý Lớp học (Chuẩn OLM)"])

def format_classroom(c: Classroom, db: Session) -> dict:
    teacher = db.query(User).filter(User.id == c.teacher_id).first()
    student_count = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == c.id).count()
    assignment_count = db.query(Assignment).filter(Assignment.classroom_code == c.code).count()
    return {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "grade_subject": c.grade_subject,
        "description": c.description,
        "teacher_name": teacher.full_name if teacher else "Giáo viên V-Code",
        "teacher_email": teacher.email if teacher else "",
        "students_count": student_count,
        "assignments_count": assignment_count
    }

@router.get("/")
def list_all_classes(db: Session = Depends(get_db)):
    rows = db.query(Classroom).order_by(Classroom.created_at.desc()).all()
    return {"classes": [format_classroom(c, db) for c in rows]}

@router.get("/teacher/{identifier}")
def list_teacher_classes(identifier: str, db: Session = Depends(get_db)):
    ident = identifier.strip().lower()
    teacher = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not teacher:
        return {"classes": []}
    rows = db.query(Classroom).filter(Classroom.teacher_id == teacher.id).order_by(Classroom.created_at.desc()).all()
    return {"classes": [format_classroom(c, db) for c in rows]}

@router.get("/student/{identifier}")
def list_student_classes(identifier: str, db: Session = Depends(get_db)):
    ident = identifier.strip().lower()
    student = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not student:
        return {"classes": []}
    memberships = db.query(ClassroomMember).filter(ClassroomMember.student_id == student.id).all()
    class_ids = [m.classroom_id for m in memberships]
    if not class_ids:
        return {"classes": []}
    rows = db.query(Classroom).filter(Classroom.id.in_(class_ids)).all()
    return {"classes": [format_classroom(c, db) for c in rows]}

@router.post("/create")
def create_classroom(payload: dict, db: Session = Depends(get_db)):
    ident = (payload.get("teacher_email") or payload.get("teacher_username") or "giaovien").strip().lower()
    teacher = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Vui lòng đăng nhập tài khoản giáo viên trước khi tạo lớp.")
    if teacher.role != "teacher":
        teacher.role = "teacher"
        db.commit()

    custom_code = (payload.get("code") or "").strip().upper()
    code = custom_code if custom_code else f"VC{secrets.token_hex(2).upper()}"
    while db.query(Classroom).filter(Classroom.code == code).first():
        code = f"VC{secrets.token_hex(2).upper()}"

    cls = Classroom(
        code=code,
        name=(payload.get("name") or "Lớp Tin học mới").strip(),
        grade_subject=(payload.get("grade_subject") or "Tin học THPT • Python").strip(),
        description=(payload.get("description") or "").strip(),
        teacher_id=teacher.id
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return {"status": "ok", "classroom": format_classroom(cls, db)}

@router.post("/join")
def join_classroom(payload: dict, db: Session = Depends(get_db)):
    code = (payload.get("code") or "").strip().upper()
    ident = (payload.get("student_email") or payload.get("username") or "").strip().lower()
    cls = db.query(Classroom).filter(Classroom.code == code).first()
    if not cls:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lớp học với ID mã lớp '{code}'. Hãy kiểm tra lại mã thầy/cô gửi.")
    student = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Vui lòng đăng nhập tài khoản trước khi tham gia lớp.")

    exists = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == cls.id, ClassroomMember.student_id == student.id).first()
    if not exists:
        db.add(ClassroomMember(classroom_id=cls.id, student_id=student.id))
        db.commit()
    return {"status": "joined", "classroom": format_classroom(cls, db)}

@router.get("/{code}/detail")
def get_classroom_detail(code: str, db: Session = Depends(get_db)):
    c_code = code.strip().upper()
    cls = db.query(Classroom).filter(Classroom.code == c_code).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học.")

    members = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == cls.id).all()
    student_ids = [m.student_id for m in members]
    students = db.query(User).filter(User.id.in_(student_ids)).all() if student_ids else []

    assignments = db.query(Assignment).filter(Assignment.classroom_code == c_code).order_by(Assignment.created_at.desc()).all()
    submissions = db.query(Submission).filter(Submission.classroom_code == c_code).order_by(Submission.submitted_at.desc()).limit(50).all()

    return {
        "classroom": format_classroom(cls, db),
        "students": [
            {"username": s.username, "full_name": s.full_name, "email": s.email, "xp": s.xp_points}
            for s in students
        ],
        "assignments": [
            {
                "code": a.code,
                "title": a.title,
                "description": a.description,
                "difficulty": a.difficulty,
                "points": a.points,
                "due_date": a.due_date,
                "starter_code": a.starter_code,
                "test_cases": json.loads(a.test_cases_json or "[]")
            }
            for a in assignments
        ],
        "submissions": [
            {
                "username": sub.username,
                "student_name": sub.student_name or sub.username,
                "assignment_code": sub.assignment_code,
                "score": sub.score,
                "passed_tests": sub.passed_tests,
                "total_tests": sub.total_tests,
                "submitted_at": sub.submitted_at.strftime("%H:%M %d/%m/%Y")
            }
            for sub in submissions
        ]
    }
""",

    "backend/routers/assessment.py": """import json
import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.assessment import Assignment, Submission

router = APIRouter(prefix="/api/assessment", tags=["Giao bài tập, Nộp bài & Xếp hạng"])

@router.post("/create")
def create_assignment(payload: dict, db: Session = Depends(get_db)):
    code = f"BT-{secrets.token_hex(3).upper()}"
    test_cases = payload.get("test_cases") or [{"input": "6", "expected": "12"}]
    item = Assignment(
        code=code,
        title=(payload.get("title") or "Bài tập thực hành Python").strip(),
        description=(payload.get("description") or "").strip(),
        classroom_code=(payload.get("classroom_code") or "TIN10HP").strip().upper(),
        difficulty=payload.get("difficulty") or "Cơ bản",
        points=int(payload.get("points") or 100),
        due_date=payload.get("due_date") or "Trong tuần",
        starter_code=payload.get("starter_code") or "n = int(input())\\nprint(n)",
        test_cases_json=json.dumps(test_cases, ensure_ascii=False),
        created_by=payload.get("created_by") or "giaovien"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "status": "ok",
        "assignment": {
            "code": item.code,
            "title": item.title,
            "description": item.description,
            "classroom_code": item.classroom_code,
            "difficulty": item.difficulty,
            "points": item.points,
            "due_date": item.due_date,
            "starter_code": item.starter_code,
            "test_cases": test_cases
        }
    }

@router.get("/assignments")
def list_assignments(class_code: str = "", db: Session = Depends(get_db)):
    q = db.query(Assignment)
    if class_code:
        q = q.filter(Assignment.classroom_code == class_code.strip().upper())
    rows = q.order_by(Assignment.created_at.desc()).all()
    return {
        "assignments": [
            {
                "code": a.code,
                "title": a.title,
                "description": a.description,
                "classroom_code": a.classroom_code,
                "difficulty": a.difficulty,
                "points": a.points,
                "due_date": a.due_date,
                "starter_code": a.starter_code,
                "test_cases": json.loads(a.test_cases_json or "[]")
            }
            for a in rows
        ]
    }

@router.post("/submit")
def submit_solution(payload: dict, db: Session = Depends(get_db)):
    ident = (payload.get("email") or payload.get("username") or "hocsinh").strip().lower()
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    sub = Submission(
        username=user.username if user else ident,
        student_name=payload.get("student_name") or (user.full_name if user else ident),
        classroom_code=(payload.get("classroom_code") or "TIN10HP").strip().upper(),
        assignment_code=payload.get("assignment_code", "py-01"),
        source_code=payload.get("source_code", ""),
        passed_tests=int(payload.get("passed_tests", 0)),
        total_tests=int(payload.get("total_tests", 0)),
        score=int(payload.get("score", 0))
    )
    db.add(sub)
    if user and sub.score == 100:
        user.xp_points += 50
    db.commit()
    return {"status": "saved", "score": sub.score, "new_xp": user.xp_points if user else 0}

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role != "teacher").order_by(User.xp_points.desc()).limit(20).all()
    return {
        "leaderboard": [
            {"rank": idx + 1, "name": u.full_name, "classCode": u.class_name or "V-Code", "xp": u.xp_points}
            for idx, u in enumerate(users)
        ]
    }
""",

    "backend/database/init_db.py": """import json
from backend.database.base import Base
from backend.database.connection import engine, SessionLocal
from backend.models.user import User
from backend.models.classroom import Classroom, ClassroomMember, StudentLiveSession
from backend.models.learning import Lesson, LessonProgress
from backend.models.assessment import Assignment, Submission
from backend.models.workspace import SharedSnippet
from backend.services.auth_service import hash_password

def init_database(reset_schema: bool = False):
    if reset_schema:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        teacher = db.query(User).filter(User.email == "giaovien@vcode.edu.vn").first()
        if not teacher:
            teacher = User(
                username="giaovien",
                email="giaovien@vcode.edu.vn",
                full_name="Thầy Nguyễn Phi Hùng",
                password_hash=hash_password("123456"),
                role="teacher",
                auth_provider="local",
                school_name="THCS & THPT Hòa Phú",
                class_name="Tổ Tin học",
                xp_points=2500
            )
            student1 = User(
                username="hocsinh",
                email="hocsinh@vcode.edu.vn",
                full_name="Nguyễn Minh Quân",
                password_hash=hash_password("123456"),
                role="student",
                auth_provider="local",
                school_name="THCS & THPT Hòa Phú",
                class_name="10A1",
                xp_points=1450
            )
            student2 = User(
                username="thuha_10a1",
                email="thuha@vcode.edu.vn",
                full_name="Lê Thu Hà",
                password_hash=hash_password("123456"),
                role="student",
                auth_provider="google",
                school_name="THCS & THPT Hòa Phú",
                class_name="10A1",
                xp_points=1320
            )
            db.add_all([teacher, student1, student2])
            db.commit()
            db.refresh(teacher)
            db.refresh(student1)
            db.refresh(student2)

            cls1 = Classroom(
                code="TIN10HP",
                name="Tin học 10A1 — THCS & THPT Hòa Phú",
                grade_subject="Tin học 10 • Python GDPT 2018",
                description="Lớp học thực hành Python cơ bản và cầu nối Scratch Live.",
                teacher_id=teacher.id
            )
            cls2 = Classroom(
                code="HSGPY26",
                name="Đội tuyển HSG Tin học Python",
                grade_subject="Bồi dưỡng HSG • Thuật toán",
                description="Luyện đề thi Học sinh giỏi Tin học cấp Tỉnh.",
                teacher_id=teacher.id
            )
            db.add_all([cls1, cls2])
            db.commit()
            db.refresh(cls1)

            db.add_all([
                ClassroomMember(classroom_id=cls1.id, student_id=student1.id),
                ClassroomMember(classroom_id=cls1.id, student_id=student2.id)
            ])
            db.commit()

        if db.query(Assignment).count() == 0:
            db.add_all([
                Assignment(
                    code="BT-CHAN01",
                    title="Bài tập 1: Tổng các số chẵn từ 1 đến N",
                    description="Nhập số nguyên dương N. Tính và in ra tổng các số chẵn từ 1 đến N.",
                    classroom_code="TIN10HP",
                    difficulty="Cơ bản",
                    points=100,
                    due_date="25/11/2026",
                    starter_code="n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong += i\\nprint(tong)",
                    test_cases_json=json.dumps([{"input": "6", "expected": "12"}, {"input": "10", "expected": "30"}]),
                    created_by="giaovien"
                ),
                Assignment(
                    code="BT-HLUC02",
                    title="Bài tập 2: Xếp loại học lực theo điểm trung bình",
                    description="Nhập điểm nguyên (0-10). Nếu >= 8 in 'Gioi', >= 6 in 'Kha', ngược lại in 'Can co gang'.",
                    classroom_code="TIN10HP",
                    difficulty="Cơ bản",
                    points=100,
                    due_date="28/11/2026",
                    starter_code="diem = int(input())\\nif diem >= 8:\\n    print('Gioi')\\nelif diem >= 6:\\n    print('Kha')\\nelse:\\n    print('Can co gang')",
                    test_cases_json=json.dumps([{"input": "9", "expected": "Gioi"}, {"input": "7", "expected": "Kha"}, {"input": "4", "expected": "Can co gang"}]),
                    created_by="giaovien"
                )
            ])
            db.commit()

        if db.query(StudentLiveSession).count() == 0:
            db.add_all([
                StudentLiveSession(
                    student_username="hocsinh", student_name="Nguyễn Minh Quân", class_code="TIN10HP",
                    current_problem="Bài tập 1: Tổng các số chẵn từ 1 đến N", status="coding", progress_percent=80,
                    current_code="n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong += i\\nprint(tong)", error_count=0
                ),
                StudentLiveSession(
                    student_username="thuha_10a1", student_name="Lê Thu Hà", class_code="TIN10HP",
                    current_problem="Bài tập 2: Xếp loại học lực", status="error", progress_percent=45,
                    current_code="diem = int(input())\\nif diem >= 8\\n    print('Gioi')", error_count=1
                )
            ])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_database(reset_schema=True)
    print("✔ Đã nâng cấp schema & khởi tạo lại CSDL vcode_edu.db thành công!")
"""
}

# ==============================================================================
# PHẦN 2: CSS CHO GIAO DIỆN AUTH CHUYÊN NGHIỆP (GOOGLE/FB) & LỚP HỌC CHUẨN OLM
# ==============================================================================
EXTRA_UI_CSS = """
/* ==================== PROFESSIONAL AUTH MODAL & SOCIAL OAUTH ==================== */
.auth-modal-pro {
  max-width: 440px !important;
  padding: 32px 28px !important;
  background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-base) 100%) !important;
}

.auth-header-brand {
  text-align: center;
  margin-bottom: 22px;
}

.auth-header-brand .brand-mark {
  margin: 0 auto 12px;
  width: 44px;
  height: 44px;
  font-size: 18px;
  border-radius: 12px;
}

.auth-header-brand h2 {
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}

.auth-header-brand p {
  font-size: 13px;
  color: var(--text-secondary);
}

.social-auth-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 18px;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 10px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.social-btn:hover {
  transform: translateY(-2px);
  border-color: var(--accent-emerald);
  background: var(--bg-surface);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 12px;
  margin: 16px 0;
}

.auth-divider::before, .auth-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border-subtle);
}

.auth-field {
  margin-bottom: 13px;
}

.auth-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.password-wrap {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
}

.auth-switch-footer {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}

.auth-switch-footer button {
  background: transparent;
  border: none;
  color: var(--accent-emerald);
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  font-size: 13px;
  margin-left: 4px;
}

.auth-switch-footer button:hover {
  text-decoration: underline;
}

/* ==================== OLM-STYLE CLASSROOM PORTAL ==================== */
.olm-portal-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(59, 130, 246, 0.10));
  border: 1px solid var(--border-highlight);
  border-radius: var(--radius-lg);
  padding: 22px 26px;
  margin-bottom: 24px;
}

.olm-role-switcher {
  display: flex;
  gap: 8px;
  background: var(--bg-base);
  padding: 5px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
}

.olm-role-tab {
  padding: 9px 18px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.olm-role-tab.active {
  background: var(--accent-emerald);
  color: #031F16;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}

.olm-join-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-highlight);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.olm-class-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 20px;
  transition: all 0.22s ease;
  cursor: pointer;
}

.olm-class-card:hover, .olm-class-card.selected {
  border-color: var(--accent-emerald);
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}

.olm-code-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 7px;
  background: rgba(16, 185, 129, 0.14);
  border: 1px dashed var(--accent-emerald);
  color: var(--accent-emerald);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 13px;
  letter-spacing: 0.06em;
}

.olm-subnav {
  display: flex;
  gap: 6px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 18px;
  padding-bottom: 10px;
  flex-wrap: wrap;
}

.olm-assignment-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 15px 18px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.olm-assignment-row:hover {
  border-color: var(--border-highlight);
}
"""

# ==============================================================================
# PHẦN 3: HTML MỚI CHO VIEW LỚP HỌC (CHUẨN OLM) & MODAL ĐĂNG NHẬP/ĐĂNG KÝ CHUYÊN NGHIỆP
# ==============================================================================
NEW_CLASSROOM_SECTION = """  <!-- ==================== VIEW 4: LỚP HỌC CHUẨN OLM.VN (GIÁO VIÊN & HỌC SINH ONLINE THẬT) ==================== -->
  <section id="view-classroom" class="view-section">
    <div class="page-container">
      <div class="olm-portal-banner">
        <div>
          <span class="bento-tag" style="margin-bottom:4px">Hệ thống Lớp học Trực tuyến • Kết nối Database &amp; Real-time</span>
          <h2 style="font-size:24px;margin-bottom:4px">Không gian Lớp học V-Code Edu (Mô hình OLM)</h2>
          <p style="font-size:13px;color:var(--text-secondary)">Chọn cổng Giáo viên để tạo lớp, giao bài, giám sát Real-time hoặc cổng Học sinh để nhập ID mã lớp làm bài tập.</p>
        </div>
        <div class="olm-role-switcher">
          <button id="olm-tab-teacher" class="olm-role-tab active" onclick="switchClassroomPortal('teacher')">👨‍🏫 Cổng Giáo viên</button>
          <button id="olm-tab-student" class="olm-role-tab" onclick="switchClassroomPortal('student')">👨‍🎓 Cổng Học sinh</button>
        </div>
      </div>

      <!-- ==================== CỔNG GIÁO VIÊN ==================== -->
      <div id="portal-teacher">
        <div id="teacher-register-card" class="bento-card" style="display:none;margin-bottom:24px;border-color:var(--accent-emerald)">
          <span class="bento-tag">Kích hoạt quyền Giáo viên</span>
          <h3 style="margin-bottom:8px">Đăng ký Tài khoản Giáo viên V-Code Edu</h3>
          <p style="margin-bottom:14px">Kích hoạt ngay để tạo lớp học không giới hạn, chia sẻ mã lớp ID, giao bài tập Python có chấm tự động và theo dõi học sinh làm bài trực tuyến.</p>
          <div class="grid-2col" style="gap:12px;margin-bottom:14px">
            <div><label style="font-size:12px;color:var(--text-secondary)">Trường học / Đơn vị công tác:</label><input id="reg-teacher-school" class="input-field" value="THCS & THPT Hòa Phú" style="margin-top:4px" /></div>
            <div><label style="font-size:12px;color:var(--text-secondary)">Tổ chuyên môn:</label><input id="reg-teacher-dept" class="input-field" value="Tổ Tin học" style="margin-top:4px" /></div>
          </div>
          <button class="btn btn-primary" onclick="activateClassroomRole('teacher')">✓ Xác nhận Đăng ký Giáo viên</button>
        </div>

        <div id="teacher-dashboard">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px">
            <h3 style="font-size:17px">📚 Danh sách Lớp học do bạn quản lý</h3>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-class-modal').classList.add('open')">+ Tạo lớp học mới</button>
              <button class="btn btn-blue btn-sm" onclick="openCreateAssignmentModal()">📝 Giao bài tập cho lớp</button>
              <button class="btn btn-sm" onclick="exportGradesCSV()">📊 Xuất Bảng điểm (.CSV)</button>
            </div>
          </div>

          <div id="teacher-classes-grid" class="grid-3col" style="margin-bottom:26px"></div>

          <div id="teacher-active-class-panel" class="bento-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px">
              <div>
                <span class="bento-tag" style="margin-bottom:2px">Lớp học đang quản lý</span>
                <h3 id="teacher-selected-class-title" style="font-size:19px">Đang tải lớp học...</h3>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <span id="teacher-selected-class-code" class="olm-code-chip">TIN10HP</span>
                <button class="btn btn-sm" onclick="copyActiveClassCode()">📋 Copy Mã lớp</button>
                <button class="btn btn-sm btn-primary" onclick="shareActiveClassQR()">📱 Chia sẻ QR vào lớp</button>
              </div>
            </div>

            <div class="olm-subnav">
              <button class="subtab-btn active" data-tpanel="realtime" onclick="switchTeacherSubpanel('realtime')">📡 Giám sát Học sinh Online (Real-time)</button>
              <button class="subtab-btn" data-tpanel="assignments" onclick="switchTeacherSubpanel('assignments')">📝 Bài tập đã giao &amp; Bài nộp</button>
              <button class="subtab-btn" data-tpanel="students" onclick="switchTeacherSubpanel('students')">👥 Danh sách Học sinh</button>
            </div>

            <div id="tpanel-realtime" class="tpanel-box">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
                <div>
                  <span class="badge badge-easy"><span class="live-pulse"></span> ĐỒNG BỘ REAL-TIME MỖI 3 GIÂY</span>
                  <span style="font-size:12px;color:var(--text-secondary);margin-left:8px">Theo dõi học sinh làm bài trực tuyến trên cùng hệ thống hoặc nhiều thiết bị.</span>
                </div>
                <button class="btn btn-amber btn-sm" onclick="window.VCodeMonitor.toggleDemoSimulation(this)">⚡ Bật Mô Phỏng Demo</button>
              </div>
              <div style="overflow-x:auto">
                <table class="data-table">
                  <thead><tr><th>Học sinh</th><th>Bài đang làm</th><th>Trạng thái</th><th>Tiến độ</th><th>Thao tác GV</th></tr></thead>
                  <tbody id="realtime-monitor-body"></tbody>
                </table>
              </div>
            </div>

            <div id="tpanel-assignments" class="tpanel-box" style="display:none">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <strong>Danh sách bài tập đã giao cho lớp này:</strong>
                <button class="btn btn-sm btn-primary" onclick="openCreateAssignmentModal()">+ Giao thêm bài mới</button>
              </div>
              <div id="teacher-assignments-list" style="margin-bottom:20px"></div>

              <strong style="display:block;margin-bottom:10px">Lịch sử nộp bài &amp; Điểm tự động (từ Database):</strong>
              <div style="overflow-x:auto">
                <table class="data-table">
                  <thead><tr><th>Học sinh</th><th>Mã bài tập</th><th>Test đạt</th><th>Điểm số</th><th>Thời gian nộp</th></tr></thead>
                  <tbody id="teacher-submissions-body"></tbody>
                </table>
              </div>
            </div>

            <div id="tpanel-students" class="tpanel-box" style="display:none">
              <div style="overflow-x:auto">
                <table class="data-table">
                  <thead><tr><th>STT</th><th>Họ và tên</th><th>Email</th><th>Điểm XP</th></tr></thead>
                  <tbody id="teacher-students-body"></tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== CỔNG HỌC SINH (NHẬP ID MÃ LỚP & LÀM BÀI TẬP) ==================== -->
      <div id="portal-student" style="display:none">
        <div class="olm-join-bar">
          <div style="flex:1;min-width:240px">
            <div style="font-weight:700;font-size:14.5px;margin-bottom:2px">🎓 Tham gia lớp học bằng ID Mã lớp</div>
            <div style="font-size:12px;color:var(--text-secondary)">Nhập mã lớp do thầy/cô chia sẻ (VD: <code style="color:var(--accent-emerald)">TIN10HP</code> hoặc mã lớp mới tạo) để vào lớp và làm bài tập được giao.</div>
          </div>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <input id="student-join-code-input" class="input-field mono" style="width:200px;text-transform:uppercase;font-weight:700" placeholder="Nhập ID mã lớp..." />
            <button class="btn btn-primary" onclick="joinClassByCodeAction()">+ Vào lớp ngay</button>
          </div>
        </div>

        <div class="grid-2col" style="grid-template-columns: 360px 1fr;align-items:start">
          <div>
            <h3 style="font-size:16px;margin-bottom:12px">🏫 Lớp học của em</h3>
            <div id="student-joined-classes-list"></div>
          </div>

          <div class="bento-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
              <div>
                <span class="bento-tag" style="margin-bottom:2px">Nhiệm vụ học tập</span>
                <h3 id="student-selected-class-title">Chọn một lớp học để xem bài tập được giao</h3>
              </div>
              <span id="student-selected-class-code" class="olm-code-chip" style="display:none"></span>
            </div>
            <div id="student-assignments-list">
              <p style="color:var(--text-secondary)">Hãy nhập mã lớp ở khung phía trên (thử mã <code>TIN10HP</code>) để vào lớp và làm bài tập!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>"""

NEW_AUTH_AND_CLASS_MODALS = """  <!-- ==================== MODAL 1: ĐĂNG NHẬP CHUYÊN NGHIỆP + ĐĂNG KÝ GỌN + GOOGLE/FACEBOOK ==================== -->
  <div id="auth-modal" class="modal-overlay">
    <div class="modal-box auth-modal-pro">
      <button class="modal-close" onclick="closeModal('auth-modal')">✕</button>

      <div class="auth-header-brand">
        <div class="brand-mark">V</div>
        <h2 id="auth-heading">Đăng nhập V-Code Edu</h2>
        <p id="auth-subheading">Tiếp tục hành trình học lập trình Python &amp; Scratch Live</p>
      </div>

      <div class="social-auth-grid">
        <button type="button" class="social-btn" onclick="openSocialAuthPrompt('google')">
          <svg width="17" height="17" viewBox="0 0 24 24"><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/><path fill="#4285F4" d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.86-3c-1.08.72-2.45 1.16-3.42 1.16-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/></svg>
          <span>Google</span>
        </button>
        <button type="button" class="social-btn" onclick="openSocialAuthPrompt('facebook')">
          <svg width="17" height="17" viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          <span>Facebook</span>
        </button>
        <button type="button" class="social-btn" onclick="openSocialAuthPrompt('github')">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
          <span>GitHub</span>
        </button>
      </div>

      <div class="auth-divider">hoặc tiếp tục bằng Email</div>

      <form id="auth-login-form" onsubmit="handleLoginSubmit(event)">
        <div class="auth-field">
          <label>Email</label>
          <input id="login-identifier" type="text" class="input-field" required placeholder="nhapemail@gmail.com (hoặc giaovien)" />
        </div>
        <div class="auth-field">
          <label>Mật khẩu</label>
          <div class="password-wrap">
            <input id="login-password" type="password" class="input-field" required placeholder="Nhập mật khẩu..." />
            <button type="button" class="password-toggle" onclick="togglePassVis('login-password')">👁</button>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:11px;margin-top:6px">Đăng nhập ngay</button>
        <div class="auth-switch-footer">
          Chưa có tài khoản? <button type="button" onclick="switchAuthTab('register')">Đăng ký tài khoản →</button>
        </div>
      </form>

      <form id="auth-register-form" style="display:none" onsubmit="handleRegisterSubmit(event)">
        <div class="auth-field">
          <label>Họ và tên</label>
          <input id="reg-fullname" type="text" class="input-field" required placeholder="VD: Nguyễn Minh Quân" />
        </div>
        <div class="auth-field">
          <label>Email</label>
          <input id="reg-email" type="email" class="input-field" required placeholder="VD: minhquan@gmail.com" />
        </div>
        <div class="auth-field">
          <label>Mật khẩu</label>
          <div class="password-wrap">
            <input id="reg-password" type="password" class="input-field" required minlength="6" placeholder="Tối thiểu 6 ký tự..." />
            <button type="button" class="password-toggle" onclick="togglePassVis('reg-password')">👁</button>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:11px;margin-top:6px">Tạo tài khoản miễn phí</button>
        <div class="auth-switch-footer">
          Đã có tài khoản? <button type="button" onclick="switchAuthTab('login')">Quay lại Đăng nhập</button>
        </div>
      </form>
    </div>
  </div>

  <!-- MODAL XÁC NHẬN TÀI KHOẢN GOOGLE / FACEBOOK / GITHUB -->
  <div id="social-auth-modal" class="modal-overlay">
    <div class="modal-box" style="max-width:400px">
      <button class="modal-close" onclick="closeModal('social-auth-modal')">✕</button>
      <span id="social-provider-badge" class="badge badge-blue" style="margin-bottom:8px">GOOGLE OAUTH</span>
      <h3 id="social-modal-title" style="margin-bottom:6px">Tiếp tục với Google</h3>
      <p style="font-size:12.5px;color:var(--text-secondary);margin-bottom:14px">Nhập tài khoản để đăng nhập / đăng ký đồng bộ trực tiếp vào CSDL V-Code Edu:</p>
      <form onsubmit="handleSocialAuthConfirm(event)">
        <input id="social-provider-val" type="hidden" value="google" />
        <div class="auth-field">
          <label>Họ tên hiển thị</label>
          <input id="social-fullname" class="input-field" required placeholder="VD: Nguyễn Văn A" />
        </div>
        <div class="auth-field">
          <label>Địa chỉ Email tài khoản</label>
          <input id="social-email" type="email" class="input-field" required placeholder="VD: nguyenvana@gmail.com" />
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:10px">Xác nhận &amp; Tiếp tục</button>
      </form>
    </div>
  </div>

  <!-- MODAL TẠO LỚP HỌC MỚI (GIÁO VIÊN) -->
  <div id="create-class-modal" class="modal-overlay">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal('create-class-modal')">✕</button>
      <span class="bento-tag">Cổng Giáo viên • V-Code Edu</span>
      <h3 style="margin-bottom:14px">Tạo Lớp học Trực tuyến Mới</h3>
      <form onsubmit="handleCreateClassSubmit(event)">
        <div class="auth-field"><label>Tên lớp học *</label><input id="new-class-name" class="input-field" required placeholder="VD: Tin học 10A2 — Trường THPT Hòa Phú" /></div>
        <div class="grid-2col" style="gap:10px;margin-bottom:12px">
          <div><label style="font-size:12px;color:var(--text-secondary)">Khối / Môn học</label><input id="new-class-subject" class="input-field" value="Tin học THPT • Python" style="margin-top:4px" /></div>
          <div><label style="font-size:12px;color:var(--text-secondary)">ID Mã lớp (bỏ trống tự tạo)</label><input id="new-class-code" class="input-field mono" placeholder="VD: TIN10A2" style="margin-top:4px;text-transform:uppercase" /></div>
        </div>
        <div class="auth-field"><label>Mô tả ngắn</label><input id="new-class-desc" class="input-field" placeholder="Lớp học thực hành Python & Scratch Live..." /></div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:10px">+ Tạo lớp &amp; Lấy Mã ID Chia sẻ</button>
      </form>
    </div>
  </div>

  <!-- MODAL GIAO BÀI TẬP CHO LỚP (GIÁO VIÊN) -->
  <div id="create-assignment-modal" class="modal-overlay">
    <div class="modal-box" style="max-width:540px">
      <button class="modal-close" onclick="closeModal('create-assignment-modal')">✕</button>
      <span class="bento-tag">Giao bài tập chấm tự động</span>
      <h3 style="margin-bottom:12px">Giao Bài Tập Python Cho Lớp <span id="assign-target-class" style="color:var(--accent-emerald)"></span></h3>
      <form onsubmit="handleCreateAssignmentSubmit(event)">
        <div class="auth-field"><label>Tên bài tập *</label><input id="assign-title" class="input-field" required placeholder="VD: Bài tập 3: Đếm số chia hết cho 3 từ 1 đến N" /></div>
        <div class="auth-field"><label>Đề bài yêu cầu *</label><input id="assign-desc" class="input-field" required placeholder="Nhập số nguyên dương N. In ra số lượng các số chia hết cho 3..." /></div>
        <div class="grid-2col" style="gap:10px;margin-bottom:12px">
          <div><label style="font-size:12px;color:var(--text-secondary)">Mức độ</label><select id="assign-diff" class="select-field" style="margin-top:4px"><option>Cơ bản</option><option>Trung bình</option><option>Nâng cao</option></select></div>
          <div><label style="font-size:12px;color:var(--text-secondary)">Hạn nộp</label><input id="assign-due" class="input-field" value="Cuối tuần này" style="margin-top:4px" /></div>
        </div>
        <div class="grid-2col" style="gap:10px;margin-bottom:12px">
          <div><label style="font-size:12px;color:var(--text-secondary)">Test Case Input *</label><input id="assign-in" class="input-field mono" required value="9" style="margin-top:4px" /></div>
          <div><label style="font-size:12px;color:var(--text-secondary)">Kết quả kỳ vọng (Output) *</label><input id="assign-out" class="input-field mono" required value="3" style="margin-top:4px" /></div>
        </div>
        <div class="auth-field">
          <label>Code khung gợi ý ban đầu cho học sinh:</label>
          <textarea id="assign-starter" class="input-field mono" rows="3">n = int(input())
# Viết lời giải của em bên dưới
</textarea>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:10px">✓ Giao bài tập ngay cho cả lớp</button>
      </form>
    </div>
  </div>"""

# ==============================================================================
# PHẦN 4: JS/APP.JS — KẾT NỐI ONLINE THẬT TỚI FASTAPI DATABASE + FALLBACK OFFLINE
# ==============================================================================
NEW_APP_JS = """// V-CODE EDU — BỘ ĐIỀU KHIỂN TRUNG TÂM SPA (AUTH GOOGLE/FB + LỚP HỌC CHUẨN OLM + REAL-TIME DB)
const ROLE_LABELS = {
  teacher: 'Giáo viên',
  student: 'Học sinh',
  admin: 'Quản trị viên',
  none: 'Thành viên mới'
};

const SNIPPETS = [
  { label: '+ Nhập số N', code: "n = int(input())\\n" },
  { label: '+ Vòng lặp for', code: "for i in range(1, n + 1):\\n    print(i)\\n" },
  { label: '+ Rẽ nhánh if/else', code: "if n % 2 == 0:\\n    print('Chan')\\nelse:\\n    print('Le')\\n" },
  { label: '+ Python Tiếng Việt', code: "n = nhap_so()\\nlap_voi i trong_khoang(1, n + 1):\\n    in_ra(i)\\n" }
];

window.AppState = {
  currentView: 'home',
  currentPortal: 'teacher',
  currentLesson: window.VCODE_LESSONS[2],
  activeClassroomCode: 'TIN10HP',
  activeStudentClassCode: '',
  user: JSON.parse(localStorage.getItem('vcode_current_user') || 'null') || {
    username: 'giaovien',
    email: 'giaovien@vcode.edu.vn',
    full_name: 'Thầy Nguyễn Phi Hùng',
    role: 'teacher',
    auth_provider: 'local',
    school_name: 'THCS & THPT Hòa Phú',
    class_name: 'Tổ Tin học',
    xp: 2500
  },
  completedLessons: window.VCodeOfflineDB.load().completedLessons || ['py-01'],
  teacherClasses: [],
  studentClasses: [],
  leaderboard: [
    { rank: 1, name: 'Trần Hoàng Nam', classCode: 'HSGPY26', solved: 18, time: '04:12', xp: 1850 },
    { rank: 2, name: 'Nguyễn Minh Quân', classCode: 'TIN10HP', solved: 15, time: '05:40', xp: 1450 },
    { rank: 3, name: 'Lê Thu Hà', classCode: 'TIN10HP', solved: 14, time: '06:15', xp: 1320 }
  ],
  peekStudentUsername: null,
  livePollTimer: null
};

function apiBase() {
  return window.VCodeAI.getConfig().backendUrl.replace(/\\/$/, '');
}

async function apiRequest(path, options = {}) {
  if (!navigator.onLine) throw new Error('OFFLINE');
  const res = await fetch(`${apiBase()}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Lỗi máy chủ (${res.status})`);
  return data;
}

function toggleLeftDrawer(forceState) {
  const btn = document.getElementById('hamburger-btn');
  const drawer = document.getElementById('left-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  const willOpen = typeof forceState === 'boolean' ? forceState : !drawer.classList.contains('open');
  btn?.classList.toggle('open', willOpen);
  drawer?.classList.toggle('open', willOpen);
  backdrop?.classList.toggle('open', willOpen);
}

function switchView(viewId) {
  document.querySelectorAll('.view-section').forEach((el) => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab, .drawer-item').forEach((el) => el.classList.remove('active'));
  document.getElementById(`view-${viewId}`)?.classList.add('active');
  document.querySelectorAll(`[data-view="${viewId}"]`).forEach((el) => el.classList.add('active'));
  window.AppState.currentView = viewId;
  toggleLeftDrawer(false);
  if (viewId === 'workspace') syncLiveEditorOutputs();
  if (viewId === 'classroom') initClassroomPortalData();
  if (viewId === 'learning') renderLearningPath();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showToast(msg) {
  const t = document.getElementById('toast-banner');
  if (!t) return;
  t.innerHTML = msg;
  t.style.display = 'block';
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { t.style.display = 'none'; }, 4200);
}

function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
function togglePassVis(id) {
  const el = document.getElementById(id);
  if (el) el.type = el.type === 'password' ? 'text' : 'password';
}

function openAuthModal(tab = 'login') {
  document.getElementById('auth-modal').classList.add('open');
  switchAuthTab(tab);
}

function switchAuthTab(tab) {
  const isLogin = tab === 'login';
  document.getElementById('auth-login-form').style.display = isLogin ? 'block' : 'none';
  document.getElementById('auth-register-form').style.display = isLogin ? 'none' : 'block';
  document.getElementById('auth-heading').textContent = isLogin ? 'Đăng nhập V-Code Edu' : 'Tạo tài khoản mới';
  document.getElementById('auth-subheading').textContent = isLogin
    ? 'Tiếp tục hành trình học lập trình Python & Scratch Live'
    : 'Chỉ cần Họ tên, Email và Mật khẩu — hoàn toàn miễn phí';
}

function saveLoggedInUser(userObj) {
  window.AppState.user = userObj;
  localStorage.setItem('vcode_current_user', JSON.stringify(userObj));
  updateUserHeaderUI();
  if (window.AppState.currentView === 'classroom') initClassroomPortalData();
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-identifier').value.trim();
  const password = document.getElementById('login-password').value;
  try {
    const data = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`👋 Đăng nhập thành công! Xin chào <b>${data.user.full_name}</b>.`);
  } catch (err) {
    if (err.message === 'OFFLINE' || err.message.includes('Failed to fetch')) {
      const db = window.VCodeOfflineDB.load();
      const localUser = db.users.find((u) => u.email === email.toLowerCase() || u.username === email.toLowerCase());
      if (localUser) {
        saveLoggedInUser(localUser);
        closeModal('auth-modal');
        showToast(`🟠 Đăng nhập chế độ Offline: <b>${localUser.full_name}</b>.`);
      } else {
        alert('Không kết nối được máy chủ Backend (cổng 8000) và chưa có tài khoản này trong máy. Hãy bật server hoặc đăng ký mới!');
      }
    } else {
      alert(err.message);
    }
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const full_name = document.getElementById('reg-fullname').value.trim();
  const email = document.getElementById('reg-email').value.trim().toLowerCase();
  const password = document.getElementById('reg-password').value;

  try {
    const data = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ full_name, email, password })
    });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`🎉 Tạo tài khoản thành công cho <b>${data.user.full_name}</b>! Vào mục Lớp học để chọn Giáo viên hoặc Học sinh.`);
  } catch (err) {
    if (err.message === 'OFFLINE' || err.message.includes('Failed to fetch')) {
      const fallbackUser = {
        username: email.split('@')[0],
        email,
        full_name,
        role: 'none',
        auth_provider: 'local',
        school_name: 'THCS & THPT Hòa Phú',
        class_name: '',
        xp: 100
      };
      const db = window.VCodeOfflineDB.load();
      db.users.push(fallbackUser);
      window.VCodeOfflineDB.save(db);
      saveLoggedInUser(fallbackUser);
      closeModal('auth-modal');
      showToast(`🟠 Đã đăng ký cục bộ (Offline) cho <b>${full_name}</b>.`);
    } else {
      alert(err.message);
    }
  }
}

function openSocialAuthPrompt(provider) {
  const names = { google: 'Google', facebook: 'Facebook', github: 'GitHub' };
  document.getElementById('social-provider-val').value = provider;
  document.getElementById('social-provider-badge').textContent = `${names[provider].toUpperCase()} OAUTH`;
  document.getElementById('social-modal-title').textContent = `Tiếp tục với tài khoản ${names[provider]}`;
  document.getElementById('social-auth-modal').classList.add('open');
}

async function handleSocialAuthConfirm(e) {
  e.preventDefault();
  const provider = document.getElementById('social-provider-val').value;
  const full_name = document.getElementById('social-fullname').value.trim();
  const email = document.getElementById('social-email').value.trim().toLowerCase();

  try {
    const data = await apiRequest('/api/auth/social', {
      method: 'POST',
      body: JSON.stringify({ provider, email, full_name })
    });
    saveLoggedInUser(data.user);
    closeModal('social-auth-modal');
    closeModal('auth-modal');
    showToast(`✅ Đã kết nối tài khoản <b>${provider.toUpperCase()}</b> — Xin chào <b>${data.user.full_name}</b>!`);
  } catch (err) {
    const fallbackUser = {
      username: email.split('@')[0],
      email,
      full_name,
      role: 'none',
      auth_provider: provider,
      school_name: 'THCS & THPT Hòa Phú',
      class_name: '',
      xp: 150
    };
    saveLoggedInUser(fallbackUser);
    closeModal('social-auth-modal');
    closeModal('auth-modal');
    showToast(`🟠 Kết nối ${provider.toUpperCase()} cục bộ cho <b>${full_name}</b>.`);
  }
}

function updateUserHeaderUI() {
  const u = window.AppState.user;
  document.getElementById('user-xp-badge').textContent = `${u.xp || 100} XP`;
  document.getElementById('user-profile-btn').textContent = `👤 ${u.full_name}`;
  const drawerUser = document.getElementById('drawer-user-summary');
  if (drawerUser) {
    const prov = u.auth_provider && u.auth_provider !== 'local' ? ` • ${u.auth_provider.toUpperCase()}` : '';
    drawerUser.innerHTML = `<strong>${u.full_name}</strong><div style="font-size:11.5px;color:var(--text-secondary)">${u.email || u.username}</div><div style="font-size:11.5px;color:var(--accent-emerald);margin-top:2px">${ROLE_LABELS[u.role] || 'Thành viên'}${prov}</div>`;
  }
}

function switchClassroomPortal(roleTab) {
  window.AppState.currentPortal = roleTab;
  document.getElementById('olm-tab-teacher').classList.toggle('active', roleTab === 'teacher');
  document.getElementById('olm-tab-student').classList.toggle('active', roleTab === 'student');
  document.getElementById('portal-teacher').style.display = roleTab === 'teacher' ? 'block' : 'none';
  document.getElementById('portal-student').style.display = roleTab === 'student' ? 'block' : 'none';
  initClassroomPortalData();
}

function switchTeacherSubpanel(panelName) {
  document.querySelectorAll('[data-tpanel]').forEach((b) => b.classList.toggle('active', b.dataset.tpanel === panelName));
  document.querySelectorAll('.tpanel-box').forEach((p) => { p.style.display = p.id === `tpanel-${panelName}` ? 'block' : 'none'; });
}

async function activateClassroomRole(role) {
  const u = window.AppState.user;
  const school = document.getElementById('reg-teacher-school')?.value || 'THCS & THPT Hòa Phú';
  const dept = document.getElementById('reg-teacher-dept')?.value || 'Tổ Tin học';
  try {
    const data = await apiRequest('/api/auth/set-role', {
      method: 'POST',
      body: JSON.stringify({ email: u.email || u.username, role, school_name: school, class_name: dept })
    });
    saveLoggedInUser(data.user);
    showToast(`🎉 Đã kích hoạt quyền <b>${ROLE_LABELS[role]}</b> thành công trong Database!`);
  } catch (err) {
    u.role = role;
    u.school_name = school;
    saveLoggedInUser(u);
    showToast(`✔ Đã kích hoạt quyền <b>${ROLE_LABELS[role]}</b>.`);
  }
}

async function initClassroomPortalData() {
  const u = window.AppState.user;
  const isTeacher = u.role === 'teacher' || u.role === 'admin';
  const regCard = document.getElementById('teacher-register-card');
  const dash = document.getElementById('teacher-dashboard');
  if (regCard && dash) {
    regCard.style.display = isTeacher ? 'none' : 'block';
    dash.style.display = isTeacher ? 'block' : 'none';
  }

  if (window.AppState.currentPortal === 'teacher' && isTeacher) {
    try {
      const res = await apiRequest(`/api/classes/teacher/${encodeURIComponent(u.email || u.username)}`);
      window.AppState.teacherClasses = res.classes || [];
    } catch {
      if (window.AppState.teacherClasses.length === 0) {
        window.AppState.teacherClasses = [{ code: 'TIN10HP', name: 'Tin học 10A1 — THCS & THPT Hòa Phú', grade_subject: 'Tin học 10 • Python', students_count: 2, assignments_count: 2 }];
      }
    }
    renderTeacherClassesGrid();
    if (window.AppState.teacherClasses.length > 0) {
      const exists = window.AppState.teacherClasses.some((c) => c.code === window.AppState.activeClassroomCode);
      const targetCode = exists ? window.AppState.activeClassroomCode : window.AppState.teacherClasses[0].code;
      selectTeacherClassroom(targetCode);
    }
    startLiveMonitoringPolling();
  }

  if (window.AppState.currentPortal === 'student') {
    try {
      const res = await apiRequest(`/api/classes/student/${encodeURIComponent(u.email || u.username)}`);
      window.AppState.studentClasses = res.classes || [];
    } catch {}
    renderStudentJoinedClasses();
  }
}

function renderTeacherClassesGrid() {
  const grid = document.getElementById('teacher-classes-grid');
  if (!grid) return;
  if (window.AppState.teacherClasses.length === 0) {
    grid.innerHTML = `<div class="bento-card" style="grid-column:span 3;text-align:center"><p>Bạn chưa tạo lớp học nào. Hãy bấm <b>+ Tạo lớp học mới</b> để bắt đầu!</p></div>`;
    return;
  }
  grid.innerHTML = window.AppState.teacherClasses.map((c) => `
    <div class="olm-class-card ${c.code === window.AppState.activeClassroomCode ? 'selected' : ''}" onclick="selectTeacherClassroom('${c.code}')">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span class="olm-code-chip">${c.code}</span>
        <span class="badge badge-blue">${c.students_count || 0} HS</span>
      </div>
      <h4 style="font-size:15px;margin-bottom:4px">${c.name}</h4>
      <div style="font-size:12px;color:var(--text-secondary)">${c.grade_subject || 'Python THPT'} • ${c.assignments_count || 0} bài tập</div>
    </div>`).join('');
}

async function selectTeacherClassroom(code) {
  window.AppState.activeClassroomCode = code;
  renderTeacherClassesGrid();
  document.getElementById('teacher-selected-class-code').textContent = code;
  try {
    const detail = await apiRequest(`/api/classes/${encodeURIComponent(code)}/detail`);
    document.getElementById('teacher-selected-class-title').textContent = detail.classroom.name;
    const aList = document.getElementById('teacher-assignments-list');
    aList.innerHTML = detail.assignments.length
      ? detail.assignments.map((a) => `
        <div class="olm-assignment-row">
          <div>
            <strong>${a.title}</strong> <span class="badge badge-easy">${a.difficulty}</span>
            <div style="font-size:12px;color:var(--text-secondary)">${a.description} • Hạn: ${a.due_date}</div>
          </div>
          <span class="mono badge badge-blue">${a.code}</span>
        </div>`).join('')
      : `<p style="color:var(--text-secondary);font-size:13px">Chưa có bài tập nào trong lớp này. Bấm <b>+ Giao thêm bài mới</b> nhé!</p>`;

    const sBody = document.getElementById('teacher-submissions-body');
    sBody.innerHTML = detail.submissions.length
      ? detail.submissions.map((s) => `
        <tr>
          <td><strong>${s.student_name}</strong></td>
          <td class="mono">${s.assignment_code}</td>
          <td class="mono">${s.passed_tests}/${s.total_tests}</td>
          <td><span class="badge ${s.score === 100 ? 'badge-easy' : 'badge-med'}">${s.score}/100</span></td>
          <td class="mono" style="font-size:12px">${s.submitted_at}</td>
        </tr>`).join('')
      : `<tr><td colspan="5" style="color:var(--text-secondary)">Chưa có học sinh nào nộp bài tập trong lớp này.</td></tr>`;

    const stBody = document.getElementById('teacher-students-body');
    stBody.innerHTML = detail.students.length
      ? detail.students.map((st, idx) => `
        <tr><td>${idx + 1}</td><td><strong>${st.full_name}</strong></td><td>${st.email}</td><td class="mono" style="color:var(--accent-emerald)">${st.xp} XP</td></tr>`).join('')
      : `<tr><td colspan="4" style="color:var(--text-secondary)">Chưa có học sinh tham gia. Hãy gửi mã lớp <b>${code}</b> cho học sinh!</td></tr>`;
  } catch {
    document.getElementById('teacher-selected-class-title').textContent = `Lớp ${code} (Chế độ Offline)`;
  }
  await fetchLiveStudentsFromBackend();
}

async function handleCreateClassSubmit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('new-class-name').value.trim(),
    grade_subject: document.getElementById('new-class-subject').value.trim(),
    code: document.getElementById('new-class-code').value.trim().toUpperCase(),
    description: document.getElementById('new-class-desc').value.trim(),
    teacher_email: window.AppState.user.email || window.AppState.user.username
  };
  try {
    const res = await apiRequest('/api/classes/create', { method: 'POST', body: JSON.stringify(payload) });
    closeModal('create-class-modal');
    e.target.reset();
    window.AppState.activeClassroomCode = res.classroom.code;
    showToast(`🎉 Đã tạo lớp <b>${res.classroom.name}</b> — Mã lớp ID: <b>${res.classroom.code}</b>`);
    initClassroomPortalData();
  } catch (err) {
    alert(err.message);
  }
}

function openCreateAssignmentModal() {
  document.getElementById('assign-target-class').textContent = window.AppState.activeClassroomCode;
  document.getElementById('create-assignment-modal').classList.add('open');
}

async function handleCreateAssignmentSubmit(e) {
  e.preventDefault();
  const payload = {
    classroom_code: window.AppState.activeClassroomCode,
    title: document.getElementById('assign-title').value.trim(),
    description: document.getElementById('assign-desc').value.trim(),
    difficulty: document.getElementById('assign-diff').value,
    due_date: document.getElementById('assign-due').value.trim(),
    starter_code: document.getElementById('assign-starter').value,
    test_cases: [{ input: document.getElementById('assign-in').value.trim(), expected: document.getElementById('assign-out').value.trim() }],
    created_by: window.AppState.user.username
  };
  try {
    await apiRequest('/api/assessment/create', { method: 'POST', body: JSON.stringify(payload) });
    closeModal('create-assignment-modal');
    e.target.reset();
    showToast(`📝 Đã giao bài tập <b>${payload.title}</b> cho lớp ${payload.classroom_code}!`);
    selectTeacherClassroom(payload.classroom_code);
    switchTeacherSubpanel('assignments');
  } catch (err) {
    alert(err.message);
  }
}

function copyActiveClassCode() {
  const code = window.AppState.activeClassroomCode;
  navigator.clipboard?.writeText(code);
  showToast(`📋 Đã sao chép ID mã lớp: <b>${code}</b>`);
}

function shareActiveClassQR() {
  const code = window.AppState.activeClassroomCode;
  const base = window.location.href.split('#')[0];
  const joinUrl = `${base}#join=${code}`;
  document.getElementById('share-link-input').value = joinUrl;
  const qrContainer = document.getElementById('qr-code-box');
  qrContainer.innerHTML = '';
  if (typeof QRCode !== 'undefined') {
    new QRCode(qrContainer, { text: joinUrl, width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  }
  document.getElementById('share-modal').classList.add('open');
}

async function joinClassByCodeAction(explicitCode) {
  const inp = document.getElementById('student-join-code-input');
  const code = (explicitCode || inp?.value || '').trim().toUpperCase();
  if (!code) { alert('Vui lòng nhập ID mã lớp học!'); return; }
  const u = window.AppState.user;
  try {
    const res = await apiRequest('/api/classes/join', {
      method: 'POST',
      body: JSON.stringify({ code, student_email: u.email || u.username })
    });
    if (inp) inp.value = '';
    showToast(`🎉 Đã tham gia lớp <b>${res.classroom.name}</b> thành công!`);
    await initClassroomPortalData();
    openStudentClassDetail(res.classroom.code);
  } catch (err) {
    alert(err.message);
  }
}

function renderStudentJoinedClasses() {
  const box = document.getElementById('student-joined-classes-list');
  if (!box) return;
  if (window.AppState.studentClasses.length === 0) {
    box.innerHTML = `<div class="bento-card"><p style="font-size:13px;color:var(--text-secondary)">Em chưa tham gia lớp học nào. Hãy nhập ID mã lớp (ví dụ: <b>TIN10HP</b>) ở khung phía trên để vào lớp!</p></div>`;
    return;
  }
  box.innerHTML = window.AppState.studentClasses.map((c) => `
    <div class="olm-class-card ${c.code === window.AppState.activeStudentClassCode ? 'selected' : ''}" style="margin-bottom:10px" onclick="openStudentClassDetail('${c.code}')">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span class="olm-code-chip">${c.code}</span>
        <span class="badge badge-easy">${c.assignments_count || 0} bài tập</span>
      </div>
      <strong style="display:block;font-size:14.5px;margin-bottom:3px">${c.name}</strong>
      <div style="font-size:12px;color:var(--text-secondary)">GV: ${c.teacher_name}</div>
    </div>`).join('');

  if (!window.AppState.activeStudentClassCode && window.AppState.studentClasses.length > 0) {
    openStudentClassDetail(window.AppState.studentClasses[0].code);
  }
}

async function openStudentClassDetail(code) {
  window.AppState.activeStudentClassCode = code;
  renderStudentJoinedClasses();
  try {
    const detail = await apiRequest(`/api/classes/${encodeURIComponent(code)}/detail`);
    document.getElementById('student-selected-class-title').textContent = detail.classroom.name;
    const chip = document.getElementById('student-selected-class-code');
    chip.textContent = `Mã lớp: ${code}`;
    chip.style.display = 'inline-flex';

    const listEl = document.getElementById('student-assignments-list');
    if (!detail.assignments.length) {
      listEl.innerHTML = `<p style="color:var(--text-secondary)">Thầy/cô chưa giao bài tập nào cho lớp này.</p>`;
      return;
    }
    window.__classAssignmentsCache = detail.assignments;
    listEl.innerHTML = detail.assignments.map((a, idx) => {
      const mySubs = detail.submissions.filter((s) => s.assignment_code === a.code && s.username === window.AppState.user.username);
      const best = mySubs.length ? Math.max(...mySubs.map((s) => s.score)) : null;
      return `
        <div class="olm-assignment-row">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <strong>${a.title}</strong>
              <span class="badge badge-blue">${a.difficulty}</span>
              ${best !== null ? `<span class="badge badge-easy">✓ Điểm cao nhất: ${best}/100</span>` : `<span class="badge badge-med">Chưa làm</span>`}
            </div>
            <div style="font-size:12.5px;color:var(--text-secondary)">${a.description} • Hạn nộp: ${a.due_date}</div>
          </div>
          <button class="btn btn-primary btn-sm" onclick="startClassAssignmentInIDE(${idx}, '${code}')">💻 Làm bài ngay →</button>
        </div>`;
    }).join('');
  } catch (err) {
    showToast(`⚠️ Không tải được bài tập lớp ${code}: ${err.message}`);
  }
}

function startClassAssignmentInIDE(idx, classCode) {
  const a = (window.__classAssignmentsCache || [])[idx];
  if (!a) return;
  window.AppState.currentLesson = {
    id: a.code,
    title: a.title,
    summary: a.description,
    starter: a.starter_code,
    testCases: a.test_cases,
    classroom_code: classCode
  };
  document.getElementById('prob-title').textContent = `[Lớp ${classCode}] ${a.title}`;
  document.getElementById('prob-desc').textContent = a.description;
  document.getElementById('code-editor').value = a.starter_code || '';
  if (a.test_cases && a.test_cases[0]) {
    document.getElementById('custom-stdin').value = a.test_cases[0].input;
  }
  switchView('workspace');
  syncLiveEditorOutputs();
  showToast(`💻 Đang làm bài tập lớp <b>${classCode}</b> — Trạng thái đang đồng bộ Real-time về Giáo viên!`);
}

async function fetchLiveStudentsFromBackend() {
  try {
    const code = window.AppState.activeClassroomCode;
    const data = await apiRequest(`/api/monitor/live?class_code=${encodeURIComponent(code)}`);
    if (data.students && data.students.length > 0) {
      data.students.forEach((st) => {
        window.VCodeMonitor.upsertStudent({
          username: st.username,
          name: st.name,
          classCode: st.classCode,
          problem: st.problem,
          status: st.status,
          progress: st.progress,
          errors: st.errors,
          code: st.code
        });
      });
    }
  } catch {}
  renderLiveMonitorTable();
}

function startLiveMonitoringPolling() {
  clearInterval(window.AppState.livePollTimer);
  window.AppState.livePollTimer = setInterval(() => {
    if (window.AppState.currentView === 'classroom' && window.AppState.currentPortal === 'teacher') {
      fetchLiveStudentsFromBackend();
    }
  }, 3000);
}

function switchRightTab(tabName) {
  document.querySelectorAll('.subtab-btn').forEach((b) => b.classList.toggle('active', b.dataset.rtab === tabName));
  document.querySelectorAll('.right-panel').forEach((p) => p.classList.toggle('active', p.id === `rpanel-${tabName}`));
}

function syncLiveEditorOutputs() {
  const editor = document.getElementById('code-editor');
  if (!editor) return;
  const code = editor.value;
  const linesEl = document.getElementById('line-numbers');
  if (linesEl) linesEl.innerHTML = Array.from({ length: code.split('\\n').length }, (_, i) => i + 1).join('<br>');
  const scratchStage = document.getElementById('scratch-live-stage');
  if (scratchStage) scratchStage.innerHTML = window.ScratchBridge.renderFromPython(code);
  const flowBox = document.getElementById('flowchart-box');
  if (flowBox) flowBox.innerHTML = window.VCodeAI.generateFlowchartSVG(code);

  localStorage.setItem('vcode_draft_' + window.AppState.currentLesson.id, code);
  clearTimeout(window.__rtTimer);
  window.__rtTimer = setTimeout(() => {
    const targetClass = window.AppState.currentLesson.classroom_code || window.AppState.activeStudentClassCode || 'TIN10HP';
    window.VCodeMonitor.emitStudentActivity(
      { ...window.AppState.user, class_name: targetClass },
      window.AppState.currentLesson.title,
      code,
      'coding',
      Math.min(90, Math.max(20, code.split('\\n').length * 11)),
      0
    );
  }, 600);
}

function openLessonInIDE(lessonId) {
  const found = window.VCODE_LESSONS.find((l) => l.id === lessonId);
  if (!found) return;
  window.AppState.currentLesson = found;
  document.getElementById('prob-title').textContent = found.title;
  document.getElementById('prob-desc').textContent = found.summary;
  const saved = localStorage.getItem('vcode_draft_' + found.id);
  document.getElementById('code-editor').value = saved || found.starter;
  renderSidebarProblems();
  switchView('workspace');
  syncLiveEditorOutputs();
}

function runCodeAction() {
  const code = document.getElementById('code-editor').value;
  const stdin = document.getElementById('custom-stdin').value.split('\\n');
  const consoleEl = document.getElementById('console-output');
  const res = window.VCodeIDE.runPython(code, stdin);
  const targetClass = window.AppState.currentLesson.classroom_code || window.AppState.activeStudentClassCode || 'TIN10HP';

  if (res.ok) {
    consoleEl.textContent = `>>> Thực thi hoàn tất (0.01s):\\n${res.output || '(Không có dữ liệu in ra)'}`;
    appendAIChat('ai', `✓ Mã nguồn chạy thành công! Kết quả: "${res.output}". Bấm "✓ Chấm Test Case" để nộp bài lấy điểm.`);
    window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: targetClass }, window.AppState.currentLesson.title, code, 'coding', 85, 0);
  } else {
    consoleEl.textContent = `>>> Lỗi thực thi:\\n${res.error}`;
    appendAIChat('error', window.VCodeAI.offlineDiagnose('', code, res.error));
    switchRightTab('ai');
    window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: targetClass }, window.AppState.currentLesson.title, code, 'error', 40, 1);
  }
}

async function submitAutoGradeAction() {
  const code = document.getElementById('code-editor').value;
  const lesson = window.AppState.currentLesson;
  const report = window.VCodeIDE.gradeSubmission(code, lesson.testCases || [{ input: '6', expected: '12' }]);
  let out = `=== CHẤM TỰ ĐỘNG: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\\n`;
  report.details.forEach((d) => {
    out += `• Test #${d.index} [Input: ${d.input}]: ${d.passed ? '✓ ĐẠT' : `✗ SAI (Ra '${d.actual}', cần '${d.expected}')`}\\n`;
  });
  document.getElementById('console-output').textContent = out;
  switchRightTab('ai');

  const targetClass = lesson.classroom_code || window.AppState.activeStudentClassCode || 'TIN10HP';
  try {
    const saved = await apiRequest('/api/assessment/submit', {
      method: 'POST',
      body: JSON.stringify({
        email: window.AppState.user.email || window.AppState.user.username,
        student_name: window.AppState.user.full_name,
        classroom_code: targetClass,
        assignment_code: lesson.id,
        source_code: code,
        passed_tests: report.passed,
        total_tests: report.total,
        score: report.score
      })
    });
    if (saved.new_xp) {
      window.AppState.user.xp = saved.new_xp;
      updateUserHeaderUI();
    }
  } catch {
    window.VCodeOfflineDB.enqueueSync({ type: 'submission', lessonId: lesson.id, score: report.score });
  }

  if (report.score === 100) {
    if (!window.AppState.completedLessons.includes(lesson.id)) {
      window.AppState.completedLessons.push(lesson.id);
      const db = window.VCodeOfflineDB.load();
      db.completedLessons = window.AppState.completedLessons;
      window.VCodeOfflineDB.save(db);
    }
    window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: targetClass }, lesson.title, code, 'completed', 100, 0);
    showToast('🎉 Đạt 100/100 điểm! Bài làm đã được lưu trực tiếp lên bảng điểm lớp học.');
  }
}

function appendAIChat(kind, text, badgeLabel = '') {
  const feed = document.getElementById('ai-chat-feed');
  if (!feed) return;
  const div = document.createElement('div');
  div.className = `chat-msg ${kind}`;
  div.innerHTML = (badgeLabel ? `<div style="font-size:10.5px;color:var(--accent-emerald);margin-bottom:3px;font-weight:700">${badgeLabel}</div>` : '') + text.replace(/\\n/g, '<br>');
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

async function sendAIChatAction() {
  const input = document.getElementById('ai-question-input');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  appendAIChat('user', q);
  const code = document.getElementById('code-editor').value;
  const res = await window.VCodeAI.askHybrid(q, code);
  appendAIChat('ai', res.text, res.mode === 'offline' ? '🟠 AI Socratic Offline' : '🟢 AI Online API');
}

function openShareModal() {
  const code = document.getElementById('code-editor').value;
  const payload = btoa(unescape(encodeURIComponent(JSON.stringify({ title: window.AppState.currentLesson.title, code }))));
  const base = window.location.href.split('#')[0];
  const shareUrl = `${base}#share=${payload}`;
  document.getElementById('share-link-input').value = shareUrl;
  const qrContainer = document.getElementById('qr-code-box');
  qrContainer.innerHTML = '';
  if (typeof QRCode !== 'undefined') {
    new QRCode(qrContainer, { text: shareUrl.slice(0, 900), width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  }
  document.getElementById('share-modal').classList.add('open');
}

function copyShareLink() {
  const inp = document.getElementById('share-link-input');
  inp.select();
  navigator.clipboard?.writeText(inp.value);
  showToast('🔗 Đã sao chép đường link chia sẻ!');
}

function downloadPythonFile() {
  const code = document.getElementById('code-editor').value;
  const blob = new Blob([code], { type: 'text/x-python;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${window.AppState.currentLesson.id}_vcode_edu.py`;
  a.click();
}

function renderLiveMonitorTable() {
  const tbody = document.getElementById('realtime-monitor-body');
  if (!tbody) return;
  tbody.innerHTML = window.VCodeMonitor.students.map((s) => {
    const statusMap = {
      coding: `<span class="badge badge-blue"><span class="live-pulse"></span> Đang gõ code</span>`,
      completed: `<span class="badge badge-easy">✓ Hoàn thành</span>`,
      error: `<span class="badge badge-hard">⚠ Gặp lỗi (${s.errors})</span>`,
      idle: `<span class="badge badge-med">⏸ Tạm dừng</span>`
    };
    return `
      <tr>
        <td><strong>${s.name}</strong><div style="font-size:11px;color:var(--text-muted)">${s.classCode} • ${s.updated}</div></td>
        <td>${s.problem}</td>
        <td>${statusMap[s.status] || statusMap.coding}</td>
        <td style="min-width:130px"><div style="font-size:11px;margin-bottom:4px" class="mono">${s.progress}%</div><div class="progress-track"><div class="progress-fill" style="width:${s.progress}%"></div></div></td>
        <td><button class="btn btn-sm btn-primary" onclick="openPeekModal('${s.username}')">👁 Xem code trực tiếp</button></td>
      </tr>`;
  }).join('');
}

function openPeekModal(username) {
  const st = window.VCodeMonitor.students.find((s) => s.username === username);
  if (!st) return;
  window.AppState.peekStudentUsername = username;
  document.getElementById('peek-student-name').textContent = `${st.name} (${st.classCode})`;
  document.getElementById('peek-student-problem').textContent = st.problem;
  document.getElementById('peek-code-preview').textContent = st.code;
  document.getElementById('peek-modal').classList.add('open');
}

function sendTeacherHintAction() {
  const txt = document.getElementById('teacher-hint-input').value.trim();
  if (!txt || !window.AppState.peekStudentUsername) return;
  window.VCodeMonitor.sendHintToStudent(window.AppState.peekStudentUsername, txt);
  document.getElementById('teacher-hint-input').value = '';
  closeModal('peek-modal');
  showToast('💬 Đã gửi gợi ý trực tiếp tới màn hình học sinh!');
}

function renderLearningPath() {
  const grid = document.getElementById('learning-lessons-grid');
  if (!grid) return;
  const doneCount = window.AppState.completedLessons.length;
  const pct = Math.round((doneCount / window.VCODE_LESSONS.length) * 100);
  document.getElementById('learning-progress-text').textContent = `Đã hoàn thành ${doneCount}/${window.VCODE_LESSONS.length} bài học Python (${pct}%)`;
  document.getElementById('learning-progress-bar').style.width = `${pct}%`;
  grid.innerHTML = window.VCODE_LESSONS.map((l) => {
    const done = window.AppState.completedLessons.includes(l.id);
    return `
      <div class="bento-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã hoàn thành' : l.level}</span>
          <span class="mono" style="font-size:11.5px;color:var(--text-muted)">⏱ ${l.duration}</span>
        </div>
        <h3>${l.title}</h3>
        <p style="margin-bottom:10px">${l.summary}</p>
        <div style="font-size:12.5px;color:var(--text-secondary);background:var(--bg-elevated);padding:10px;border-radius:8px;margin-bottom:14px">${l.theory}</div>
        <button class="btn btn-sm btn-primary" onclick="openLessonInIDE('${l.id}')">💻 Thực hành &amp; Xem Scratch Live →</button>
      </div>`;
  }).join('');
}

function saveAIConfig() {
  localStorage.setItem('vcode_backend_url', document.getElementById('cfg-backend-url').value.trim() || 'http://localhost:8000');
  localStorage.setItem('vcode_gemini_key', document.getElementById('cfg-gemini-key').value.trim());
  closeModal('ai-config-modal');
  showToast('⚙️ Đã lưu cấu hình Kết nối AI & Backend!');
}

function renderSidebarProblems() {
  const el = document.getElementById('problem-list');
  if (!el) return;
  el.innerHTML = window.VCODE_LESSONS.map((l) => `
    <div onclick="openLessonInIDE('${l.id}')" style="padding:10px;border:1px solid ${window.AppState.currentLesson.id === l.id ? 'var(--accent-emerald)' : 'var(--border-subtle)'};border-radius:8px;margin-bottom:8px;cursor:pointer;background:var(--bg-surface)">
      <strong style="font-size:12.5px">${l.title}</strong>
      <div style="font-size:11px;color:var(--text-secondary);margin-top:3px">${l.level}</div>
    </div>`).join('');
}

function exportGradesCSV() {
  let csv = "Hang,Ho Ten,Ma Lop,Bai Giai Dung,Thoi Gian,XP\\n";
  window.AppState.leaderboard.forEach((r) => { csv += `${r.rank},"${r.name}",${r.classCode},${r.solved},${r.time},${r.xp}\\n`; });
  const blob = new Blob(["\\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = "Bang_Diem_VCode_Edu.csv";
  a.click();
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('vcode_theme', next);
}

window.insertSnippet = function(idx) {
  const ed = document.getElementById('code-editor');
  ed.value += (ed.value.endsWith('\\n') ? '' : '\\n') + SNIPPETS[idx].code;
  syncLiveEditorOutputs();
};

function checkHashActionsOnLoad() {
  if (window.location.hash.startsWith('#share=')) {
    try {
      const decoded = JSON.parse(decodeURIComponent(escape(atob(window.location.hash.replace('#share=', '')))));
      document.getElementById('prob-title').textContent = decoded.title || 'Mã nguồn được chia sẻ';
      document.getElementById('code-editor').value = decoded.code || '';
      switchView('workspace');
      syncLiveEditorOutputs();
      showToast('🔗 Đã nạp mã nguồn được chia sẻ qua Link / Mã QR!');
      return true;
    } catch {}
  }
  if (window.location.hash.startsWith('#join=')) {
    const classCode = window.location.hash.replace('#join=', '').trim().toUpperCase();
    switchView('classroom');
    switchClassroomPortal('student');
    const inp = document.getElementById('student-join-code-input');
    if (inp) inp.value = classCode;
    showToast(`🎓 Đã nhận mã lớp <b>${classCode}</b>! Bấm "+ Vào lớp ngay" để tham gia.`);
    return true;
  }
  return false;
}

window.addEventListener('DOMContentLoaded', () => {
  document.documentElement.setAttribute('data-theme', localStorage.getItem('vcode_theme') || 'dark');
  document.getElementById('snippet-bar').innerHTML = SNIPPETS.map((s, i) => `<button class="snippet-chip" onclick="insertSnippet(${i})">${s.label}</button>`).join('');
  document.getElementById('arena-leaderboard-body').innerHTML = window.AppState.leaderboard.map((r) => `
    <tr><td class="mono"><strong>#${r.rank}</strong></td><td><strong>${r.name}</strong></td><td><span class="badge badge-easy">${r.classCode}</span></td><td>${r.solved} bài</td><td class="mono">${r.time}</td><td class="mono" style="color:var(--accent-emerald);font-weight:700">${r.xp} XP</td></tr>`).join('');

  window.VCodeMonitor.init(
    () => renderLiveMonitorTable(),
    (hint) => showToast(`👨‍🏫 <b>Gợi ý trực tiếp từ Giáo viên:</b> ${hint.hintText}`)
  );

  const pill = document.getElementById('network-status');
  function syncNet() {
    if (navigator.onLine) {
      pill.classList.remove('offline');
      pill.innerHTML = `<span class="status-dot"></span><span>Online • Đồng bộ Cloud</span>`;
      window.VCodeOfflineDB.flushSync(apiBase());
    } else {
      pill.classList.add('offline');
      pill.innerHTML = `<span class="status-dot"></span><span>Offline • Lưu cục bộ PWA</span>`;
    }
  }
  window.addEventListener('online', syncNet);
  window.addEventListener('offline', syncNet);
  syncNet();

  updateUserHeaderUI();
  renderSidebarProblems();
  renderLearningPath();
  renderLiveMonitorTable();

  if (!checkHashActionsOnLoad()) {
    openLessonInIDE('py-03');
    switchView('home');
  }
});
"""

def apply_upgrade():
    for rel, content in BACKEND_FILES.items():
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✔ Đã cập nhật Backend: {rel}")

    css_path = "css/design-system.css"
    old_css = open(css_path, "r", encoding="utf-8").read() if os.path.exists(css_path) else ""
    marker = "/* ==================== PROFESSIONAL AUTH MODAL & SOCIAL OAUTH ==================== */"
    if marker in old_css:
        old_css = old_css.split(marker)[0].rstrip()
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(old_css + "\n\n" + EXTRA_UI_CSS.strip() + "\n")
    print("✔ Đã cập nhật CSS: css/design-system.css")

    with open("js/app.js", "w", encoding="utf-8") as f:
        f.write(NEW_APP_JS.strip() + "\n")
    print("✔ Đã cập nhật JS điều khiển: js/app.js")

    for html_file in ["index.html", "index_2.html"]:
        if not os.path.exists(html_file):
            continue
        html = open(html_file, "r", encoding="utf-8").read()

        html = html.replace("✨ Đăng nhập / Đăng ký đa dạng", "🔑 Đăng nhập / Đăng ký")
        html = html.replace("openAuthModal('register')", "openAuthModal('login')")

        cls_start = html.find('<section id="view-classroom" class="view-section">')
        arena_marker = html.find('<!-- ==================== VIEW 5:')
        if cls_start != -1 and arena_marker != -1:
            html = html[:cls_start] + NEW_CLASSROOM_SECTION.strip() + "\n\n  " + html[arena_marker:]

        auth_start = html.find('<div id="auth-modal" class="modal-overlay">')
        share_marker = html.find('<!-- ==================== MODAL 2:')
        if auth_start != -1 and share_marker != -1:
            html = html[:auth_start] + NEW_AUTH_AND_CLASS_MODALS.strip() + "\n\n  " + html[share_marker:]

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✔ Đã cập nhật giao diện Auth & Lớp học OLM: {html_file}")

    print("\n--- CẬP NHẬT LẠI CƠ SỞ DỮ LIỆU THẬT (vcode_edu.db) ---")
    subprocess.run([sys.executable, "-m", "backend.database.init_db"], check=True)
    print("\n🎉 NÂNG CẤP HOÀN TẤT 100%! Hãy khởi động lại Backend cổng 8000 và bấm Ctrl + Shift + R trên trình duyệt!")

if __name__ == "__main__":
    apply_upgrade()