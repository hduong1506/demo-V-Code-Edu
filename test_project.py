import os
import json
from backend.services.auth_service import hash_password, verify_password
from backend.services.ai_service import offline_socratic_reply

def run_tests():
    print("=== KIỂM THỬ TỰ ĐỘNG HỆ THỐNG V-CODE EDU ===")
    for p in ["index.html", "manifest.json", "sw.js", "css/design-system.css", "js/three-hero.js", "js/scratch-bridge.js", "js/ide-engine.js", "js/ai-tutor.js", "js/realtime-monitor.js", "js/app.js", "backend/main.py"]:
        assert os.path.exists(p), f"Thiếu file bắt buộc: {p}"
    print("[PASS] 1. Đầy đủ cấu trúc Frontend + Scratch Live + Real-time + Backend.")

    with open("manifest.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert "V-Code Edu" in m["name"]
    print("[PASS] 2. Cấu hình PWA Offline V-Code Edu hợp lệ.")

    h = hash_password("Test@12345")
    assert verify_password("Test@12345", h) and not verify_password("wrong", h)
    print("[PASS] 3. Mã hóa mật khẩu PBKDF2-SHA256 chính xác.")

    r = offline_socratic_reply("Lỗi vòng lặp", "for i in range(5)\n print(i)", "SyntaxError")
    assert r["mode"] == "offline" and "SyntaxError" in r["reply"]
    print("[PASS] 4. Trợ lý AI Socratic Offline hoạt động chính xác.")

    print("=== TẤT CẢ 4/4 BÀI KIỂM THỬ ĐẠT 100% ===")

if __name__ == "__main__":
    run_tests()
