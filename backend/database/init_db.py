import json
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
                starter_code="# Học sinh tự viết mã nguồn giải bài toán bên dưới\n",
                test_cases_json=json.dumps([{"input": "6", "expected": "12"}, {"input": "10", "expected": "30"}]),
                created_by="giaovien"
            ))
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_database(reset_schema=True)
    print("✔ Đã làm sạch học sinh mô phỏng & khởi tạo CSDL thật vcode_edu.db!")
