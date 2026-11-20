from datetime import datetime
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
