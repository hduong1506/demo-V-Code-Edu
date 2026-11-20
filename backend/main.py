"""
V-CODE EDU — FASTAPI BACKEND SERVER (FULL DATABASE INTEGRATION)
Chạy trong Terminal VS Code:
    uvicorn backend.main:app --reload --port 8000
"""
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.init_db import init_database
from backend.routers import auth, classrooms, assessment, monitor, ai, sync

app = FastAPI(
    title="V-Code Edu API",
    description="Hệ thống API & Cơ sở dữ liệu cho nền tảng Học lập trình Python & Scratch Live Việt Nam",
    version="5.1.0"
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
    return {"status": "ok", "service": "V-Code Edu FastAPI + Database", "timestamp": int(time.time())}

app.include_router(auth.router)
app.include_router(classrooms.router)
app.include_router(assessment.router)
app.include_router(monitor.router)
app.include_router(ai.router)
app.include_router(sync.router)
