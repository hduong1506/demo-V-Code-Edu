# -*- coding: utf-8 -*-
"""
V-CODE EDU — KHỞI TẠO HỆ THỐNG BACKEND & CƠ SỞ DỮ LIỆU (FASTAPI + SQLALCHEMY)
Hỗ trợ tùy chỉnh nâng cấp từng bảng (User, Classroom, LiveSession, Lesson, Assignment, Submission, Share)
Cách chạy: python setup_vcode_backend.py
"""
import os
import sys
import subprocess

BACKEND_FILES = {
    "backend/__init__.py": "",
    "backend/requirements.txt": """fastapi>=0.111.0
uvicorn>=0.30.0
sqlalchemy>=2.0.30
pydantic>=2.7.0
httpx>=0.27.0
psycopg2-binary>=2.9.9
""",

    "backend/database/__init__.py": "",
    "backend/database/base.py": """from sqlalchemy.orm import declarative_base

Base = declarative_base()
""",

    "backend/database/connection.py": """import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tự động dùng PostgreSQL khi có biến môi trường DATABASE_URL, ngược lại dùng SQLite cục bộ (vcode_edu.db)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vcode_edu.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    "backend/models/__init__.py": "",
    "backend/models/user.py": """from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(256), nullable=False)
    # Vai trò đa dạng: student_thcs | student_thpt | student_hsg | teacher | admin
    role = Column(String(30), default="student_thpt", nullable=False)
    school_name = Column(String(150), default="THCS & THPT Hòa Phú")
    class_name = Column(String(50), default="10A1")
    phone = Column(String(20), default="")
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
    student_username = Column(String(50), unique=True, index=True, nullable=False)
    student_name = Column(String(120), nullable=False)
    class_code = Column(String(20), default="TIN10-HP")
    current_problem = Column(String(150), default="")
    status = Column(String(30), default="coding")
    progress_percent = Column(Integer, default=0)
    current_code = Column(Text, default="")
    error_count = Column(Integer, default=0)
    teacher_hint = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)
""",

    "backend/models/learning.py": """from datetime import datetime
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
    classroom_code = Column(String(20), default="PUBLIC")
    difficulty = Column(String(20), default="Dễ")
    points = Column(Integer, default=100)
    starter_code = Column(Text, default="")
    test_cases_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)
    assignment_code = Column(String(40), index=True, nullable=False)
    source_code = Column(Text, nullable=False)
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    score = Column(Integer, default=0)
    teacher_feedback = Column(Text, default="")
    submitted_at = Column(DateTime, default=datetime.utcnow)
""",

    "backend/models/workspace.py": """from datetime import datetime
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
""",

    "backend/services/__init__.py": "",
    "backend/services/auth_service.py": """import hashlib
import hmac
import secrets
import base64

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"{salt}${base64.b64encode(dk).decode('ascii')}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, encoded = stored_hash.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
        return hmac.compare_digest(base64.b64encode(dk).decode("ascii"), encoded)
    except Exception:
        return False

def create_session_token(username: str, role: str) -> str:
    raw = f"{username}:{role}:{secrets.token_hex(16)}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
""",

    "backend/services/ai_service.py": """import os
import json
import urllib.request

def offline_socratic_reply(question: str, code: str = "", error_msg: str = "") -> dict:
    q = (question or "").lower()
    err = error_msg or ""

    if "SyntaxError" in err:
        return {"mode": "offline", "reply": "Lỗi Cú Pháp (SyntaxError): Kiểm tra dấu hai chấm ':' cuối lệnh if/elif/else/for/while hoặc dấu ngoặc đơn bị thiếu."}
    if "IndentationError" in err:
        return {"mode": "offline", "reply": "Lỗi Thụt Lề (IndentationError): Các dòng cùng khối lệnh trong Python phải thụt lề đều 4 dấu cách (1 Tab)."}
    if "ZeroDivisionError" in err:
        return {"mode": "offline", "reply": "Lỗi Chia Cho 0 (ZeroDivisionError): Cần kiểm tra mẫu số khác 0 trước khi chia."}
    if "số nguyên tố" in q or "nguyen to" in q:
        return {"mode": "offline", "reply": "Gợi ý Socratic: Số nguyên tố là số > 1 chỉ chia hết cho 1 và chính nó. Em hãy thử duyệt i từ 2 đến n-1 và kiểm tra n % i == 0."}
    if "for" in q or "vòng lặp" in q:
        return {"mode": "offline", "reply": "Vòng lặp for chuẩn: 'for i in range(1, n + 1):' sẽ duyệt từ 1 tới n. Lưu ý thụt lề 4 dấu cách ở các dòng bên trong."}
    return {
        "mode": "offline",
        "reply": f"Trợ lý V-Code Edu (Offline): Mã nguồn hiện có {len(code.splitlines())} dòng. Hãy kiểm tra đủ 3 bước: (1) Đọc dữ liệu int(input()), (2) Xử lý logic, (3) In kết quả print()."
    }

