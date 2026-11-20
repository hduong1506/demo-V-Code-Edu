from pydantic import BaseModel

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
