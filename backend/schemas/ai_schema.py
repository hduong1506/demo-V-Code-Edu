from pydantic import BaseModel

class AIChatSchema(BaseModel):
    question: str
    code: str = ""
    error_message: str = ""
    api_key: str = ""
