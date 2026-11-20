import json
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
        starter_code=payload.get("starter_code") or "n = int(input())\nprint(n)",
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
