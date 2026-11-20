import hashlib
import hmac
import secrets
import base64

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"{salt}${base64.b64encode(dk).decode('ascii')}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, encoded = stored_hash.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
        return hmac.compare_digest(base64.b64encode(dk).decode("ascii"), encoded)
    except Exception:
        return False

def create_session_token(username: str, role: str) -> str:
    raw = f"{username}:{role}:{secrets.token_hex(16)}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
