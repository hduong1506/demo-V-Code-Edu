import re
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
