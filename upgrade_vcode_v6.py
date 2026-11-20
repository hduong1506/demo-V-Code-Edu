# -*- coding: utf-8 -*-
"""
V-CODE EDU v6.0 — BẢN NÂNG CẤP HOÀN THIỆN TOÀN DIỆN
Chạy trong Terminal VS Code tại thư mục V-Code Edu:
    python upgrade_vcode_v6.py
"""
import os
import sys
import subprocess

# ==============================================================================
# 1. BACKEND UPDATES (KHÓA VAI TRÒ 1 LẦN, ĐỔI MẬT KHẨU, AVATAR, REAL-TIME THẬT)
# ==============================================================================
BACKEND_FILES = {
    "backend/schemas/user_schema.py": """from pydantic import BaseModel

class RegisterSchema(BaseModel):
    full_name: str
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

class SocialAuthSchema(BaseModel):
    provider: str
    email: str
    full_name: str
    avatar_url: str = ""

class SetRoleSchema(BaseModel):
    email: str
    role: str
    school_name: str = "THCS & THPT Hòa Phú"
    class_name: str = ""

class UpdateProfileSchema(BaseModel):
    email: str
    full_name: str
    school_name: str = ""
    class_name: str = ""
    avatar_url: str = ""

class ChangePasswordSchema(BaseModel):
    email: str
    old_password: str
    new_password: str
""",

    "backend/routers/auth.py": """import re
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.schemas.user_schema import (
    RegisterSchema, LoginSchema, SocialAuthSchema,
    SetRoleSchema, UpdateProfileSchema, ChangePasswordSchema
)
from backend.services.auth_service import hash_password, verify_password, create_session_token

router = APIRouter(prefix="/api/auth", tags=["Xác thực & Quản lý Tài khoản"])

def serialize_user(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "auth_provider": u.auth_provider,
        "avatar_url": u.avatar_url or "",
        "school_name": u.school_name or "",
        "class_name": u.class_name or "",
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
            avatar_url=payload.avatar_url or "",
            xp_points=150
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif payload.avatar_url and not user.avatar_url:
        user.avatar_url = payload.avatar_url
        db.commit()
        db.refresh(user)
    return {"status": "ok", "token": create_session_token(user.username, user.role), "user": serialize_user(user)}

@router.post("/set-role")
def set_classroom_role(payload: SetRoleSchema, db: Session = Depends(get_db)):
    ident = payload.email.strip().lower()
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    if payload.role not in ("teacher", "student"):
        raise HTTPException(status_code=400, detail="Vai trò chỉ nhận 'teacher' hoặc 'student'.")
    if user.role in ("teacher", "student") and user.role != payload.role:
        raise HTTPException(status_code=403, detail="Vai trò tài khoản chỉ được chọn 1 lần duy nhất và đã bị khóa cố định.")
    user.role = payload.role
    if payload.school_name.strip():
        user.school_name = payload.school_name.strip()
    if payload.class_name.strip():
        user.class_name = payload.class_name.strip()
    db.commit()
    db.refresh(user)
    return {"status": "ok", "user": serialize_user(user)}

@router.post("/update-profile")
def update_profile(payload: UpdateProfileSchema, db: Session = Depends(get_db)):
    ident = payload.email.strip().lower()
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    if payload.full_name.strip():
        user.full_name = payload.full_name.strip()
    user.school_name = payload.school_name.strip()
    user.class_name = payload.class_name.strip()
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(user)
    return {"status": "ok", "user": serialize_user(user)}

@router.post("/change-password")
def change_password(payload: ChangePasswordSchema, db: Session = Depends(get_db)):
    ident = payload.email.strip().lower()
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự.")
    if user.auth_provider == "local" and not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác.")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"status": "ok", "message": "Đã cập nhật mật khẩu an toàn thành công!"}
""",

    "backend/routers/classrooms.py": """import json
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.classroom import Classroom, ClassroomMember, StudentLiveSession
from backend.models.assessment import Assignment, Submission

router = APIRouter(prefix="/api/classes", tags=["Quản lý Lớp học (Dữ liệu thật)"])

def format_classroom(c: Classroom, db: Session) -> dict:
    teacher = db.query(User).filter(User.id == c.teacher_id).first()
    student_count = db.query(ClassroomMember).filter(ClassroomMember.classroom_id == c.id).count()
    assignment_count = db.query(Assignment).filter(Assignment.classroom_code == c.code).count()
    return {
        "id": c.id, "code": c.code, "name": c.name, "grade_subject": c.grade_subject,
        "description": c.description,
        "teacher_name": teacher.full_name if teacher else "Giáo viên V-Code",
        "students_count": student_count, "assignments_count": assignment_count
    }

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
    ident = (payload.get("teacher_email") or payload.get("teacher_username") or "").strip().lower()
    teacher = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not teacher or teacher.role != "teacher":
        raise HTTPException(status_code=403, detail="Chỉ tài khoản đã đăng ký vai trò Giáo viên mới được tạo lớp.")
    custom_code = (payload.get("code") or "").strip().upper()
    code = custom_code if custom_code else f"VC{secrets.token_hex(2).upper()}"
    while db.query(Classroom).filter(Classroom.code == code).first():
        code = f"VC{secrets.token_hex(2).upper()}"
    cls = Classroom(
        code=code, name=(payload.get("name") or "Lớp Tin học mới").strip(),
        grade_subject=(payload.get("grade_subject") or "Tin học THPT • Python").strip(),
        description=(payload.get("description") or "").strip(), teacher_id=teacher.id
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
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lớp học với ID mã lớp '{code}'.")
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
    submissions = db.query(Submission).filter(Submission.classroom_code == c_code).order_by(Submission.submitted_at.desc()).all()
    live_rows = db.query(StudentLiveSession).filter(StudentLiveSession.class_code == c_code).all()
    live_map = {r.student_username: r for r in live_rows}

    real_roster = []
    for st in students:
        st_subs = [s for s in submissions if s.username == st.username]
        live = live_map.get(st.username)
        if st_subs:
            latest = st_subs[0]
            status, problem, progress, score, code_snap, updated = (
                "completed", latest.assignment_code, 100, latest.score, latest.source_code, latest.submitted_at.strftime("%H:%M %d/%m")
            )
        elif live and live.status in ("coding", "error"):
            status, problem, progress, score, code_snap, updated = (
                live.status, live.current_problem or "Đang làm bài tập", live.progress_percent, None, live.current_code, "Đang trực tuyến"
            )
        else:
            status, problem, progress, score, code_snap, updated = (
                "not_started", "Chưa mở bài tập", 0, None, "", "Chưa làm"
            )
        real_roster.append({
            "username": st.username, "full_name": st.full_name, "email": st.email, "xp": st.xp_points,
            "status": status, "problem": problem, "progress": progress, "score": score, "code": code_snap, "updated": updated
        })

    return {
        "classroom": format_classroom(cls, db),
        "roster": real_roster,
        "assignments": [
            {
                "code": a.code, "title": a.title, "description": a.description,
                "difficulty": a.difficulty, "points": a.points, "due_date": a.due_date,
                "starter_code": a.starter_code, "test_cases": json.loads(a.test_cases_json or "[]")
            }
            for a in assignments
        ],
        "submissions": [
            {
                "username": sub.username, "student_name": sub.student_name or sub.username,
                "assignment_code": sub.assignment_code, "score": sub.score,
                "passed_tests": sub.passed_tests, "total_tests": sub.total_tests,
                "submitted_at": sub.submitted_at.strftime("%H:%M %d/%m/%Y")
            }
            for sub in submissions[:50]
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
                username="giaovien", email="giaovien@vcode.edu.vn", full_name="Thầy Nguyễn Phi Hùng",
                password_hash=hash_password("123456"), role="teacher", auth_provider="local",
                school_name="THCS & THPT Hòa Phú", class_name="Tổ Tin học", xp_points=2500
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            cls1 = Classroom(
                code="TIN10HP", name="Tin học 10A1 — THCS & THPT Hòa Phú",
                grade_subject="Tin học 10 • Python GDPT 2018",
                description="Lớp học thực hành Python cơ bản và cầu nối Scratch Live.", teacher_id=teacher.id
            )
            db.add(cls1)
            db.commit()

        if db.query(Assignment).count() == 0:
            db.add(Assignment(
                code="BT-CHAN01", title="Bài tập 1: Tổng các số chẵn từ 1 đến N",
                description="Nhập số nguyên dương N. Tính và in ra tổng các số chẵn từ 1 đến N.",
                classroom_code="TIN10HP", difficulty="Cơ bản", points=100, due_date="25/11/2026",
                starter_code="# Học sinh tự viết mã nguồn giải bài toán bên dưới\\n",
                test_cases_json=json.dumps([{"input": "6", "expected": "12"}, {"input": "10", "expected": "30"}]),
                created_by="giaovien"
            ))
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_database(reset_schema=True)
    print("✔ Đã làm sạch học sinh mô phỏng & khởi tạo CSDL thật vcode_edu.db!")
"""
}

