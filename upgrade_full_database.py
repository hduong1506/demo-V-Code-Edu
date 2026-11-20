# -*- coding: utf-8 -*-
"""
V-CODE EDU — HOÀN THIỆN TOÀN BỘ DATABASE & API KẾT NỐI THẬT (SQLITE / POSTGRESQL + FASTAPI)
Chạy trong Terminal VS Code tại thư mục V-Code Edu:
    python upgrade_full_database.py
"""
import os
import sys
import subprocess

FILES = {
    "backend/database/base.py": """from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
""",

    "backend/database/connection.py": """import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Định vị file vcode_edu.db cố định tại thư mục gốc dự án V-Code Edu
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'vcode_edu.db').as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL).strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False, future=True)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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

def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Nạp tài khoản mẫu (Giáo viên, Học sinh, Quản trị viên)
        teacher = db.query(User).filter(User.username == "giaovien").first()
        if not teacher:
            teacher = User(
                username="giaovien",
                email="giaovien@vcode.edu.vn",
                full_name="Thầy Nguyễn Phi Hùng",
                password_hash=hash_password("VCodeEdu@2026"),
                role="teacher",
                school_name="THCS & THPT Hòa Phú",
                class_name="Tổ Tin học",
                xp_points=2500
            )
            student1 = User(
                username="hocsinh",
                email="hocsinh@vcode.edu.vn",
                full_name="Nguyễn Minh Quân",
                password_hash=hash_password("HocSinh@2026"),
                role="student_thpt",
                school_name="THCS & THPT Hòa Phú",
                class_name="10A1",
                xp_points=1450
            )
            student2 = User(
                username="thuha_10a1",
                email="thuha@vcode.edu.vn",
                full_name="Lê Thu Hà",
                password_hash=hash_password("HocSinh@2026"),
                role="student_thpt",
                school_name="THCS & THPT Hòa Phú",
                class_name="10A1",
                xp_points=1320
            )
            admin = User(
                username="admin",
                email="admin@vcode.edu.vn",
                full_name="Quản trị viên V-Code Edu",
                password_hash=hash_password("Admin@2026"),
                role="admin",
                school_name="THCS & THPT Hòa Phú",
                class_name="Ban Giám Hiệu",
                xp_points=9999
            )
            db.add_all([teacher, student1, student2, admin])
            db.commit()
            db.refresh(teacher)
            db.refresh(student1)
            db.refresh(student2)

            # 2. Nạp lớp học & gán thành viên vào lớp
            cls1 = Classroom(code="TIN10-HP", name="Tin học 10A1 — THCS & THPT Hòa Phú", description="Python cơ bản GDPT 2018", teacher_id=teacher.id)
            cls2 = Classroom(code="HSG-PY26", name="Đội tuyển HSG Lập trình Python", description="Thuật toán nâng cao", teacher_id=teacher.id)
            db.add_all([cls1, cls2])
            db.commit()
            db.refresh(cls1)

            db.add_all([
                ClassroomMember(classroom_id=cls1.id, student_id=student1.id),
                ClassroomMember(classroom_id=cls1.id, student_id=student2.id)
            ])
            db.commit()

        # 3. Nạp lộ trình bài học Python chuẩn GDPT 2018
        if db.query(Lesson).count() == 0:
            lessons = [
                Lesson(
                    slug="py-01", order_index=1, title="Bài 1: Biến, Kiểu dữ liệu & Nhập xuất (input / print)",
                    summary="Làm quen cách khai báo biến, đọc số nguyên bằng int(input()) và xuất kết quả.",
                    content_html="Dùng hàm int(input()) để nhập số nguyên và print() để hiển thị kết quả.",
                    starter_code="n = int(input())\\nchu_vi = n * 4\\nprint(chu_vi)", difficulty="Cơ bản"
                ),
                Lesson(
                    slug="py-02", order_index=2, title="Bài 2: Cấu trúc Rẽ nhánh (if / elif / else)",
                    summary="Xây dựng chương trình ra quyết định theo điều kiện và phân loại học lực.",
                    content_html="Câu lệnh if kết thúc bằng dấu ':' và khối lệnh bên trong thụt lề 4 khoảng trắng.",
                    starter_code="diem = int(input())\\nif diem >= 8:\\n    print('Gioi')\\nelif diem >= 6:\\n    print('Kha')\\nelse:\\n    print('Can co gang')", difficulty="Cơ bản"
                ),
                Lesson(
                    slug="py-03", order_index=3, title="Bài 3: Vòng lặp for & Tính tổng số chẵn",
                    summary="Dùng vòng lặp for kết hợp range() để duyệt dãy số và cộng dồn có điều kiện.",
                    content_html="Hàm range(1, n + 1) tạo dãy số liên tiếp từ 1 đến đúng n.",
                    starter_code="n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong = tong + i\\nprint(tong)", difficulty="Trung bình"
                ),
                Lesson(
                    slug="py-04", order_index=4, title="Bài 4: Thuật toán Giai thừa N! & Đấu trường",
                    summary="Tính tích N! bằng vòng lặp tích lũy và luyện tốc độ giải thuật.",
                    content_html="Biến tích lũy cho phép nhân phải khởi tạo bằng 1.",
                    starter_code="n = int(input())\\ngt = 1\\nfor i in range(1, n + 1):\\n    gt = gt * i\\nprint(gt)", difficulty="Nâng cao"
                )
            ]
            db.add_all(lessons)
            db.commit()

        # 4. Nạp bài tập & bộ Test Case chấm tự động
        if db.query(Assignment).count() == 0:
            assignments = [
                Assignment(
                    code="py-01", title="Bài 1: Tính chu vi hình vuông", description="Nhập cạnh N, in ra chu vi.",
                    classroom_code="TIN10-HP", difficulty="Dễ", points=100,
                    starter_code="n = int(input())\\nprint(n * 4)",
                    test_cases_json=json.dumps([{"input": "5", "expected": "20"}, {"input": "12", "expected": "48"}])
                ),
                Assignment(
                    code="py-03", title="Bài 3: Tổng các số chẵn từ 1 đến N", description="Nhập N, tính tổng các số chẵn từ 1 đến N.",
                    classroom_code="TIN10-HP", difficulty="Trung bình", points=150,
                    starter_code="n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong += i\\nprint(tong)",
                    test_cases_json=json.dumps([{"input": "6", "expected": "12"}, {"input": "10", "expected": "30"}])
                )
            ]
            db.add_all(assignments)
            db.commit()

        # 5. Nạp dữ liệu giám sát Real-time ban đầu cho Giáo viên
        if db.query(StudentLiveSession).count() == 0:
            db.add_all([
                StudentLiveSession(
                    student_username="hocsinh", student_name="Nguyễn Minh Quân", class_code="TIN10-HP",
                    current_problem="Bài 3: Vòng lặp for & Tổng số chẵn", status="coding", progress_percent=75,
                    current_code="n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong += i\\nprint(tong)", error_count=0
                ),
                StudentLiveSession(
                    student_username="thuha_10a1", student_name="Lê Thu Hà", class_code="TIN10-HP",
                    current_problem="Bài 2: Cấu trúc Rẽ nhánh if/elif", status="error", progress_percent=45,
                    current_code="diem = int(input())\\nif diem >= 8\\n    print('Gioi')", error_count=2
                )
            ])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("✔ Đã khởi tạo & nạp đầy đủ dữ liệu vào CSDL vcode_edu.db thành công!")
""",

    "backend/routers/classrooms.py": """import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.classroom import Classroom, ClassroomMember

router = APIRouter(prefix="/api/classes", tags=["Quản lý Lớp học"])

@router.get("/")
def get_all_classes(db: Session = Depends(get_db)):
    classes = db.query(Classroom).all()
    result = []
    for c in classes:
        teacher = db.query(User).filter(User.id == c.teacher_id).first()
        member_count = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == c.id).count()
        result.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "description": c.description,
            "teacher": teacher.full_name if teacher else "Giáo viên V-Code",
            "students": member_count
        })
    return {"classes": result}

@router.post("/create")
def create_classroom(payload: dict, db: Session = Depends(get_db)):
    teacher_username = payload.get("teacher_username", "giaovien")
    teacher = db.query(User).filter(User.username == teacher_username).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản giáo viên")
    code = payload.get("code") or f"VC-{secrets.token_hex(2).upper()}"
    cls = Classroom(
        code=code.upper(),
        name=payload.get("name", "Lớp Tin học mới"),
        description=payload.get("description", ""),
        teacher_id=teacher.id
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return {"status": "ok", "classroom": {"id": cls.id, "code": cls.code, "name": cls.name}}

@router.post("/join")
def join_classroom(payload: dict, db: Session = Depends(get_db)):
    code = (payload.get("code") or "").strip().upper()
    username = (payload.get("username") or "").strip()
    cls = db.query(Classroom).filter(Classroom.code == code).first()
    user = db.query(User).filter(User.username == username).first()
    if not cls or not user:
        raise HTTPException(status_code=404, detail="Mã lớp hoặc tài khoản không tồn tại")
    exists = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == cls.id, ClassroomMember.student_id == user.id).first()
    if not exists:
        db.add(ClassroomMember(classroom_id=cls.id, student_id=user.id))
        db.commit()
    return {"status": "joined", "class_name": cls.name}
""",

    "backend/routers/assessment.py": """import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.assessment import Assignment, Submission

router = APIRouter(prefix="/api/assessment", tags=["Bài tập, Nộp bài & Xếp hạng"])

@router.get("/assignments")
def list_assignments(db: Session = Depends(get_db)):
    rows = db.query(Assignment).all()
    return {
        "assignments": [
            {
                "code": a.code,
                "title": a.title,
                "description": a.description,
                "classroom_code": a.classroom_code,
                "difficulty": a.difficulty,
                "points": a.points,
                "starter_code": a.starter_code,
                "test_cases": json.loads(a.test_cases_json or "[]")
            }
            for a in rows
        ]
    }

@router.post("/submit")
def submit_solution(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username", "hocsinh")
    sub = Submission(
        username=username,
        assignment_code=payload.get("assignment_code", "py-01"),
        source_code=payload.get("source_code", ""),
        passed_tests=int(payload.get("passed_tests", 0)),
        total_tests=int(payload.get("total_tests", 0)),
        score=int(payload.get("score", 0))
    )
    db.add(sub)
    user = db.query(User).filter(User.username == username).first()
    if user and sub.score == 100:
        user.xp_points += 50
    db.commit()
    return {"status": "saved", "score": sub.score, "new_xp": user.xp_points if user else 0}

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role != "teacher").order_by(User.xp_points.desc()).limit(20).all()
    return {
        "leaderboard": [
            {"rank": idx + 1, "name": u.full_name, "classCode": u.class_name, "xp": u.xp_points}
            for idx, u in enumerate(users)
        ]
    }
""",

    "backend/main.py": """\"\"\"
V-CODE EDU — FASTAPI BACKEND SERVER (FULL DATABASE INTEGRATION)
Chạy trong Terminal VS Code:
    uvicorn backend.main:app --reload --port 8000
\"\"\"
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.init_db import init_database
from backend.routers import auth, classrooms, assessment, monitor, ai, sync

app = FastAPI(
    title="V-Code Edu API",
    description="Hệ thống API & Cơ sở dữ liệu cho nền tảng Học lập trình Python & Scratch Live Việt Nam",
    version="5.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_database()

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "V-Code Edu FastAPI + Database", "timestamp": int(time.time())}

app.include_router(auth.router)
app.include_router(classrooms.router)
app.include_router(assessment.router)
app.include_router(monitor.router)
app.include_router(ai.router)
app.include_router(sync.router)
"""
}

def main():
    for rel, content in FILES.items():
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✔ Đã cập nhật: {rel}")

    print("\n--- KHỞI TẠO FILE CƠ SỞ DỮ LIỆU THẬT (vcode_edu.db) ---")
    subprocess.run([sys.executable, "-m", "backend.database.init_db"], check=True)

if __name__ == "__main__":
    main()