import os
import json
import urllib.request

def offline_socratic_reply(question: str, code: str = "", error_msg: str = "") -> dict:
    q = (question or "").lower()
    err = error_msg or ""

    if "SyntaxError" in err:
        return {"mode": "offline", "reply": "Lỗi Cú Pháp (SyntaxError): Kiểm tra dấu hai chấm ':' cuối lệnh if/elif/else/for/while hoặc dấu ngoặc đơn bị thiếu."}
    if "IndentationError" in err:
        return {"mode": "offline", "reply": "Lỗi Thụt Lề (IndentationError): Các dòng cùng khối lệnh trong Python phải thụt lề đều 4 dấu cách (1 Tab)."}
    if "ZeroDivisionError" in err:
        return {"mode": "offline", "reply": "Lỗi Chia Cho 0 (ZeroDivisionError): Cần kiểm tra mẫu số khác 0 trước khi chia."}
    if "số nguyên tố" in q or "nguyen to" in q:
        return {"mode": "offline", "reply": "Gợi ý Socratic: Số nguyên tố là số > 1 chỉ chia hết cho 1 và chính nó. Em hãy thử duyệt i từ 2 đến n-1 và kiểm tra n % i == 0."}
    if "for" in q or "vòng lặp" in q:
        return {"mode": "offline", "reply": "Vòng lặp for chuẩn: 'for i in range(1, n + 1):' sẽ duyệt từ 1 tới n. Lưu ý thụt lề 4 dấu cách ở các dòng bên trong."}
    return {
        "mode": "offline",
        "reply": f"Trợ lý V-Code Edu (Offline): Mã nguồn hiện có {len(code.splitlines())} dòng. Hãy kiểm tra đủ 3 bước: (1) Đọc dữ liệu int(input()), (2) Xử lý logic, (3) In kết quả print()."
    }

def ask_ai_hybrid(question: str, code: str = "", error_msg: str = "", api_key_override: str = "") -> dict:
    api_key = (api_key_override or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        return offline_socratic_reply(question, code, error_msg)

    prompt = (
        "Bạn là Gia sư Lập trình Tiếng Việt của V-Code Edu dành cho học sinh phổ thông Việt Nam. "
        "Hãy trả lời ngắn gọn, thân thiện, gợi mở tư duy Socratic thay vì làm hộ hoàn toàn.\n"
        f"Câu hỏi: {question}\nMã nguồn:\n```python\n{code}\n```\nLỗi (nếu có): {error_msg}"
    )
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"mode": "online-gemini", "reply": text}
    except Exception:
        fb = offline_socratic_reply(question, code, error_msg)
        fb["note"] = "API trực tuyến không khả dụng, đã tự động chuyển sang chế độ AI Offline."
        return fb