# ==============================================================================
# 2. FRONTEND JS FILES (3D BURST SCROLL, FIREBASE OAUTH, REAL-TIME THẬT, CHALLENGES)
# ==============================================================================
FRONTEND_JS_FILES = {
    "js/firebase-auth.js": """// V-CODE EDU — OAUTH THẬT (GOOGLE / FACEBOOK / GITHUB) QUA FIREBASE AUTHENTICATION
window.VCODE_FIREBASE_CONFIG = JSON.parse(localStorage.getItem('vcode_firebase_config') || 'null') || {
  apiKey: "",
  authDomain: "",
  projectId: ""
};

window.VCodeOAuth = {
  isConfigured() {
    return Boolean(window.VCODE_FIREBASE_CONFIG && window.VCODE_FIREBASE_CONFIG.apiKey && window.VCODE_FIREBASE_CONFIG.authDomain);
  },

  async signInWithProvider(providerName) {
    if (!this.isConfigured() || typeof firebase === 'undefined') {
      return { configured: false };
    }
    if (!firebase.apps.length) {
      firebase.initializeApp(window.VCODE_FIREBASE_CONFIG);
    }
    let provider;
    if (providerName === 'google') provider = new firebase.auth.GoogleAuthProvider();
    else if (providerName === 'facebook') provider = new firebase.auth.FacebookAuthProvider();
    else provider = new firebase.auth.GithubAuthProvider();

    const result = await firebase.auth().signInWithPopup(provider);
    const u = result.user;
    return {
      configured: true,
      email: u.email || `${u.uid}@${providerName}.vcode.edu`,
      full_name: u.displayName || 'Thành viên V-Code Edu',
      avatar_url: u.photoURL || ''
    };
  }
};
""",

    "js/realtime-monitor.js": """// V-CODE EDU v6 — GIÁM SÁT REAL-TIME 100% DỮ LIỆU THẬT (KHÔNG CÒN HỌC SINH MÔ PHỎNG)
window.VCodeMonitor = {
  channel: typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('vcode_edu_realtime') : null,

  init(onLiveEvent, onTeacherHint) {
    if (this.channel) {
      this.channel.onmessage = (ev) => {
        const msg = ev.data || {};
        if (msg.type === 'STUDENT_HEARTBEAT' && onLiveEvent) onLiveEvent(msg.payload);
        if (msg.type === 'TEACHER_HINT' && onTeacherHint) onTeacherHint(msg.payload);
      };
    }
  },

  emitStudentActivity(user, problemTitle, code, status = 'coding', progress = 50, errors = 0) {
    if (!user || !user.username) return;
    const payload = {
      username: user.username, name: user.full_name, classCode: user.class_name || 'TIN10HP',
      problem: problemTitle, status, progress, errors, code
    };
    if (this.channel) this.channel.postMessage({ type: 'STUDENT_HEARTBEAT', payload });
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl.replace(/\\/$/, '');
      fetch(`${url}/api/monitor/heartbeat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_username: payload.username, student_name: payload.name,
          class_code: payload.classCode, current_problem: payload.problem,
          status: payload.status, progress_percent: payload.progress,
          current_code: payload.code, error_count: payload.errors
        })
      }).catch(() => {});
    }
  },

  sendHintToStudent(username, hintText) {
    if (this.channel) this.channel.postMessage({ type: 'TEACHER_HINT', payload: { username, hintText } });
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl.replace(/\\/$/, '');
      fetch(`${url}/api/monitor/hint`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_username: username, hint_message: hintText })
      }).catch(() => {});
    }
  }
};
""",

    "js/three-hero.js": """// V-CODE EDU v6 — SCROLL-DRIVEN 3D MORPHING + BURST/SHATTER ANIMATION ON SCROLL
(function initScroll3DEngine() {
  const canvas = document.getElementById('scroll-3d-canvas');
  const homeView = document.getElementById('view-home');
  if (!canvas || !homeView) return;

  const ctx = canvas.getContext('2d');
  let width = 0, height = 0, rawScroll = 0, smoothScroll = 0;
  let mouseX = 0, mouseY = 0, smoothMouseX = 0, smoothMouseY = 0;

  const COUNT = 200;
  const particles = [];
  for (let i = 0; i < COUNT; i++) {
    const t = i / COUNT;
    const phi = Math.acos(1 - 2 * t), theta = Math.PI * (1 + Math.sqrt(5)) * i;
    const r1 = i < 145 ? 185 : 270;
    const s1 = i < 145
      ? { x: r1 * Math.sin(phi) * Math.cos(theta), y: r1 * Math.sin(phi) * Math.sin(theta), z: r1 * Math.cos(phi) }
      : { x: r1 * Math.cos(t * Math.PI * 10), y: Math.sin(t * Math.PI * 10) * 45, z: r1 * Math.sin(t * Math.PI * 10) };
    const hAngle = t * Math.PI * 6 + (i % 2 === 0 ? 0 : Math.PI);
    const s2 = { x: Math.cos(hAngle) * 145, y: (t - 0.5) * 440, z: Math.sin(hAngle) * 145 };
    const cols = 16, row = Math.floor(i / cols), col = i % cols;
    const s3 = { x: (col - cols / 2) * 36, y: Math.sin(col * 0.55) * Math.cos(row * 0.55) * 65, z: (row - (COUNT / cols) / 2) * 36 };
    const u = (i % 32) / 32 * Math.PI * 2, v = Math.floor(i / 32) / 6.25 * Math.PI * 2;
    const s4 = { x: (190 + 62 * Math.cos(v)) * Math.cos(u), y: 62 * Math.sin(v) * 1.4, z: (190 + 62 * Math.cos(v)) * Math.sin(u) };

    particles.push({
      x: s1.x, y: s1.y, z: s1.z, shapes: [s1, s2, s3, s4],
      burst: { x: (Math.random() - 0.5) * 560, y: (Math.random() - 0.5) * 420, z: (Math.random() - 0.5) * 480 },
      color: i % 4 === 0 ? '#10B981' : (i % 4 === 1 ? '#3B82F6' : (i % 4 === 2 ? '#8B5CF6' : '#F59E0B')),
      size: (i % 3) + 2.1
    });
  }

  function resize() { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize);
  resize();
  window.addEventListener('mousemove', (e) => { mouseX = (e.clientX / window.innerWidth) - 0.5; mouseY = (e.clientY / window.innerHeight) - 0.5; });
  function lerp(a, b, t) { return a + (b - a) * t; }

  function updateScrollChoreography() {
    const maxScroll = Math.max(1, homeView.scrollHeight - window.innerHeight);
    rawScroll = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    smoothScroll += (rawScroll - smoothScroll) * 0.085;

    const fill = document.getElementById('scroll-3d-progress-fill');
    if (fill) fill.style.height = `${(smoothScroll * 100).toFixed(1)}%`;
    const activeIdx = Math.min(3, Math.floor(smoothScroll * 3.99));
    document.querySelectorAll('.scroll-dot-item').forEach((dot, idx) => dot.classList.toggle('active', idx === activeIdx));

    // Hiệu ứng vỡ/bung tách 3D cho các phân cảnh khi cuộn
    document.querySelectorAll('.scroll-chapter').forEach((sec) => {
      const rect = sec.getBoundingClientRect();
      const offset = (rect.top + rect.height / 2 - window.innerHeight / 2) / window.innerHeight;
      const dist = Math.min(1, Math.abs(offset));
      const copy = sec.querySelector('.chapter-copy, .hero-copy-block');
      const visual = sec.querySelector('.scroll-3d-stage');

      if (copy) {
        copy.style.transform = `translate3d(${(offset * -44).toFixed(1)}px, ${(offset * 18).toFixed(1)}px, 0) scale(${(1 - dist * 0.08).toFixed(3)})`;
        copy.style.opacity = `${Math.max(0.22, 1 - dist * 0.85).toFixed(2)}`;
      }
      if (visual) {
        const dir = visual.dataset.tiltDir === 'left' ? 1 : -1;
        visual.style.transform = `perspective(1350px) translate3d(${(offset * 48 * dir).toFixed(1)}px, ${(offset * 24).toFixed(1)}px, 0) rotateX(${(offset * 18).toFixed(2)}deg) rotateY(${(dir * (6 + dist * 16) + smoothMouseX * 10).toFixed(2)}deg) scale(${(1 - dist * 0.09).toFixed(3)})`;
        visual.style.opacity = `${Math.max(0.22, 1 - dist * 0.85).toFixed(2)}`;
      }
    });
  }

  let tick = 0;
  function renderLoop() {
    requestAnimationFrame(renderLoop);
    if (!homeView.classList.contains('active')) return;
    tick += 0.012;
    smoothMouseX += (mouseX - smoothMouseX) * 0.06;
    smoothMouseY += (mouseY - smoothMouseY) * 0.06;
    updateScrollChoreography();
    ctx.clearRect(0, 0, width, height);

    const scaled = smoothScroll * 3;
    const idxA = Math.min(2, Math.floor(scaled)), idxB = idxA + 1, blend = scaled - idxA;
    const easeBlend = blend * blend * (3 - 2 * blend);
    const burstFactor = Math.sin(blend * Math.PI);

    const anchors = [0.73, 0.27, 0.72, 0.50];
    const centerX = width * lerp(anchors[idxA], anchors[idxB], easeBlend), centerY = height * 0.52;
    const rotY = tick * 0.42 + smoothScroll * Math.PI * 2.4 + smoothMouseX * 0.9;
    const rotX = 0.25 + Math.sin(smoothScroll * Math.PI) * 0.45 + smoothMouseY * 0.6;
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY), cosX = Math.cos(rotX), sinX = Math.sin(rotX);

    const projected = [];
    for (let i = 0; i < COUNT; i++) {
      const p = particles[i], a = p.shapes[idxA], b = p.shapes[idxB];
      const tx = lerp(a.x, b.x, easeBlend) + p.burst.x * burstFactor * 0.75;
      const ty = lerp(a.y, b.y, easeBlend) + p.burst.y * burstFactor * 0.75 + Math.sin(tick * 2 + i * 0.2) * 5;
      const tz = lerp(a.z, b.z, easeBlend) + p.burst.z * burstFactor * 0.75;
      p.x += (tx - p.x) * 0.14; p.y += (ty - p.y) * 0.14; p.z += (tz - p.z) * 0.14;
      const x1 = p.x * cosY - p.z * sinY, z1 = p.z * cosY + p.x * sinY;
      const y2 = p.y * cosX - z1 * sinX, z2 = z1 * cosX + p.y * sinX;
      const scale = 720 / (720 + z2 + 360);
      projected.push({ sx: centerX + x1 * scale, sy: centerY + y2 * scale, z: z2, scale, color: p.color, size: p.size });
    }

    ctx.lineWidth = 1;
    for (let i = 0; i < COUNT; i++) {
      const p1 = projected[i];
      for (let j = i + 1; j < Math.min(COUNT, i + 12); j++) {
        const p2 = projected[j], dx = p1.sx - p2.sx, dy = p1.sy - p2.sy, dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 86) {
          ctx.strokeStyle = `rgba(16, 185, 129, ${Math.max(0.04, (1 - dist / 86) * (0.34 - burstFactor * 0.15)).toFixed(3)})`;
          ctx.beginPath(); ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
        }
      }
    }

    projected.sort((a, b) => b.z - a.z);
    for (const pt of projected) {
      ctx.fillStyle = pt.color;
      ctx.globalAlpha = Math.max(0.25, Math.min(0.95, pt.scale));
      ctx.beginPath(); ctx.arc(pt.sx, pt.sy, Math.max(1.4, pt.size * pt.scale * (1.3 + burstFactor * 0.5)), 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  window.scrollToChapter = (idx) => document.getElementById(`home-chapter-${idx}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  renderLoop();
})();
"""
}

EXTRA_V6_CSS = """
/* ==================== V6: THEME BTN, AVATAR, CHALLENGES & EXAM IDE ==================== */
.theme-toggle-top {
  width: 36px; height: 36px; border-radius: 9px;
  border: 1px solid var(--border-subtle); background: var(--bg-elevated);
  color: var(--text-primary); display: grid; place-items: center;
  cursor: pointer; font-size: 16px; transition: all 0.2s ease;
}
.theme-toggle-top:hover { border-color: var(--accent-emerald); transform: rotate(18deg); }

.user-avatar-chip {
  display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px 4px 5px;
  border-radius: 999px; border: 1px solid var(--border-highlight);
  background: var(--bg-elevated); color: var(--text-primary);
  font-weight: 600; font-size: 12.5px; cursor: pointer; transition: all 0.2s ease;
}
.user-avatar-chip:hover { background: var(--bg-surface); }
.user-avatar-img {
  width: 26px; height: 26px; border-radius: 50%; object-fit: cover;
  background: linear-gradient(135deg, var(--accent-emerald), var(--accent-blue));
  color: #031C14; display: grid; place-items: center; font-weight: 800; font-size: 12px;
}

.workflow-step-card {
  display: flex; align-items: flex-start; gap: 12px; padding: 13px 15px;
  border-radius: 11px; background: var(--bg-elevated); border: 1px solid var(--border-subtle); margin-bottom: 10px;
}
.workflow-step-num {
  width: 28px; height: 28px; border-radius: 8px; background: var(--accent-emerald-glow);
  color: var(--accent-emerald); border: 1px solid var(--border-highlight);
  display: grid; place-items: center; font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 12px; flex-shrink: 0;
}

.challenge-stage-card {
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  border-radius: 16px; padding: 22px; transition: all 0.25s ease; box-shadow: var(--shadow-card);
}
.challenge-stage-card:hover { transform: translateY(-4px); border-color: var(--accent-emerald); }
.challenge-stage-card.completed { border-color: var(--accent-emerald); background: linear-gradient(180deg, rgba(16,185,129,0.08), var(--bg-surface)); }

.exam-ide-shell {
  height: calc(100vh - 62px); display: grid;
  grid-template-columns: 330px 1fr 340px; background: var(--bg-base);
}
@media (max-width: 1024px) { .exam-ide-shell { grid-template-columns: 1fr; height: auto; } }
"""