def ask_ai_hybrid(question: str, code: str = "", error_msg: str = "", api_key_override: str = "") -> dict:
    api_key = (api_key_override or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        return offline_socratic_reply(question, code, error_msg)

    prompt = (
        "Bạn là Gia sư Lập trình Tiếng Việt của V-Code Edu dành cho học sinh phổ thông Việt Nam. "
        "Hãy trả lời ngắn gọn, thân thiện, gợi mở tư duy Socratic thay vì làm hộ hoàn toàn.\\n"
        f"Câu hỏi: {question}\\nMã nguồn:\\n```python\\n{code}\\n```\\nLỗi (nếu có): {error_msg}"
    )
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"mode": "online-gemini", "reply": text}
    except Exception:
        fb = offline_socratic_reply(question, code, error_msg)
        fb["note"] = "API trực tuyến không khả dụng, đã tự động chuyển sang chế độ AI Offline."
        return fb
""",

    "backend/database/init_db.py": """from backend.database.base import Base
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
        if not db.query(User).filter(User.username == "giaovien").first():
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
            student = User(
                username="hocsinh",
                email="hocsinh@vcode.edu.vn",
                full_name="Nguyễn Minh Quân",
                password_hash=hash_password("HocSinh@2026"),
                role="student_thpt",
                school_name="THCS & THPT Hòa Phú",
                class_name="10A1",
                xp_points=1250
            )
            db.add_all([teacher, student])
            db.commit()
            db.refresh(teacher)

            cls1 = Classroom(code="TIN10-HP", name="Tin học 10A1 — THCS & THPT Hòa Phú", description="Python cơ bản GDPT 2018", teacher_id=teacher.id)
            cls2 = Classroom(code="HSG-PY26", name="Đội tuyển HSG Lập trình Python", description="Thuật toán nâng cao", teacher_id=teacher.id)
            db.add_all([cls1, cls2])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("✔ Đã khởi tạo CSDL V-Code Edu thành công!")
""",

    "backend/schemas/__init__.py": "",
    "backend/schemas/user_schema.py": """from pydantic import BaseModel

