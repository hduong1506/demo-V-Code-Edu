from pydantic import BaseModel

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