# ==============================================================================
# 3. CHẶNG THỬ THÁCH GIẢI TRÍ & LOGIC ĐIỀU KHIỂN MỚI (JS/APP.JS)
# ==============================================================================
APP_JS_V6 = """// V-CODE EDU v6.0 — BỘ ĐIỀU KHIỂN TRUNG TÂM
const ROLE_LABELS = { teacher: 'Giáo viên', student: 'Học sinh', admin: 'Quản trị viên', none: 'Chưa chọn vai trò' };

const SNIPPETS = [
  { label: '+ Nhập số N', code: "n = int(input())\\n" },
  { label: '+ Vòng lặp for', code: "for i in range(1, n + 1):\\n    print(i)\\n" },
  { label: '+ Rẽ nhánh if/else', code: "if n % 2 == 0:\\n    print('Chan')\\nelse:\\n    print('Le')\\n" },
  { label: '+ Python Tiếng Việt', code: "n = nhap_so()\\nlap_voi i trong_khoang(1, n + 1):\\n    in_ra(i)\\n" }
];

const CHALLENGE_STAGES = [
  {
    id: 'ch-01', stage: 1, icon: '🚀', title: 'Chặng 1: Khởi động Phi thuyền',
    badge: 'Tân binh', xp: 100,
    desc: 'Nhập số năng lượng N (số nguyên). Nhân đôi N và in ra để kích hoạt động cơ phi thuyền.',
    starter: 'n = int(input())\\nprint(n * 2)',
    testCases: [{ input: '5', expected: '10' }, { input: '12', expected: '24' }]
  },
  {
    id: 'ch-02', stage: 2, icon: '🔐', title: 'Chặng 2: Giải mã Cánh cổng',
    badge: 'Thám hiểm', xp: 150,
    desc: 'Nhập mật mã nguyên N. Nếu N chẵn in "MO CUA", nếu N lẻ in "KHOA".',
    starter: 'n = int(input())\\nif n % 2 == 0:\\n    print("MO CUA")\\nelse:\\n    print("KHOA")',
    testCases: [{ input: '8', expected: 'MO CUA' }, { input: '7', expected: 'KHOA' }]
  },
  {
    id: 'ch-03', stage: 3, icon: '🌀', title: 'Chặng 3: Vòng xoáy Năng lượng',
    badge: 'Chiến binh', xp: 200,
    desc: 'Nhập số nguyên dương N. Tính tổng các số từ 1 đến N để nạp đầy lõi năng lượng.',
    starter: 'n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    tong += i\\nprint(tong)',
    testCases: [{ input: '5', expected: '15' }, { input: '10', expected: '55' }]
  },
  {
    id: 'ch-04', stage: 4, icon: '🧮', title: 'Chặng 4: Mật mã Số học',
    badge: 'Học giả', xp: 250,
    desc: 'Nhập số nguyên dương N. Đếm xem từ 1 đến N có bao nhiêu số chia hết cho 3.',
    starter: 'n = int(input())\\ndem = 0\\nfor i in range(1, n + 1):\\n    if i % 3 == 0:\\n        dem += 1\\nprint(dem)',
    testCases: [{ input: '9', expected: '3' }, { input: '15', expected: '5' }]
  },
  {
    id: 'ch-05', stage: 5, icon: '👑', title: 'Chặng 5: Chinh phục Đỉnh cao',
    badge: 'Bậc thầy Python', xp: 350,
    desc: 'Nhập số nguyên dương N. Tính giai thừa N! = 1 * 2 * ... * N để mở kho báu cuối cùng.',
    starter: 'n = int(input())\\ngt = 1\\nfor i in range(1, n + 1):\\n    gt = gt * i\\nprint(gt)',
    testCases: [{ input: '5', expected: '120' }, { input: '4', expected: '24' }]
  }
];

window.AppState = {
  currentView: 'home',
  currentLesson: window.VCODE_LESSONS[2],
  currentExamAssignment: null,
  activeClassroomCode: '',
  activeStudentClassCode: '',
  user: JSON.parse(localStorage.getItem('vcode_current_user') || 'null'),
  completedLessons: window.VCodeOfflineDB.load().completedLessons || ['py-01'],
  completedChallenges: JSON.parse(localStorage.getItem('vcode_completed_challenges') || '[]'),
  teacherClasses: [],
  studentClasses: [],
  currentRoster: [],
  peekStudentUsername: null,
  livePollTimer: null
};

function apiBase() { return window.VCodeAI.getConfig().backendUrl.replace(/\\/$/, ''); }

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
  if (viewId === 'challenges') renderChallengeStages();
  if (viewId === 'account') renderAccountView();
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
function togglePassVis(id) { const el = document.getElementById(id); if (el) el.type = el.type === 'password' ? 'text' : 'password'; }

// ==================== AUTH OAUTH THẬT & QUẢN LÝ TÀI KHOẢN ====================
function handleTopUserClick() {
  if (window.AppState.user) switchView('account');
  else openAuthModal('login');
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
    ? 'Đăng nhập bằng Google, Facebook, GitHub hoặc Email của bạn'
    : 'Chỉ cần Họ tên, Email và Mật khẩu — hoàn toàn miễn phí';
}

function saveLoggedInUser(userObj) {
  window.AppState.user = userObj;
  localStorage.setItem('vcode_current_user', JSON.stringify(userObj));
  updateUserHeaderUI();
  if (window.AppState.currentView === 'classroom') initClassroomPortalData();
  if (window.AppState.currentView === 'account') renderAccountView();
}

function logoutAction() {
  window.AppState.user = null;
  localStorage.removeItem('vcode_current_user');
  updateUserHeaderUI();
  switchView('home');
  showToast('👋 Bạn đã đăng xuất an toàn khỏi V-Code Edu.');
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-identifier').value.trim();
  const password = document.getElementById('login-password').value;
  try {
    const data = await apiRequest('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`👋 Đăng nhập thành công! Xin chào <b>${data.user.full_name}</b>.`);
  } catch (err) {
    alert(err.message === 'OFFLINE' ? 'Đang mất mạng hoặc chưa bật máy chủ Backend cổng 8000!' : err.message);
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const full_name = document.getElementById('reg-fullname').value.trim();
  const email = document.getElementById('reg-email').value.trim().toLowerCase();
  const password = document.getElementById('reg-password').value;
  try {
    const data = await apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`🎉 Tạo tài khoản thành công cho <b>${data.user.full_name}</b>!`);
  } catch (err) {
    alert(err.message);
  }
}

async function handleRealSocialLogin(provider) {
  try {
    const oauthRes = await window.VCodeOAuth.signInWithProvider(provider);
    if (!oauthRes.configured) {
      // Nếu chưa gắn Firebase Config thì mở hộp thoại hướng dẫn cấu hình OAuth thật trong 1 phút
      document.getElementById('oauth-config-modal').classList.add('open');
      return;
    }
    const data = await apiRequest('/api/auth/social', {
      method: 'POST',
      body: JSON.stringify({
        provider, email: oauthRes.email, full_name: oauthRes.full_name, avatar_url: oauthRes.avatar_url
      })
    });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`✅ Đã đăng nhập thật bằng <b>${provider.toUpperCase()}</b> — Xin chào <b>${data.user.full_name}</b>!`);
  } catch (err) {
    alert(`Lỗi đăng nhập ${provider.toUpperCase()}: ${err.message}`);
  }
}

function saveOAuthConfig() {
  const cfg = {
    apiKey: document.getElementById('fb-api-key').value.trim(),
    authDomain: document.getElementById('fb-auth-domain').value.trim(),
    projectId: document.getElementById('fb-project-id').value.trim()
  };
  localStorage.setItem('vcode_firebase_config', JSON.stringify(cfg));
  window.VCODE_FIREBASE_CONFIG = cfg;
  closeModal('oauth-config-modal');
  showToast('🔐 Đã lưu cấu hình Firebase OAuth thật! Bấm lại nút Google/Facebook/GitHub để đăng nhập.');
}

function updateUserHeaderUI() {
  const u = window.AppState.user;
  const xpEl = document.getElementById('user-xp-badge');
  const btn = document.getElementById('user-profile-btn');
  const drawerUser = document.getElementById('drawer-user-summary');

  if (!u) {
    xpEl.style.display = 'none';
    btn.className = 'btn btn-sm btn-primary';
    btn.innerHTML = '🔑 Đăng nhập';
    if (drawerUser) drawerUser.innerHTML = `<div style="font-size:12.5px;color:var(--text-secondary)">Chưa đăng nhập tài khoản</div>`;
    return;
  }
  xpEl.style.display = 'inline-flex';
  xpEl.textContent = `${u.xp || 100} XP`;
  btn.className = 'user-avatar-chip';
  const initial = (u.full_name || 'U').charAt(0).toUpperCase();
  const avHtml = u.avatar_url ? `<img src="${u.avatar_url}" class="user-avatar-img" alt="av"/>` : `<span class="user-avatar-img">${initial}</span>`;
  btn.innerHTML = `${avHtml}<span>${u.full_name}</span>`;
  if (drawerUser) {
    drawerUser.innerHTML = `<strong>${u.full_name}</strong><div style="font-size:11.5px;color:var(--text-secondary)">${u.email}</div><div style="font-size:11.5px;color:var(--accent-emerald);margin-top:2px">${ROLE_LABELS[u.role] || 'Thành viên'}</div>`;
  }
}

function renderAccountView() {
  const u = window.AppState.user;
  if (!u) { openAuthModal('login'); switchView('home'); return; }
  document.getElementById('acc-fullname').value = u.full_name || '';
  document.getElementById('acc-email').value = u.email || '';
  document.getElementById('acc-school').value = u.school_name || '';
  document.getElementById('acc-class').value = u.class_name || '';
  document.getElementById('acc-role-badge').textContent = ROLE_LABELS[u.role] || 'Chưa chọn vai trò';
  const preview = document.getElementById('acc-avatar-preview');
  preview.innerHTML = u.avatar_url
    ? `<img src="${u.avatar_url}" style="width:76px;height:76px;border-radius:50%;object-fit:cover;border:2px solid var(--accent-emerald)"/>`
    : `<div style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,var(--accent-emerald),var(--accent-blue));color:#031C14;display:grid;place-items:center;font-size:28px;font-weight:800">${(u.full_name || 'U').charAt(0).toUpperCase()}</div>`;
}

function handleAvatarFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    window.AppState.user.avatar_url = dataUrl;
    await saveAccountProfileAction();
  };
  reader.readAsDataURL(file);
}

async function saveAccountProfileAction(e) {
  if (e) e.preventDefault();
  const u = window.AppState.user;
  const payload = {
    email: u.email,
    full_name: document.getElementById('acc-fullname').value.trim() || u.full_name,
    school_name: document.getElementById('acc-school').value.trim(),
    class_name: document.getElementById('acc-class').value.trim(),
    avatar_url: u.avatar_url || ''
  };
  try {
    const res = await apiRequest('/api/auth/update-profile', { method: 'POST', body: JSON.stringify(payload) });
    saveLoggedInUser(res.user);
    showToast('✅ Đã lưu thông tin hồ sơ & ảnh đại diện vào Database!');
  } catch (err) {
    saveLoggedInUser({ ...u, ...payload });
    showToast('🟠 Đã cập nhật hồ sơ cục bộ.');
  }
}

async function handleChangePasswordSubmit(e) {
  e.preventDefault();
  const old_password = document.getElementById('acc-old-pass').value;
  const new_password = document.getElementById('acc-new-pass').value;
  const confirm = document.getElementById('acc-confirm-pass').value;
  if (new_password !== confirm) { alert('Mật khẩu mới xác nhận không khớp!'); return; }
  try {
    const res = await apiRequest('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ email: window.AppState.user.email, old_password, new_password })
    });
    e.target.reset();
    showToast(`🔐 ${res.message}`);
  } catch (err) {
    alert(err.message);
  }
}

// ==================== LỚP HỌC CHUẨN OLM (KHÓA VAI TRÒ 1 LẦN + DỮ LIỆU THẬT) ====================
async function initClassroomPortalData() {
  const u = window.AppState.user;
  const loginNotice = document.getElementById('classroom-login-required');
  const rolePicker = document.getElementById('classroom-role-once-picker');
  const teacherPortal = document.getElementById('portal-teacher');
  const studentPortal = document.getElementById('portal-student');

  loginNotice.style.display = 'none';
  rolePicker.style.display = 'none';
  teacherPortal.style.display = 'none';
  studentPortal.style.display = 'none';

  if (!u) {
    loginNotice.style.display = 'block';
    return;
  }
  if (!u.role || u.role === 'none') {
    rolePicker.style.display = 'block';
    return;
  }

  if (u.role === 'teacher' || u.role === 'admin') {
    teacherPortal.style.display = 'block';
    try {
      const res = await apiRequest(`/api/classes/teacher/${encodeURIComponent(u.email)}`);
      window.AppState.teacherClasses = res.classes || [];
    } catch { window.AppState.teacherClasses = []; }
    renderTeacherClassesGrid();
    if (window.AppState.teacherClasses.length > 0) {
      const code = window.AppState.teacherClasses.some((c) => c.code === window.AppState.activeClassroomCode)
        ? window.AppState.activeClassroomCode : window.AppState.teacherClasses[0].code;
      selectTeacherClassroom(code);
    } else {
      document.getElementById('teacher-active-class-panel').style.display = 'none';
    }
    startLiveMonitoringPolling();
  } else {
    studentPortal.style.display = 'block';
    try {
      const res = await apiRequest(`/api/classes/student/${encodeURIComponent(u.email)}`);
      window.AppState.studentClasses = res.classes || [];
    } catch { window.AppState.studentClasses = []; }
    renderStudentJoinedClasses();
  }
}

async function lockRoleOnceAction(role) {
  const label = role === 'teacher' ? 'GIÁO VIÊN' : 'HỌC SINH';
  if (!confirm(`Xác nhận đăng ký vai trò ${label}? Lưu ý: Vai trò này chỉ được chọn 1 lần duy nhất cho tài khoản của bạn.`)) return;
  const u = window.AppState.user;
  try {
    const res = await apiRequest('/api/auth/set-role', {
      method: 'POST',
      body: JSON.stringify({ email: u.email, role, school_name: u.school_name || 'THCS & THPT Hòa Phú', class_name: u.class_name || '' })
    });
    saveLoggedInUser(res.user);
    showToast(`🔒 Đã kích hoạt cố định vai trò <b>${label}</b>!`);
    initClassroomPortalData();
  } catch (err) {
    alert(err.message);
  }
}

function switchTeacherSubpanel(panelName) {
  document.querySelectorAll('[data-tpanel]').forEach((b) => b.classList.toggle('active', b.dataset.tpanel === panelName));
  document.querySelectorAll('.tpanel-box').forEach((p) => { p.style.display = p.id === `tpanel-${panelName}` ? 'block' : 'none'; });
}

function renderTeacherClassesGrid() {
  const grid = document.getElementById('teacher-classes-grid');
  if (!grid) return;
  if (window.AppState.teacherClasses.length === 0) {
    grid.innerHTML = `<div class="bento-card" style="grid-column:span 3;text-align:center"><p>Bạn chưa tạo lớp học nào. Hãy bấm <b>+ Tạo lớp học mới</b> để lấy ID mã lớp gửi cho học sinh!</p></div>`;
    return;
  }
  grid.innerHTML = window.AppState.teacherClasses.map((c) => `
    <div class="olm-class-card ${c.code === window.AppState.activeClassroomCode ? 'selected' : ''}" onclick="selectTeacherClassroom('${c.code}')">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span class="olm-code-chip">${c.code}</span>
        <span class="badge badge-blue">${c.students_count || 0} HS thật</span>
      </div>
      <h4 style="font-size:15px;margin-bottom:4px">${c.name}</h4>
      <div style="font-size:12px;color:var(--text-secondary)">${c.grade_subject} • ${c.assignments_count || 0} bài tập</div>
    </div>`).join('');
}

async function selectTeacherClassroom(code) {
  window.AppState.activeClassroomCode = code;
  document.getElementById('teacher-active-class-panel').style.display = 'block';
  renderTeacherClassesGrid();
  document.getElementById('teacher-selected-class-code').textContent = code;
  try {
    const detail = await apiRequest(`/api/classes/${encodeURIComponent(code)}/detail`);
    document.getElementById('teacher-selected-class-title').textContent = detail.classroom.name;
    window.AppState.currentRoster = detail.roster || [];
    renderRealRosterTable();

    const aList = document.getElementById('teacher-assignments-list');
    aList.innerHTML = detail.assignments.length
      ? detail.assignments.map((a) => `
        <div class="olm-assignment-row">
          <div><strong>${a.title}</strong> <span class="badge badge-easy">${a.difficulty}</span><div style="font-size:12px;color:var(--text-secondary)">${a.description} • Hạn: ${a.due_date}</div></div>
          <span class="mono badge badge-blue">${a.code}</span>
        </div>`).join('')
      : `<p style="color:var(--text-secondary);font-size:13px">Chưa có bài tập nào trong lớp này.</p>`;

    const sBody = document.getElementById('teacher-submissions-body');
    sBody.innerHTML = detail.submissions.length
      ? detail.submissions.map((s) => `
        <tr><td><strong>${s.student_name}</strong></td><td class="mono">${s.assignment_code}</td><td class="mono">${s.passed_tests}/${s.total_tests}</td><td><span class="badge ${s.score === 100 ? 'badge-easy' : 'badge-med'}">${s.score}/100</span></td><td class="mono" style="font-size:12px">${s.submitted_at}</td></tr>`).join('')
      : `<tr><td colspan="5" style="color:var(--text-secondary)">Chưa có học sinh nào nộp bài.</td></tr>`;
  } catch {}
}

function renderRealRosterTable() {
  const tbody = document.getElementById('realtime-monitor-body');
  if (!tbody) return;
  const roster = window.AppState.currentRoster || [];
  if (roster.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:24px">Chưa có học sinh nào tham gia lớp này. Hãy chia sẻ mã lớp <b>${window.AppState.activeClassroomCode}</b> để học sinh vào lớp!</td></tr>`;
    return;
  }
  tbody.innerHTML = roster.map((s) => {
    const badgeMap = {
      not_started: `<span class="badge badge-med">⚪ Chưa làm</span>`,
      coding: `<span class="badge badge-blue"><span class="live-pulse"></span> Đang làm bài</span>`,
      error: `<span class="badge badge-hard">⚠ Đang làm (Gặp lỗi)</span>`,
      completed: `<span class="badge badge-easy">✓ Đã làm (${s.score ?? 100}/100đ)</span>`
    };
    return `
      <tr>
        <td><strong>${s.full_name}</strong><div style="font-size:11px;color:var(--text-muted)">${s.email} • ${s.updated}</div></td>
        <td>${s.problem}</td>
        <td>${badgeMap[s.status] || badgeMap.not_started}</td>
        <td style="min-width:120px"><div style="font-size:11px;margin-bottom:4px" class="mono">${s.progress}%</div><div class="progress-track"><div class="progress-fill" style="width:${s.progress}%"></div></div></td>
        <td>${s.code ? `<button class="btn btn-sm btn-primary" onclick="openPeekModal('${s.username}')">👁 Xem bài làm</button>` : `<span style="font-size:12px;color:var(--text-muted)">Chưa có code</span>`}</td>
      </tr>`;
  }).join('');
}

function openPeekModal(username) {
  const st = (window.AppState.currentRoster || []).find((s) => s.username === username);
  if (!st) return;
  window.AppState.peekStudentUsername = username;
  document.getElementById('peek-student-name').textContent = st.full_name;
  document.getElementById('peek-student-problem').textContent = st.problem;
  document.getElementById('peek-code-preview').textContent = st.code || '# Chưa có mã nguồn';
  document.getElementById('peek-modal').classList.add('open');
}

function sendTeacherHintAction() {
  const txt = document.getElementById('teacher-hint-input').value.trim();
  if (!txt || !window.AppState.peekStudentUsername) return;
  window.VCodeMonitor.sendHintToStudent(window.AppState.peekStudentUsername, txt);
  document.getElementById('teacher-hint-input').value = '';
  closeModal('peek-modal');
  showToast('💬 Đã gửi nhận xét trực tiếp tới học sinh!');
}

function startLiveMonitoringPolling() {
  clearInterval(window.AppState.livePollTimer);
  window.AppState.livePollTimer = setInterval(() => {
    if (window.AppState.currentView === 'classroom' && window.AppState.user?.role === 'teacher' && window.AppState.activeClassroomCode) {
      selectTeacherClassroom(window.AppState.activeClassroomCode);
    }
  }, 3500);
}

async function handleCreateClassSubmit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('new-class-name').value.trim(),
    grade_subject: document.getElementById('new-class-subject').value.trim(),
    code: document.getElementById('new-class-code').value.trim().toUpperCase(),
    description: document.getElementById('new-class-desc').value.trim(),
    teacher_email: window.AppState.user.email
  };
  try {
    const res = await apiRequest('/api/classes/create', { method: 'POST', body: JSON.stringify(payload) });
    closeModal('create-class-modal');
    e.target.reset();
    window.AppState.activeClassroomCode = res.classroom.code;
    showToast(`🎉 Đã tạo lớp <b>${res.classroom.name}</b> — Mã lớp ID: <b>${res.classroom.code}</b>`);
    initClassroomPortalData();
  } catch (err) { alert(err.message); }
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
    showToast(`📝 Đã giao bài tập <b>${payload.title}</b>!`);
    selectTeacherClassroom(payload.classroom_code);
    switchTeacherSubpanel('assignments');
  } catch (err) { alert(err.message); }
}

function copyActiveClassCode() {
  navigator.clipboard?.writeText(window.AppState.activeClassroomCode);
  showToast(`📋 Đã sao chép ID mã lớp: <b>${window.AppState.activeClassroomCode}</b>`);
}

function shareActiveClassQR() {
  const code = window.AppState.activeClassroomCode;
  const joinUrl = `${window.location.href.split('#')[0]}#join=${code}`;
  document.getElementById('share-link-input').value = joinUrl;
  const qrBox = document.getElementById('qr-code-box');
  qrBox.innerHTML = '';
  if (typeof QRCode !== 'undefined') new QRCode(qrBox, { text: joinUrl, width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  document.getElementById('share-modal').classList.add('open');
}

// ==================== CỔNG HỌC SINH & TRANG IDE BÀI TẬP RIÊNG (TỰ LÀM) ====================
async function joinClassByCodeAction(explicitCode) {
  const inp = document.getElementById('student-join-code-input');
  const code = (explicitCode || inp?.value || '').trim().toUpperCase();
  if (!code) { alert('Vui lòng nhập ID mã lớp học!'); return; }
  try {
    const res = await apiRequest('/api/classes/join', {
      method: 'POST', body: JSON.stringify({ code, student_email: window.AppState.user.email })
    });
    if (inp) inp.value = '';
    showToast(`🎉 Đã tham gia lớp <b>${res.classroom.name}</b>!`);
    await initClassroomPortalData();
    openStudentClassDetail(res.classroom.code);
  } catch (err) { alert(err.message); }
}

function renderStudentJoinedClasses() {
  const box = document.getElementById('student-joined-classes-list');
  if (!box) return;
  if (window.AppState.studentClasses.length === 0) {
    box.innerHTML = `<div class="bento-card"><p style="font-size:13px;color:var(--text-secondary)">Em chưa tham gia lớp học nào. Nhập mã ID lớp (VD: <b>TIN10HP</b>) ở phía trên để vào lớp!</p></div>`;
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
    window.__classAssignmentsCache = detail.assignments;
    const listEl = document.getElementById('student-assignments-list');
    listEl.innerHTML = detail.assignments.length
      ? detail.assignments.map((a, idx) => {
          const mySubs = detail.submissions.filter((s) => s.assignment_code === a.code && s.username === window.AppState.user.username);
          const best = mySubs.length ? Math.max(...mySubs.map((s) => s.score)) : null;
          return `
            <div class="olm-assignment-row">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                  <strong>${a.title}</strong> <span class="badge badge-blue">${a.difficulty}</span>
                  ${best !== null ? `<span class="badge badge-easy">✓ Đã làm (${best}/100đ)</span>` : `<span class="badge badge-med">Chưa làm</span>`}
                </div>
                <div style="font-size:12.5px;color:var(--text-secondary)">${a.description} • Hạn nộp: ${a.due_date}</div>
              </div>
              <button class="btn btn-primary btn-sm" onclick="openDedicatedAssignmentIDE(${idx}, '${code}')">📝 Vào làm bài (Tự làm) →</button>
            </div>`;
        }).join('')
      : `<p style="color:var(--text-secondary)">Giáo viên chưa giao bài tập nào cho lớp này.</p>`;
  } catch {}
}

// MỞ TRANG IDE BÀI TẬP RIÊNG (KHÔNG AI, KHÔNG SCRATCH LIVE, KHÔNG GỢI Ý CODE)
function openDedicatedAssignmentIDE(idx, classCode) {
  const a = (window.__classAssignmentsCache || [])[idx];
  if (!a) return;
  window.AppState.currentExamAssignment = { ...a, classroom_code: classCode };
  document.getElementById('exam-class-badge').textContent = `Lớp ${classCode}`;
  document.getElementById('exam-title').textContent = a.title;
  document.getElementById('exam-desc').textContent = a.description;
  document.getElementById('exam-editor').value = a.starter_code || '# Em tự viết mã nguồn Python giải bài tập tại đây\\n';
  document.getElementById('exam-stdin').value = a.test_cases?.[0]?.input || '6';
  document.getElementById('exam-console').textContent = 'Sẵn sàng kiểm tra bài làm của em...';
  syncExamEditor();
  switchView('assignment-ide');
}

function syncExamEditor() {
  const ed = document.getElementById('exam-editor');
  if (!ed) return;
  const code = ed.value;
  document.getElementById('exam-line-numbers').innerHTML = Array.from({ length: code.split('\\n').length }, (_, i) => i + 1).join('<br>');
  clearTimeout(window.__examRtTimer);
  window.__examRtTimer = setTimeout(() => {
    const a = window.AppState.currentExamAssignment;
    if (a && window.AppState.user) {
      window.VCodeMonitor.emitStudentActivity(
        { ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'coding',
        Math.min(90, Math.max(20, code.split('\\n').length * 12)), 0
      );
    }
  }, 600);
}

function runExamCodeAction() {
  const code = document.getElementById('exam-editor').value;
  const stdin = document.getElementById('exam-stdin').value.split('\\n');
  const res = window.VCodeIDE.runPython(code, stdin);
  const outEl = document.getElementById('exam-console');
  const a = window.AppState.currentExamAssignment;
  if (res.ok) {
    outEl.textContent = `>>> Kết quả chạy thử:\\n${res.output || '(Không có dữ liệu in ra)'}`;
  } else {
    outEl.textContent = `>>> Lỗi thực thi:\\n${res.error}`;
    if (a && window.AppState.user) {
      window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'error', 40, 1);
    }
  }
}

async function submitExamCodeAction() {
  const code = document.getElementById('exam-editor').value;
  const a = window.AppState.currentExamAssignment;
  if (!a) return;
  const report = window.VCodeIDE.gradeSubmission(code, a.test_cases || [{ input: '6', expected: '12' }]);
  let out = `=== KẾT QUẢ NỘP BÀI: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\\n`;
  report.details.forEach((d) => {
    out += `• Test #${d.index}: ${d.passed ? '✓ ĐẠT' : '✗ CHƯA ĐẠT'}\\n`;
  });
  document.getElementById('exam-console').textContent = out;

  try {
    const saved = await apiRequest('/api/assessment/submit', {
      method: 'POST',
      body: JSON.stringify({
        email: window.AppState.user.email, student_name: window.AppState.user.full_name,
        classroom_code: a.classroom_code, assignment_code: a.code,
        source_code: code, passed_tests: report.passed, total_tests: report.total, score: report.score
      })
    });
    if (saved.new_xp) { window.AppState.user.xp = saved.new_xp; updateUserHeaderUI(); }
    window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'completed', 100, 0);
    showToast(`✅ Đã nộp bài thành công! Điểm số: <b>${report.score}/100</b>.`);
  } catch (err) {
    alert('Không gửi được bài nộp lên máy chủ: ' + err.message);
  }
}

// ==================== THỬ THÁCH CHẶNG GIẢI TRÍ (THAY ĐẤU TRƯỜNG) ====================
function renderChallengeStages() {
  const grid = document.getElementById('challenges-stages-grid');
  if (!grid) return;
  const doneIds = window.AppState.completedChallenges;
  const pct = Math.round((doneIds.length / CHALLENGE_STAGES.length) * 100);
  document.getElementById('challenge-progress-text').textContent = `Đã chinh phục ${doneIds.length}/${CHALLENGE_STAGES.length} chặng (${pct}%)`;
  document.getElementById('challenge-progress-bar').style.width = `${pct}%`;

  grid.innerHTML = CHALLENGE_STAGES.map((c) => {
    const done = doneIds.includes(c.id);
    return `
      <div class="challenge-stage-card ${done ? 'completed' : ''}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <span style="font-size:28px">${c.icon}</span>
          <span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã vượt qua' : `+${c.xp} XP`}</span>
        </div>
        <div style="font-size:11px;color:var(--accent-emerald);font-weight:700;margin-bottom:4px">HUY HIỆU: ${c.badge.toUpperCase()}</div>
        <h3 style="font-size:16.5px;margin-bottom:8px">${c.title}</h3>
        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px">${c.desc}</p>
        <button class="btn btn-sm ${done ? '' : 'btn-primary'}" style="width:100%" onclick="openChallengeInIDE('${c.id}')">${done ? 'Chơi lại chặng này' : '⚡ Chinh phục ngay →'}</button>
      </div>`;
  }).join('');
}

function openChallengeInIDE(chId) {
  const ch = CHALLENGE_STAGES.find((c) => c.id === chId);
  if (!ch) return;
  window.AppState.currentLesson = { id: ch.id, title: ch.title, summary: ch.desc, starter: ch.starter, testCases: ch.testCases, isChallenge: true };
  document.getElementById('prob-title').textContent = `${ch.icon} ${ch.title}`;
  document.getElementById('prob-desc').textContent = ch.desc;
  document.getElementById('code-editor').value = ch.starter;
  document.getElementById('custom-stdin').value = ch.testCases[0].input;
  switchView('workspace');
  syncLiveEditorOutputs();
}

// ==================== IDE TỰ DO + SCRATCH LIVE + AI HYBRID ====================
function switchRightTab(tabName) {
  document.querySelectorAll('.subtab-btn').forEach((b) => b.classList.toggle('active', b.dataset.rtab === tabName));
  document.querySelectorAll('.right-panel').forEach((p) => p.classList.toggle('active', p.id === `rpanel-${tabName}`));
}

function syncLiveEditorOutputs() {
  const ed = document.getElementById('code-editor');
  if (!ed) return;
  const code = ed.value;
  const linesEl = document.getElementById('line-numbers');
  if (linesEl) linesEl.innerHTML = Array.from({ length: code.split('\\n').length }, (_, i) => i + 1).join('<br>');
  const scratchStage = document.getElementById('scratch-live-stage');
  if (scratchStage) scratchStage.innerHTML = window.ScratchBridge.renderFromPython(code);
  const flowBox = document.getElementById('flowchart-box');
  if (flowBox) flowBox.innerHTML = window.VCodeAI.generateFlowchartSVG(code);
}

function openLessonInIDE(lessonId) {
  const found = window.VCODE_LESSONS.find((l) => l.id === lessonId);
  if (!found) return;
  window.AppState.currentLesson = found;
  document.getElementById('prob-title').textContent = found.title;
  document.getElementById('prob-desc').textContent = found.summary;
  document.getElementById('code-editor').value = localStorage.getItem('vcode_draft_' + found.id) || found.starter;
  renderSidebarProblems();
  switchView('workspace');
  syncLiveEditorOutputs();
}

function runCodeAction() {
  const code = document.getElementById('code-editor').value;
  const stdin = document.getElementById('custom-stdin').value.split('\\n');
  const res = window.VCodeIDE.runPython(code, stdin);
  const consoleEl = document.getElementById('console-output');
  if (res.ok) {
    consoleEl.textContent = `>>> Thực thi hoàn tất (0.01s):\\n${res.output || '(Không có dữ liệu in ra)'}`;
    appendAIChat('ai', `✓ Mã nguồn chạy thành công! Kết quả: "${res.output}".`);
  } else {
    consoleEl.textContent = `>>> Lỗi thực thi:\\n${res.error}`;
    appendAIChat('error', window.VCodeAI.offlineDiagnose('', code, res.error));
    switchRightTab('ai');
  }
}

function submitAutoGradeAction() {
  const code = document.getElementById('code-editor').value;
  const lesson = window.AppState.currentLesson;
  const report = window.VCodeIDE.gradeSubmission(code, lesson.testCases || [{ input: '6', expected: '12' }]);
  let out = `=== CHẤM TỰ ĐỘNG: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\\n`;
  report.details.forEach((d) => { out += `• Test #${d.index} [Input: ${d.input}]: ${d.passed ? '✓ ĐẠT' : `✗ SAI (Ra '${d.actual}', cần '${d.expected}')`}\\n`; });
  document.getElementById('console-output').textContent = out;
  switchRightTab('ai');

  if (report.score === 100) {
    if (lesson.isChallenge && !window.AppState.completedChallenges.includes(lesson.id)) {
      window.AppState.completedChallenges.push(lesson.id);
      localStorage.setItem('vcode_completed_challenges', JSON.stringify(window.AppState.completedChallenges));
      showToast('🏆 Tuyệt vời! Em đã vượt qua chặng thử thách và mở khóa huy hiệu mới!');
    } else if (!window.AppState.completedLessons.includes(lesson.id)) {
      window.AppState.completedLessons.push(lesson.id);
      const db = window.VCodeOfflineDB.load();
      db.completedLessons = window.AppState.completedLessons;
      window.VCodeOfflineDB.save(db);
      showToast('🎉 Đạt 100/100 điểm bài thực hành!');
    }
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
  const res = await window.VCodeAI.askHybrid(q, document.getElementById('code-editor').value);
  appendAIChat('ai', res.text, res.mode === 'offline' ? '🟠 AI Socratic Offline' : '🟢 AI Online API');
}

function openShareModal() {
  const code = document.getElementById('code-editor').value;
  const payload = btoa(unescape(encodeURIComponent(JSON.stringify({ title: window.AppState.currentLesson.title, code }))));
  const shareUrl = `${window.location.href.split('#')[0]}#share=${payload}`;
  document.getElementById('share-link-input').value = shareUrl;
  const qrBox = document.getElementById('qr-code-box');
  qrBox.innerHTML = '';
  if (typeof QRCode !== 'undefined') new QRCode(qrBox, { text: shareUrl.slice(0, 900), width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  document.getElementById('share-modal').classList.add('open');
}

function copyShareLink() { const inp = document.getElementById('share-link-input'); inp.select(); navigator.clipboard?.writeText(inp.value); showToast('🔗 Đã sao chép đường link!'); }
function downloadPythonFile() { const blob = new Blob([document.getElementById('code-editor').value], { type: 'text/x-python;charset=utf-8' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'vcode_edu.py'; a.click(); }
function saveAIConfig() { localStorage.setItem('vcode_backend_url', document.getElementById('cfg-backend-url').value.trim() || 'http://localhost:8000'); localStorage.setItem('vcode_gemini_key', document.getElementById('cfg-gemini-key').value.trim()); closeModal('ai-config-modal'); showToast('⚙️ Đã lưu cấu hình!'); }

function renderLearningPath() {
  const grid = document.getElementById('learning-lessons-grid');
  if (!grid) return;
  const doneCount = window.AppState.completedLessons.length;
  const pct = Math.round((doneCount / window.VCODE_LESSONS.length) * 100);
  document.getElementById('learning-progress-text').textContent = `Đã hoàn thành ${doneCount}/${window.VCODE_LESSONS.length} bài học Python (${pct}%)`;
  document.getElementById('learning-progress-bar').style.width = `${pct}%`;
  grid.innerHTML = window.VCODE_LESSONS.map((l) => {
    const done = window.AppState.completedLessons.includes(l.id);
    return `<div class="bento-card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã hoàn thành' : l.level}</span><span class="mono" style="font-size:11.5px;color:var(--text-muted)">⏱ ${l.duration}</span></div><h3>${l.title}</h3><p style="margin-bottom:10px">${l.summary}</p><div style="font-size:12.5px;color:var(--text-secondary);background:var(--bg-elevated);padding:10px;border-radius:8px;margin-bottom:14px">${l.theory}</div><button class="btn btn-sm btn-primary" onclick="openLessonInIDE('${l.id}')">💻 Thực hành &amp; Xem Scratch Live →</button></div>`;
  }).join('');
}

function renderSidebarProblems() {
  const el = document.getElementById('problem-list');
  if (!el) return;
  el.innerHTML = window.VCODE_LESSONS.map((l) => `<div onclick="openLessonInIDE('${l.id}')" style="padding:10px;border:1px solid ${window.AppState.currentLesson.id === l.id ? 'var(--accent-emerald)' : 'var(--border-subtle)'};border-radius:8px;margin-bottom:8px;cursor:pointer;background:var(--bg-surface)"><strong style="font-size:12.5px">${l.title}</strong><div style="font-size:11px;color:var(--text-secondary);margin-top:3px">${l.level}</div></div>`).join('');
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('vcode_theme', next);
  const btn = document.getElementById('top-theme-btn');
  if (btn) btn.textContent = next === 'light' ? '🌙' : '☀️';
}

window.insertSnippet = (idx) => { const ed = document.getElementById('code-editor'); ed.value += (ed.value.endsWith('\\n') ? '' : '\\n') + SNIPPETS[idx].code; syncLiveEditorOutputs(); };

window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('vcode_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const tBtn = document.getElementById('top-theme-btn');
  if (tBtn) tBtn.textContent = savedTheme === 'light' ? '🌙' : '☀️';

  document.getElementById('snippet-bar').innerHTML = SNIPPETS.map((s, i) => `<button class="snippet-chip" onclick="insertSnippet(${i})">${s.label}</button>`).join('');

  window.VCodeMonitor.init(
    () => { if (window.AppState.currentView === 'classroom' && window.AppState.activeClassroomCode) selectTeacherClassroom(window.AppState.activeClassroomCode); },
    (hint) => showToast(`👨‍🏫 <b>Nhận xét từ Giáo viên:</b> ${hint.hintText}`)
  );

  const pill = document.getElementById('network-status');
  function syncNet() {
    if (navigator.onLine) { pill.classList.remove('offline'); pill.innerHTML = `<span class="status-dot"></span><span>Online • Đồng bộ Cloud</span>`; }
    else { pill.classList.add('offline'); pill.innerHTML = `<span class="status-dot"></span><span>Offline • Lưu cục bộ PWA</span>`; }
  }
  window.addEventListener('online', syncNet);
  window.addEventListener('offline', syncNet);
  syncNet();

  updateUserHeaderUI();
  renderSidebarProblems();
  renderLearningPath();
  renderChallengeStages();
  openLessonInIDE('py-03');
  switchView('home');
});
"""