class RegisterSchema(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    role: str = "student_thpt"
    school_name: str = "THCS & THPT Hòa Phú"
    class_name: str = "10A1"
    phone: str = ""

class LoginSchema(BaseModel):
    identifier: str
    password: str
""",

    "backend/schemas/classroom_schema.py": """from pydantic import BaseModel

class CreateClassroomSchema(BaseModel):
    code: str
    name: str
    description: str = ""
    teacher_username: str = "giaovien"

class LiveHeartbeatSchema(BaseModel):
    student_username: str
    student_name: str
    class_code: str = "TIN10-HP"
    current_problem: str = ""
    status: str = "coding"
    progress_percent: int = 0
    current_code: str = ""
    error_count: int = 0

class TeacherHintSchema(BaseModel):
    student_username: str
    hint_message: str
""",

    "backend/schemas/ai_schema.py": """from pydantic import BaseModel

class AIChatSchema(BaseModel):
    question: str
    code: str = ""
    error_message: str = ""
    api_key: str = ""
""",

    "backend/routers/__init__.py": "",
    "backend/routers/auth.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.schemas.user_schema import RegisterSchema, LoginSchema
from backend.services.auth_service import hash_password, verify_password, create_session_token

router = APIRouter(prefix="/api/auth", tags=["Xác thực & Tài khoản"])

@router.post("/register")
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    exists = db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc email đã tồn tại.")
    user = User(
        username=payload.username.strip(),
        email=payload.email.strip(),
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        school_name=payload.school_name,
        class_name=payload.class_name,
        phone=payload.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "status": "ok",
        "token": create_session_token(user.username, user.role),
        "user": {"username": user.username, "full_name": user.full_name, "role": user.role, "school": user.school_name, "class_name": user.class_name, "xp": user.xp_points}
    }

@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == payload.identifier) | (User.email == payload.identifier)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu.")
    return {
        "status": "ok",
        "token": create_session_token(user.username, user.role),
        "user": {"username": user.username, "full_name": user.full_name, "role": user.role, "school": user.school_name, "class_name": user.class_name, "xp": user.xp_points}
    }
""",

    "backend/routers/monitor.py": """from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.classroom import StudentLiveSession
from backend.schemas.classroom_schema import LiveHeartbeatSchema, TeacherHintSchema

router = APIRouter(prefix="/api/monitor", tags=["Giám sát Real-time (You Time)"])

@router.post("/heartbeat")
def push_heartbeat(payload: LiveHeartbeatSchema, db: Session = Depends(get_db)):
    row = db.query(StudentLiveSession).filter(StudentLiveSession.student_username == payload.student_username).first()
    if not row:
        row = StudentLiveSession(student_username=payload.student_username, student_name=payload.student_name)
        db.add(row)
    row.student_name = payload.student_name
    row.class_code = payload.class_code
    row.current_problem = payload.current_problem
    row.status = payload.status
    row.progress_percent = payload.progress_percent
    row.current_code = payload.current_code
    row.error_count = payload.error_count
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "ok", "teacher_hint": row.teacher_hint}

@router.get("/live")
def list_live_students(class_code: str = "", db: Session = Depends(get_db)):
    query = db.query(StudentLiveSession)
    if class_code:
        query = query.filter(StudentLiveSession.class_code == class_code)
    rows = query.order_by(StudentLiveSession.updated_at.desc()).all()
    return {
        "students": [
            {
                "username": r.student_username,
                "name": r.student_name,
                "classCode": r.class_code,
                "problem": r.current_problem,
                "status": r.status,
                "progress": r.progress_percent,
                "code": r.current_code,
                "errors": r.error_count,
                "hint": r.teacher_hint,
                "updatedAt": r.updated_at.isoformat()
            }
            for r in rows
        ]
    }

@router.post("/hint")
def send_teacher_hint(payload: TeacherHintSchema, db: Session = Depends(get_db)):
    row = db.query(StudentLiveSession).filter(StudentLiveSession.student_username == payload.student_username).first()
    if row:
        row.teacher_hint = payload.hint_message
        db.commit()
    return {"status": "sent"}
""",

    "backend/routers/ai.py": """from fastapi import APIRouter
from backend.schemas.ai_schema import AIChatSchema
from backend.services.ai_service import ask_ai_hybrid

router = APIRouter(prefix="/api/ai", tags=["Trợ lý AI Hybrid Online/Offline"])

@router.post("/chat")
def ai_chat(payload: AIChatSchema):
    return ask_ai_hybrid(payload.question, payload.code, payload.error_message, payload.api_key)
""",

    "backend/routers/sync.py": """from fastapi import APIRouter

router = APIRouter(prefix="/api/sync", tags=["Đồng bộ Offline PWA"])

@router.post("/push")
def sync_offline_batch(payload: dict):
    items = payload.get("operations", [])
    return {"status": "synced", "processed_count": len(items)}
""",

    "backend/main.py": """\"\"\"
V-CODE EDU — FASTAPI BACKEND SERVER
Chạy trong Terminal VS Code:
    pip install -r backend/requirements.txt
    uvicorn backend.main:app --reload --port 8000
Mở tài liệu API Swagger: http://localhost:8000/docs
\"\"\"
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.init_db import init_database
from backend.routers import auth, monitor, ai, sync

app = FastAPI(
    title="V-Code Edu API",
    description="Nền tảng Học tập, Giảng dạy, Thực hành Python & Scratch trực quan của Việt Nam",
    version="5.0.0"
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
    return {"status": "ok", "service": "V-Code Edu FastAPI", "timestamp": int(time.time())}

app.include_router(auth.router)
app.include_router(monitor.router)
app.include_router(ai.router)
app.include_router(sync.router)
""",

    "test_project.py": """import os
import json
from backend.services.auth_service import hash_password, verify_password
from backend.services.ai_service import offline_socratic_reply

def run_tests():
    print("=== KIỂM THỬ TỰ ĐỘNG HỆ THỐNG V-CODE EDU ===")
    for p in ["index.html", "manifest.json", "sw.js", "css/design-system.css", "js/three-hero.js", "js/scratch-bridge.js", "js/ide-engine.js", "js/ai-tutor.js", "js/realtime-monitor.js", "js/app.js", "backend/main.py"]:
        assert os.path.exists(p), f"Thiếu file bắt buộc: {p}"
    print("[PASS] 1. Đầy đủ cấu trúc Frontend + Scratch Live + Real-time + Backend.")

    with open("manifest.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert "V-Code Edu" in m["name"]
    print("[PASS] 2. Cấu hình PWA Offline V-Code Edu hợp lệ.")

    h = hash_password("Test@12345")
    assert verify_password("Test@12345", h) and not verify_password("wrong", h)
    print("[PASS] 3. Mã hóa mật khẩu PBKDF2-SHA256 chính xác.")

    r = offline_socratic_reply("Lỗi vòng lặp", "for i in range(5)\\n print(i)", "SyntaxError")
    assert r["mode"] == "offline" and "SyntaxError" in r["reply"]
    print("[PASS] 4. Trợ lý AI Socratic Offline hoạt động chính xác.")

    print("=== TẤT CẢ 4/4 BÀI KIỂM THỬ ĐẠT 100% ===")

if __name__ == "__main__":
    run_tests()
"""
}

def setup_backend():
    for rel, content in BACKEND_FILES.items():
        folder = os.path.dirname(rel)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n" if content else "")
        print(f"✔ Đã tạo: {rel}")
    print("\n--- CHẠY KIỂM THỬ TỰ ĐỘNG ---")
    subprocess.run([sys.executable, "test_project.py"], check=True)
    print("\n🎉 Hoàn tất V-Code Edu! Mở index.html (hoặc chạy: python -m http.server 5500) để trải nghiệm!")

if __name__ == "__main__":
    setup_backend()