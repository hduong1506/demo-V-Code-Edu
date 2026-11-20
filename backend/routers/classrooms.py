import json
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