# ==============================================================================
# 4. INDEX.HTML — HOÀN THIỆN TOÀN BỘ GIAO DIỆN V6.0
# ==============================================================================
INDEX_HTML_V6 = """<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>V-Code Edu — Nền tảng Học lập trình Python, Scratch Live & AI Việt Nam</title>
  <link rel="manifest" href="manifest.json" />
  <link rel="stylesheet" href="css/design-system.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js" defer></script>
  <!-- Firebase Auth SDK cho Đăng nhập thật Google / Facebook / GitHub -->
  <script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js" defer></script>
  <script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js" defer></script>
</head>
<body>

  <!-- THANH ĐA NĂNG BÊN TRÁI -->
  <div id="drawer-backdrop" class="drawer-backdrop" onclick="toggleLeftDrawer(false)"></div>
  <aside id="left-drawer" class="left-drawer">
    <div class="drawer-header">
      <div class="brand" onclick="switchView('home')"><div class="brand-mark">V</div><span>V-Code Edu</span></div>
      <button class="btn btn-sm" onclick="toggleLeftDrawer(false)">✕</button>
    </div>
    <div class="drawer-section">
      <div class="drawer-label">Tài khoản</div>
      <div id="drawer-user-summary" style="padding:10px;border-radius:10px;background:var(--bg-elevated);border:1px solid var(--border-subtle);margin-bottom:10px"></div>
      <button class="btn btn-sm btn-primary" style="width:100%" onclick="toggleLeftDrawer(false); handleTopUserClick()">⚙️ Quản lý Tài khoản / Đăng nhập</button>
    </div>
    <div class="drawer-section">
      <div class="drawer-label">Điều hướng</div>
      <button class="drawer-item active" data-view="home" onclick="switchView('home')"><span>🏠 Trang chủ 3D</span><span>→</span></button>
      <button class="drawer-item" data-view="learning" onclick="switchView('learning')"><span>📖 Học Python</span><span>→</span></button>
      <button class="drawer-item" data-view="workspace" onclick="switchView('workspace')"><span>💻 IDE &amp; Scratch Live</span><span class="badge badge-easy">LIVE</span></button>
      <button class="drawer-item" data-view="classroom" onclick="switchView('classroom')"><span>🏫 Lớp học (OLM)</span><span>→</span></button>
      <button class="drawer-item" data-view="challenges" onclick="switchView('challenges')"><span>🎯 Thử thách Chặng</span><span>→</span></button>
    </div>
    <div class="drawer-section">
      <div class="drawer-label">Cài đặt</div>
      <button class="drawer-item" onclick="toggleLeftDrawer(false); document.getElementById('ai-config-modal').classList.add('open')"><span>⚙️ Cấu hình AI &amp; Backend</span></button>
      <button class="drawer-item" onclick="toggleLeftDrawer(false); document.getElementById('oauth-config-modal').classList.add('open')"><span>🔐 Cấu hình Google / FB OAuth</span></button>
    </div>
  </aside>

  <!-- TOPBAR (CÓ NÚT SÁNG/TỐI GÓC PHẢI & AVATAR TÀI KHOẢN) -->
  <header class="topbar">
    <div class="topbar-left">
      <button id="hamburger-btn" class="hamburger-btn" onclick="toggleLeftDrawer()" aria-label="Mở menu"><span></span><span></span><span></span></button>
      <div class="brand" onclick="switchView('home')"><div class="brand-mark">V</div><span>V-Code Edu</span><span class="badge badge-easy">v6.0</span></div>
    </div>

    <nav class="nav-segmented">
      <button class="nav-tab active" data-view="home" onclick="switchView('home')">Trang chủ</button>
      <button class="nav-tab" data-view="learning" onclick="switchView('learning')">Học Python</button>
      <button class="nav-tab" data-view="workspace" onclick="switchView('workspace')">IDE &amp; Scratch Live</button>
      <button class="nav-tab" data-view="classroom" onclick="switchView('classroom')">Lớp học</button>
      <button class="nav-tab" data-view="challenges" onclick="switchView('challenges')">Thử thách</button>
    </nav>

    <div class="top-actions">
      <div id="network-status" class="status-pill"><span class="status-dot"></span><span>Online</span></div>
      <span id="user-xp-badge" class="badge badge-easy mono" style="display:none">100 XP</span>
      <button id="user-profile-btn" class="btn btn-sm btn-primary" onclick="handleTopUserClick()">🔑 Đăng nhập</button>
      <button id="top-theme-btn" class="theme-toggle-top" onclick="toggleTheme()" title="Chuyển chế độ Sáng / Tối">☀️</button>
    </div>
  </header>

  <!-- ==================== VIEW 1: TRANG CHỦ 3D ==================== -->
  <main id="view-home" class="view-section active">
    <canvas id="scroll-3d-canvas"></canvas>

    <aside class="scroll-3d-hud" aria-label="Tiến trình cuộn 3D">
      <div class="scroll-3d-track"><div id="scroll-3d-progress-fill"></div></div>
      <button class="scroll-dot-item active" onclick="scrollToChapter(0)"><span>01. Khởi đầu</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(1)"><span>02. Scratch Live</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(2)"><span>03. Lớp học số</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(3)"><span>04. Về chúng tôi</span><span class="dot"></span></button>
    </aside>

    <!-- CHƯƠNG 1 -->
    <section id="home-chapter-0" class="scroll-chapter">
      <div class="hero-copy-block">
        <div class="eyebrow-badge"><span>●</span><span>V-Code Edu • Nền tảng Lập trình Giáo dục Việt Nam</span></div>
        <h1 class="hero-title">Học lập trình <span class="hl">Python</span> &amp; <span class="hl">Scratch Live</span> trong không gian 3D.</h1>
        <p class="hero-subtitle">Gõ Python đồng bộ khối Scratch 3.0 trực tiếp, tổ chức lớp học trực tuyến chuẩn OLM, chấm điểm Test Case tự động và hoạt động mượt mà ngay cả khi mất mạng.</p>
        <div class="hero-cta-row">
          <button class="btn btn-primary" onclick="switchView('workspace')">🚀 Mở IDE &amp; Scratch Live →</button>
          <button class="btn" onclick="scrollToChapter(1)">↓ Cuộn khám phá 3D</button>
        </div>
        <div class="hero-metrics">
          <div class="metric-item"><strong>Live Sync</strong><span>Python ↔ Scratch</span></div>
          <div class="metric-item"><strong>OLM Class</strong><span>Lớp học dữ liệu thật</span></div>
          <div class="metric-item"><strong>100% PWA</strong><span>Chạy Offline</span></div>
          <div class="metric-item"><strong>5 Chặng</strong><span>Thử thách giải trí</span></div>
        </div>
      </div>

      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="right">
          <div class="stage-window-bar"><div class="window-dots"><span></span><span></span><span></span></div><span class="mono">tong_so_chan.py — V-Code Studio</span><span class="badge badge-easy">Python 3</span></div>
          <div class="stage-body">
            <div class="stage-code-pane mono">
              <div style="color:var(--text-muted)"># Tính tổng số chẵn từ 1 đến N</div>
              <div>n = <span style="color:#10B981">int</span>(<span style="color:#10B981">input</span>())</div>
              <div>tong = <span style="color:#F59E0B">0</span></div>
              <div><span style="color:#F43F5E">for</span> i <span style="color:#F43F5E">in</span> <span style="color:#10B981">range</span>(1, n + 1):</div>
              <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#F43F5E">if</span> i % 2 == 0: tong += i</div>
              <div><span style="color:#10B981">print</span>(tong)</div>
            </div>
            <div class="stage-side-pane">
              <div><span class="bento-tag">AI Sư Phạm Tiếng Việt</span><p style="font-size:12.5px;color:var(--text-secondary)">Phân tích lỗi cú pháp tiếng Việt theo phương pháp gợi mở Socratic.</p></div>
              <button class="btn btn-primary btn-sm" onclick="switchView('workspace')">Thử Gõ Code →</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 2 -->
    <section id="home-chapter-1" class="scroll-chapter reverse">
      <div class="chapter-copy">
        <span class="bento-tag">Phân cảnh 02 • Cầu nối Tư duy Trực quan</span>
        <h2 style="font-size:28px;margin-bottom:12px">Gõ Python tới đâu, khối Scratch lắp ghép Live tới đó</h2>
        <p style="color:var(--text-secondary);margin-bottom:18px">Chuyển hóa trực tiếp từng dòng lệnh Python thành khối Scratch 3.0 theo thời gian thực, giúp học sinh THCS &amp; THPT nắm vững bản chất vòng lặp, rẽ nhánh và thuật toán.</p>
      </div>
      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="left" style="padding:22px">
          <div class="sb-block sb-hat">🚩 Khi bấm vào Chạy Chương Trình</div><br/>
          <div class="sb-block sb-sensing">⌨️ Hỏi &amp; nhập số lưu vào <span class="sb-pill">n</span></div><br/>
          <div class="sb-block sb-control">🔁 Lặp biến <span class="sb-pill">i</span> trong khoảng <span class="sb-pill">1, n + 1</span></div>
          <div class="sb-indent-wrap"><div class="sb-block sb-control">🔀 Nếu <span class="sb-hex">i % 2 == 0</span> thì</div></div>
          <div class="sb-block sb-looks">💬 Hiển thị ra màn hình <span class="sb-pill">tong</span></div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 3 (THAY CỘT BÊN PHẢI BẰNG QUY TRÌNH LỚP HỌC THIẾT THỰC) -->
    <section id="home-chapter-2" class="scroll-chapter">
      <div class="chapter-copy">
        <span class="bento-tag">Phân cảnh 03 • Lớp học Số &amp; Đánh giá Khách quan</span>
        <h2 style="font-size:28px;margin-bottom:12px">Quy trình Dạy – Học – Kiểm tra khép kín trên một nền tảng</h2>
        <p style="color:var(--text-secondary)">Học sinh làm bài tập được giao trên không gian IDE độc lập (không gợi ý AI) để đảm bảo tính tự giác, trong khi giáo viên theo dõi tiến độ và chấm điểm tự động ngay trên trình duyệt.</p>
      </div>
      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="right" style="padding:22px">
          <span class="bento-tag" style="margin-bottom:12px">Kiến trúc Vận hành Lớp học Thực tế</span>
          <div class="workflow-step-card">
            <div class="workflow-step-num">01</div>
            <div><strong>Giáo viên tạo lớp &amp; giao đề có Test Case</strong><div style="font-size:12px;color:var(--text-secondary)">Sinh mã ID lớp &amp; mã QR mời học sinh tham gia đúng lớp của mình.</div></div>
          </div>
          <div class="workflow-step-card">
            <div class="workflow-step-num">02</div>
            <div><strong>Học sinh tự thực hiện trên IDE Bài tập riêng</strong><div style="font-size:12px;color:var(--text-secondary)">Ẩn trợ lý AI &amp; code mẫu để rèn tư duy độc lập; đồng bộ trạng thái Chưa làm / Đang làm / Đã làm.</div></div>
          </div>
          <div class="workflow-step-card" style="margin-bottom:0">
            <div class="workflow-step-num">03</div>
            <div><strong>Chấm điểm tự động &amp; Lưu trữ Database</strong><div style="font-size:12px;color:var(--text-secondary)">Ghi nhận điểm số, lịch sử bài nộp và cho phép giáo viên xem trực tiếp từng dòng code.</div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 4 (XÓA LINK TRANG CON, THAY BẰNG THÔNG TIN TRANG WEB & NHÓM THỰC HIỆN) -->
    <section id="home-chapter-3" class="scroll-chapter" style="grid-template-columns:1fr">
      <div class="chapter-copy" style="max-width:980px;margin:0 auto">
        <div style="text-align:center;margin-bottom:24px">
          <span class="bento-tag">Phân cảnh 04 • Thông tin Dự án &amp; Nhóm thực hiện</span>
          <h2 style="font-size:30px;margin-bottom:8px">V-Code Edu — Hệ sinh thái Học lập trình dành cho Học sinh Việt Nam</h2>
          <p style="color:var(--text-secondary);max-width:720px;margin:0 auto">Sản phẩm nghiên cứu Khoa học Kỹ thuật hướng tới phổ cập tư duy lập trình Python theo Chương trình GDPT 2018, khắc phục rào cản ngôn ngữ và hạ tầng mạng cho trường học phổ thông.</p>
        </div>
        <div class="grid-3col" style="gap:16px">
          <div style="padding:18px;border-radius:12px;background:var(--bg-elevated);border:1px solid var(--border-subtle)">
            <span class="bento-tag">Đơn vị thực hiện</span>
            <h4 style="margin-bottom:6px">Trường THCS &amp; THPT Hòa Phú</h4>
            <p style="font-size:12.5px;color:var(--text-secondary)">Tổ Tin học — Phát triển và thử nghiệm thực tế trong giảng dạy môn Tin học phổ thông &amp; bồi dưỡng đội tuyển HSG.</p>
          </div>
          <div style="padding:18px;border-radius:12px;background:var(--bg-elevated);border:1px solid var(--border-subtle)">
            <span class="bento-tag">Nhóm phát triển</span>
            <h4 style="margin-bottom:6px">Nhóm Nghiên cứu V-Code Edu</h4>
            <p style="font-size:12.5px;color:var(--text-secondary)">Phụ trách thiết kế kiến trúc hệ thống, động cơ đồng bộ Python ↔ Scratch Live, trợ lý AI sư phạm và hệ thống quản lý lớp học.</p>
          </div>
          <div style="padding:18px;border-radius:12px;background:var(--bg-elevated);border:1px solid var(--border-subtle)">
            <span class="bento-tag">Nền tảng Công nghệ</span>
            <h4 style="margin-bottom:6px">Local-First PWA &amp; FastAPI</h4>
            <p style="font-size:12.5px;color:var(--text-secondary)">HTML5 / CSS3 3D / Vanilla JS Modular, FastAPI, SQLAlchemy (SQLite / PostgreSQL) và Firebase OAuth.</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer-bar" style="position:relative;z-index:2">
      <div style="max-width:1260px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div><strong>V-Code Edu</strong> — Trường THCS &amp; THPT Hòa Phú • Dự án Khoa học Kỹ thuật</div>
        <div>© 2026 V-Code Edu Team • Online &amp; Offline PWA Ready</div>
      </div>
    </footer>
  </main>

  <!-- ==================== VIEW 2: HỌC PYTHON ==================== -->
  <section id="view-learning" class="view-section">
    <div class="page-container">
      <div class="section-header"><div><span class="bento-tag">Lộ trình GDPT 2018</span><h2>Tiến trình Học tập Lập trình Python</h2></div><span id="learning-progress-text" class="badge badge-easy"></span></div>
      <div class="progress-track" style="height:11px;margin-bottom:28px"><div id="learning-progress-bar" class="progress-fill" style="width:25%"></div></div>
      <div id="learning-lessons-grid" class="grid-2col"></div>
    </div>
  </section>

  <!-- ==================== VIEW 3: IDE TỰ DO & SCRATCH LIVE ==================== -->
  <section id="view-workspace" class="view-section">
    <div class="workspace-shell">
      <aside class="pane">
        <div class="pane-header"><span>Bài học &amp; Thực hành</span><span class="badge badge-easy">Python 3</span></div>
        <div class="pane-scroll">
          <div style="padding:12px;background:var(--bg-elevated);border-radius:10px;border:1px solid var(--border-highlight);margin-bottom:14px">
            <span class="bento-tag">Đang thực hành</span><h3 id="prob-title" style="font-size:14px;margin-bottom:5px"></h3><p id="prob-desc" style="font-size:12px;color:var(--text-secondary)"></p>
          </div>
          <div id="problem-list"></div>
        </div>
      </aside>
      <section class="pane">
        <div class="pane-header">
          <div style="display:flex;align-items:center;gap:8px"><span class="mono" style="font-weight:700">main.py</span><button class="btn btn-sm" onclick="openShareModal()">🔗 QR</button><button class="btn btn-sm" onclick="downloadPythonFile()">⬇ .py</button></div>
          <div style="display:flex;gap:6px"><button class="btn btn-sm" onclick="runCodeAction()">▶ Chạy Thử</button><button class="btn btn-primary btn-sm" onclick="submitAutoGradeAction()">✓ Chấm Test Case</button></div>
        </div>
        <div id="snippet-bar" class="snippet-bar"></div>
        <div class="editor-wrapper"><div id="line-numbers" class="line-numbers">1</div><textarea id="code-editor" class="code-textarea" spellcheck="false" oninput="syncLiveEditorOutputs()"></textarea></div>
        <div style="padding:9px 14px;background:var(--bg-surface);border-top:1px solid var(--border-subtle);display:flex;align-items:center;gap:10px">
          <span class="mono" style="font-size:12px;color:var(--text-secondary)">Dữ liệu vào (stdin):</span><input id="custom-stdin" class="input-field mono" style="width:120px;padding:4px 8px" value="6" />
        </div>
      </section>
      <aside class="pane">
        <div class="pane-header">
          <div class="subtabs">
            <button class="subtab-btn active" data-rtab="scratch" onclick="switchRightTab('scratch')">🧩 Scratch Live</button>
            <button class="subtab-btn" data-rtab="ai" onclick="switchRightTab('ai')">🤖 AI &amp; Console</button>
            <button class="subtab-btn" data-rtab="flow" onclick="switchRightTab('flow')">🔀 Sơ đồ</button>
          </div>
        </div>
        <div class="pane-scroll">
          <div id="rpanel-scratch" class="right-panel active"><div id="scratch-live-stage" class="scratch-stage"></div></div>
          <div id="rpanel-ai" class="right-panel">
            <div id="console-output" class="console-box">Bấm "▶ Chạy Thử"...</div>
            <div id="ai-chat-feed" class="ai-chat-feed"><div class="chat-msg ai">👋 Gia sư V-Code Edu sẵn sàng hỗ trợ!</div></div>
            <div style="display:flex;gap:6px"><input id="ai-question-input" class="input-field" placeholder="Hỏi AI..." onkeydown="if(event.key==='Enter') sendAIChatAction()" /><button class="btn btn-sm btn-blue" onclick="sendAIChatAction()">Gửi</button></div>
          </div>
          <div id="rpanel-flow" class="right-panel"><div id="flowchart-box" style="background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:10px;padding:10px;text-align:center"></div></div>
        </div>
      </aside>
    </div>
  </section>

  <!-- ==================== VIEW 4: LỚP HỌC (CHỌN VAI TRÒ 1 LẦN + DỮ LIỆU THẬT) ==================== -->
  <section id="view-classroom" class="view-section">
    <div class="page-container">
      <!-- Yêu cầu đăng nhập -->
      <div id="classroom-login-required" class="bento-card" style="display:none;text-align:center;max-width:560px;margin:40px auto">
        <span class="bento-tag">Lớp học Trực tuyến V-Code Edu</span>
        <h2 style="margin-bottom:10px">Vui lòng Đăng nhập để vào Lớp học</h2>
        <p style="margin-bottom:20px">Hệ thống lưu trữ dữ liệu lớp học, bài tập và điểm số theo tài khoản thật của bạn.</p>
        <button class="btn btn-primary" onclick="openAuthModal('login')">🔑 Đăng nhập / Đăng ký ngay</button>
      </div>

      <!-- Chọn vai trò 1 LẦN DUY NHẤT -->
      <div id="classroom-role-once-picker" class="bento-card" style="display:none;max-width:760px;margin:20px auto;text-align:center">
        <span class="bento-tag">Thiết lập tài khoản lần đầu</span>
        <h2 style="margin-bottom:8px">Chọn vai trò của bạn trong Lớp học</h2>
        <p style="color:var(--accent-amber);font-size:13px;margin-bottom:22px">⚠️ Lưu ý: Vai trò chỉ được chọn <strong>1 lần duy nhất</strong> và sẽ khóa cố định cho tài khoản này.</p>
        <div class="grid-2col" style="text-align:left">
          <div class="bento-card" style="border-color:var(--border-highlight)">
            <div style="font-size:30px;margin-bottom:8px">👨‍🏫</div>
            <h3>Tôi là Giáo viên</h3>
            <p style="margin-bottom:16px">Tạo lớp học, chia sẻ mã ID/QR, giao bài tập tự chấm và theo dõi tiến độ học sinh trực tiếp.</p>
            <button class="btn btn-primary" style="width:100%" onclick="lockRoleOnceAction('teacher')">Đăng ký vai trò Giáo viên</button>
          </div>
          <div class="bento-card" style="border-color:var(--accent-blue)">
            <div style="font-size:30px;margin-bottom:8px">👨‍🎓</div>
            <h3>Tôi là Học sinh</h3>
            <p style="margin-bottom:16px">Nhập ID mã lớp của thầy/cô để tham gia lớp, tự làm bài tập được giao và xem điểm ngay.</p>
            <button class="btn btn-blue" style="width:100%" onclick="lockRoleOnceAction('student')">Đăng ký vai trò Học sinh</button>
          </div>
        </div>
      </div>

      <!-- CỔNG GIÁO VIÊN -->
      <div id="portal-teacher" style="display:none">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:18px">
          <div><span class="bento-tag" style="margin-bottom:2px">Cổng Giáo viên</span><h2>Quản lý Lớp học &amp; Giám sát Học sinh Thật</h2></div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn btn-primary btn-sm" onclick="document.getElementById('create-class-modal').classList.add('open')">+ Tạo lớp học mới</button>
            <button class="btn btn-blue btn-sm" onclick="openCreateAssignmentModal()">📝 Giao bài tập</button>
          </div>
        </div>
        <div id="teacher-classes-grid" class="grid-3col" style="margin-bottom:24px"></div>
        <div id="teacher-active-class-panel" class="bento-card">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px">
            <div><span class="bento-tag" style="margin-bottom:2px">Lớp đang mở</span><h3 id="teacher-selected-class-title"></h3></div>
            <div style="display:flex;align-items:center;gap:8px"><span id="teacher-selected-class-code" class="olm-code-chip"></span><button class="btn btn-sm" onclick="copyActiveClassCode()">📋 Copy Mã</button><button class="btn btn-sm btn-primary" onclick="shareActiveClassQR()">📱 QR Lớp</button></div>
          </div>
          <div class="olm-subnav">
            <button class="subtab-btn active" data-tpanel="realtime" onclick="switchTeacherSubpanel('realtime')">📡 Danh sách Học sinh &amp; Trạng thái Real-time</button>
            <button class="subtab-btn" data-tpanel="assignments" onclick="switchTeacherSubpanel('assignments')">📝 Bài tập đã giao &amp; Bảng điểm</button>
          </div>
          <div id="tpanel-realtime" class="tpanel-box">
            <div style="overflow-x:auto"><table class="data-table"><thead><tr><th>Học sinh</th><th>Bài đang làm</th><th>Trạng thái</th><th>Tiến độ</th><th>Bài làm trực tiếp</th></tr></thead><tbody id="realtime-monitor-body"></tbody></table></div>
          </div>
          <div id="tpanel-assignments" class="tpanel-box" style="display:none">
            <div id="teacher-assignments-list" style="margin-bottom:18px"></div>
            <table class="data-table"><thead><tr><th>Học sinh</th><th>Mã bài</th><th>Test đạt</th><th>Điểm</th><th>Thời gian nộp</th></tr></thead><tbody id="teacher-submissions-body"></tbody></table>
          </div>
        </div>
      </div>

      <!-- CỔNG HỌC SINH -->
      <div id="portal-student" style="display:none">
        <div class="olm-join-bar">
          <div style="flex:1;min-width:240px">
            <div style="font-weight:700;font-size:15px">🎓 Tham gia lớp học bằng ID Mã lớp</div>
            <div style="font-size:12px;color:var(--text-secondary)">Nhập mã lớp thầy/cô gửi (VD: <code>TIN10HP</code>) để vào lớp và làm bài tập.</div>
          </div>
          <div style="display:flex;gap:8px"><input id="student-join-code-input" class="input-field mono" style="width:190px;text-transform:uppercase;font-weight:700" placeholder="ID mã lớp..." /><button class="btn btn-primary" onclick="joinClassByCodeAction()">+ Vào lớp</button></div>
        </div>
        <div class="grid-2col" style="grid-template-columns:340px 1fr;align-items:start">
          <div><h3 style="font-size:16px;margin-bottom:12px">🏫 Lớp học của em</h3><div id="student-joined-classes-list"></div></div>
          <div class="bento-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
              <h3 id="student-selected-class-title">Chọn một lớp học để xem bài tập</h3>
              <span id="student-selected-class-code" class="olm-code-chip" style="display:none"></span>
            </div>
            <div id="student-assignments-list"><p style="color:var(--text-secondary)">Nhập mã lớp ở phía trên để bắt đầu!</p></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ==================== VIEW 5: TRANG IDE BÀI TẬP RIÊNG (HỌC SINH TỰ LÀM, TẮT AI/SCRATCH) ==================== -->
  <section id="view-assignment-ide" class="view-section">
    <div class="exam-ide-shell">
      <aside class="pane">
        <div class="pane-header"><button class="btn btn-sm" onclick="switchView('classroom')">← Quay lại Lớp</button><span id="exam-class-badge" class="badge badge-blue"></span></div>
        <div class="pane-scroll">
          <span class="bento-tag">Chế độ Tự Thực Hiện (Không AI • Không Code mẫu)</span>
          <h3 id="exam-title" style="font-size:16px;margin-bottom:10px"></h3>
          <p id="exam-desc" style="font-size:13.5px;color:var(--text-secondary);line-height:1.7"></p>
          <div style="margin-top:18px;padding:12px;border-radius:10px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.35);font-size:12px;color:var(--accent-amber)">
            🔒 Trợ lý AI, Scratch Live và thanh gợi ý cú pháp đã được tạm khóa để em tự rèn luyện tư duy lập trình.
          </div>
        </div>
      </aside>
      <section class="pane">
        <div class="pane-header">
          <span class="mono" style="font-weight:700">bai_lam_cua_em.py</span>
          <div style="display:flex;gap:8px"><button class="btn btn-sm" onclick="runExamCodeAction()">▶ Chạy Thử</button><button class="btn btn-primary btn-sm" onclick="submitExamCodeAction()">✓ Nộp Bài Chấm Điểm</button></div>
        </div>
        <div class="editor-wrapper"><div id="exam-line-numbers" class="line-numbers">1</div><textarea id="exam-editor" class="code-textarea" spellcheck="false" oninput="syncExamEditor()"></textarea></div>
        <div style="padding:9px 14px;background:var(--bg-surface);border-top:1px solid var(--border-subtle);display:flex;align-items:center;gap:10px">
          <span class="mono" style="font-size:12px">Dữ liệu thử (stdin):</span><input id="exam-stdin" class="input-field mono" style="width:130px;padding:4px 8px" value="6" />
        </div>
      </section>
      <aside class="pane">
        <div class="pane-header"><span>Kết quả Chạy &amp; Chấm điểm</span></div>
        <div class="pane-scroll"><div id="exam-console" class="console-box" style="min-height:260px">Bấm "▶ Chạy Thử" hoặc "✓ Nộp Bài Chấm Điểm"...</div></div>
      </aside>
    </div>
  </section>

  <!-- ==================== VIEW 6: THỬ THÁCH CHẶNG GIẢI TRÍ (THAY ĐẤU TRƯỜNG) ==================== -->
  <section id="view-challenges" class="view-section">
    <div class="page-container">
      <div class="section-header">
        <div><span class="bento-tag">Giải trí &amp; Rèn luyện Tư duy</span><h2>Bản đồ Thử thách Lập trình Python theo Chặng</h2></div>
        <span id="challenge-progress-text" class="badge badge-easy"></span>
      </div>
      <div class="progress-track" style="height:11px;margin-bottom:28px"><div id="challenge-progress-bar" class="progress-fill" style="width:0%"></div></div>
      <div id="challenges-stages-grid" class="grid-3col"></div>
    </div>
  </section>

  <!-- ==================== VIEW 7: TRANG QUẢN LÝ TÀI KHOẢN AN TOÀN ==================== -->
  <section id="view-account" class="view-section">
    <div class="page-container" style="max-width:920px">
      <div class="section-header">
        <div><span class="bento-tag">Bảo mật &amp; Cá nhân hóa</span><h2>Quản lý Tài khoản V-Code Edu</h2></div>
        <button class="btn btn-sm" style="border-color:var(--accent-rose);color:var(--accent-rose)" onclick="logoutAction()">🚪 Đăng xuất</button>
      </div>
      <div class="grid-2col">
        <div class="bento-card">
          <h3 style="margin-bottom:14px">Thông tin cá nhân &amp; Ảnh đại diện</h3>
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:18px">
            <div id="acc-avatar-preview"></div>
            <div>
              <div style="margin-bottom:6px"><span id="acc-role-badge" class="badge badge-easy"></span></div>
              <label class="btn btn-sm" style="cursor:pointer">📷 Đổi ảnh đại diện<input type="file" accept="image/*" style="display:none" onchange="handleAvatarFileUpload(event)" /></label>
            </div>
          </div>
          <form onsubmit="saveAccountProfileAction(event)">
            <div class="auth-field"><label>Họ và tên</label><input id="acc-fullname" class="input-field" required /></div>
            <div class="auth-field"><label>Email (Không thể thay đổi)</label><input id="acc-email" class="input-field" readonly style="opacity:0.7" /></div>
            <div class="auth-field"><label>Trường học</label><input id="acc-school" class="input-field" /></div>
            <div class="auth-field"><label>Lớp / Đơn vị</label><input id="acc-class" class="input-field" /></div>
            <button type="submit" class="btn btn-primary" style="width:100%">💾 Lưu thay đổi hồ sơ</button>
          </form>
        </div>

        <div class="bento-card">
          <h3 style="margin-bottom:14px">🔐 Đổi mật khẩu &amp; An toàn tài khoản</h3>
          <form onsubmit="handleChangePasswordSubmit(event)">
            <div class="auth-field"><label>Mật khẩu hiện tại</label><input id="acc-old-pass" type="password" class="input-field" required placeholder="Nhập mật khẩu cũ..." /></div>
            <div class="auth-field"><label>Mật khẩu mới (tối thiểu 6 ký tự)</label><input id="acc-new-pass" type="password" class="input-field" required minlength="6" placeholder="Nhập mật khẩu mới..." /></div>
            <div class="auth-field"><label>Xác nhận mật khẩu mới</label><input id="acc-confirm-pass" type="password" class="input-field" required minlength="6" placeholder="Nhập lại mật khẩu mới..." /></div>
            <button type="submit" class="btn btn-blue" style="width:100%">🔑 Cập nhật Mật khẩu</button>
          </form>
        </div>
      </div>
    </div>
  </section>

  <!-- ==================== MODALS ==================== -->
  <div id="auth-modal" class="modal-overlay">
    <div class="modal-box auth-modal-pro">
      <button class="modal-close" onclick="closeModal('auth-modal')">✕</button>
      <div class="auth-header-brand"><div class="brand-mark">V</div><h2 id="auth-heading">Đăng nhập V-Code Edu</h2><p id="auth-subheading"></p></div>
      <div class="social-auth-grid">
        <button type="button" class="social-btn" onclick="handleRealSocialLogin('google')"><span>Google</span></button>
        <button type="button" class="social-btn" onclick="handleRealSocialLogin('facebook')"><span>Facebook</span></button>
        <button type="button" class="social-btn" onclick="handleRealSocialLogin('github')"><span>GitHub</span></button>
      </div>
      <div class="auth-divider">hoặc tiếp tục bằng Email</div>
      <form id="auth-login-form" onsubmit="handleLoginSubmit(event)">
        <div class="auth-field"><label>Email</label><input id="login-identifier" class="input-field" required placeholder="nhapemail@gmail.com" /></div>
        <div class="auth-field"><label>Mật khẩu</label><div class="password-wrap"><input id="login-password" type="password" class="input-field" required /><button type="button" class="password-toggle" onclick="togglePassVis('login-password')">👁</button></div></div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:11px">Đăng nhập ngay</button>
        <div class="auth-switch-footer">Chưa có tài khoản? <button type="button" onclick="switchAuthTab('register')">Đăng ký tài khoản →</button></div>
      </form>
      <form id="auth-register-form" style="display:none" onsubmit="handleRegisterSubmit(event)">
        <div class="auth-field"><label>Họ và tên</label><input id="reg-fullname" class="input-field" required /></div>
        <div class="auth-field"><label>Email</label><input id="reg-email" type="email" class="input-field" required /></div>
        <div class="auth-field"><label>Mật khẩu</label><div class="password-wrap"><input id="reg-password" type="password" class="input-field" required minlength="6" /><button type="button" class="password-toggle" onclick="togglePassVis('reg-password')">👁</button></div></div>
        <button type="submit" class="btn btn-primary" style="width:100%;padding:11px">Tạo tài khoản miễn phí</button>
        <div class="auth-switch-footer">Đã có tài khoản? <button type="button" onclick="switchAuthTab('login')">Quay lại Đăng nhập</button></div>
      </form>
    </div>
  </div>

  <!-- MODAL CẤU HÌNH FIREBASE OAUTH THẬT -->
  <div id="oauth-config-modal" class="modal-overlay">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal('oauth-config-modal')">✕</button>
      <span class="bento-tag">Kích hoạt Đăng nhập thật Google / Facebook / GitHub</span>
      <h3 style="margin-bottom:8px">Kết nối Firebase Authentication</h3>
      <p style="font-size:12.5px;color:var(--text-secondary);margin-bottom:12px">Dán thông số từ Firebase Console (Project Settings → Web App) để bật cửa sổ đăng nhập Google/Facebook/GitHub chính thức:</p>
      <div class="auth-field"><label>Firebase apiKey</label><input id="fb-api-key" class="input-field mono" placeholder="AIzaSy..." /></div>
      <div class="auth-field"><label>Firebase authDomain</label><input id="fb-auth-domain" class="input-field mono" placeholder="vcode-edu.firebaseapp.com" /></div>
      <div class="auth-field"><label>Firebase projectId</label><input id="fb-project-id" class="input-field mono" placeholder="vcode-edu" /></div>
      <button class="btn btn-primary" style="width:100%" onclick="saveOAuthConfig()">Lưu &amp; Kích hoạt OAuth thật</button>
    </div>
  </div>

  <div id="create-class-modal" class="modal-overlay"><div class="modal-box"><button class="modal-close" onclick="closeModal('create-class-modal')">✕</button><h3>Tạo Lớp học Mới</h3><form onsubmit="handleCreateClassSubmit(event)" style="margin-top:12px"><div class="auth-field"><label>Tên lớp *</label><input id="new-class-name" class="input-field" required /></div><div class="grid-2col" style="gap:10px;margin-bottom:10px"><div><label style="font-size:12px">Môn/Khối</label><input id="new-class-subject" class="input-field" value="Tin học THPT • Python" /></div><div><label style="font-size:12px">ID Mã lớp (tự tạo nếu trống)</label><input id="new-class-code" class="input-field mono" /></div></div><div class="auth-field"><label>Mô tả</label><input id="new-class-desc" class="input-field" /></div><button type="submit" class="btn btn-primary" style="width:100%">+ Tạo lớp ngay</button></form></div></div>
  <div id="create-assignment-modal" class="modal-overlay"><div class="modal-box" style="max-width:520px"><button class="modal-close" onclick="closeModal('create-assignment-modal')">✕</button><h3>Giao Bài Tập Lớp <span id="assign-target-class" style="color:var(--accent-emerald)"></span></h3><form onsubmit="handleCreateAssignmentSubmit(event)" style="margin-top:12px"><div class="auth-field"><label>Tên bài *</label><input id="assign-title" class="input-field" required /></div><div class="auth-field"><label>Đề bài *</label><input id="assign-desc" class="input-field" required /></div><div class="grid-2col" style="gap:10px;margin-bottom:10px"><div><label style="font-size:12px">Mức độ</label><select id="assign-diff" class="select-field"><option>Cơ bản</option><option>Trung bình</option><option>Nâng cao</option></select></div><div><label style="font-size:12px">Hạn nộp</label><input id="assign-due" class="input-field" value="Cuối tuần" /></div></div><div class="grid-2col" style="gap:10px;margin-bottom:10px"><div><label style="font-size:12px">Test Input *</label><input id="assign-in" class="input-field mono" required value="6" /></div><div><label style="font-size:12px">Expected Output *</label><input id="assign-out" class="input-field mono" required value="12" /></div></div><div class="auth-field"><label>Khung code ban đầu</label><textarea id="assign-starter" class="input-field mono" rows="3"># Học sinh tự viết mã nguồn bên dưới&#10;</textarea></div><button type="submit" class="btn btn-primary" style="width:100%">✓ Giao bài ngay</button></form></div></div>
  <div id="share-modal" class="modal-overlay"><div class="modal-box" style="text-align:center"><button class="modal-close" onclick="closeModal('share-modal')">✕</button><h3>Chia sẻ Link &amp; Mã QR</h3><div id="qr-code-box" style="background:#FFF;padding:14px;border-radius:12px;display:inline-block;margin:12px 0"></div><div style="display:flex;gap:8px"><input id="share-link-input" class="input-field mono" readonly /><button class="btn btn-primary btn-sm" onclick="copyShareLink()">Copy</button></div></div></div>
  <div id="peek-modal" class="modal-overlay"><div class="modal-box"><button class="modal-close" onclick="closeModal('peek-modal')">✕</button><h3 id="peek-student-name"></h3><p id="peek-student-problem" style="font-size:12px;color:var(--text-secondary);margin-bottom:8px"></p><pre id="peek-code-preview" class="console-box" style="max-height:220px"></pre><div style="display:flex;gap:8px"><input id="teacher-hint-input" class="input-field" placeholder="Gửi nhận xét trực tiếp..." /><button class="btn btn-primary btn-sm" onclick="sendTeacherHintAction()">Gửi</button></div></div></div>
  <div id="ai-config-modal" class="modal-overlay"><div class="modal-box"><button class="modal-close" onclick="closeModal('ai-config-modal')">✕</button><h3>Cấu hình AI &amp; Backend</h3><div class="auth-field" style="margin-top:10px"><label>Backend URL</label><input id="cfg-backend-url" class="input-field mono" value="http://localhost:8000" /></div><div class="auth-field"><label>Gemini API Key</label><input id="cfg-gemini-key" type="password" class="input-field mono" /></div><button class="btn btn-primary" style="width:100%" onclick="saveAIConfig()">Lưu</button></div></div>

  <div id="toast-banner" class="toast-banner"></div>

  <script src="js/lessons-data.js"></script>
  <script src="js/offline-db.js"></script>
  <script src="js/firebase-auth.js"></script>
  <script src="js/three-hero.js"></script>
  <script src="js/scratch-bridge.js"></script>
  <script src="js/ide-engine.js"></script>
  <script src="js/ai-tutor.js"></script>
  <script src="js/realtime-monitor.js"></script>
  <script src="js/app.js"></script>
  <script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});</script>
</body>
</html>
"""

def apply_v6():
    for rel, content in BACKEND_FILES.items():
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✔ Đã cập nhật Backend: {rel}")

    for rel, content in FRONTEND_JS_FILES.items():
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✔ Đã cập nhật JS: {rel}")

    with open("js/app.js", "w", encoding="utf-8") as f:
        f.write(APP_JS_V6.strip() + "\n")
    print("✔ Đã cập nhật: js/app.js")

    css_path = "css/design-system.css"
    old_css = open(css_path, "r", encoding="utf-8").read() if os.path.exists(css_path) else ""
    marker = "/* ==================== V6: THEME BTN, AVATAR, CHALLENGES & EXAM IDE ==================== */"
    if marker in old_css:
        old_css = old_css.split(marker)[0].rstrip()
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(old_css + "\n\n" + EXTRA_V6_CSS.strip() + "\n")
    print("✔ Đã cập nhật: css/design-system.css")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(INDEX_HTML_V6.strip() + "\n")
    print("✔ Đã cập nhật: index.html")

    print("\n--- LÀM SẠCH DỮ LIỆU MÔ PHỎNG & KHỞI TẠO CSDL THẬT ---")
    subprocess.run([sys.executable, "-m", "backend.database.init_db"], check=True)
    print("\n🎉 HOÀN TẤT NÂNG CẤP V-CODE EDU v6.0!")

if __name__ == "__main__":
    apply_v6()