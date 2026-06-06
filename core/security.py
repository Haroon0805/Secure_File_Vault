# security.py
import math
import re
import base64
import os
from datetime import datetime
from cryptography.fernet import Fernet
import bcrypt
import pyotp
import qrcode
from io import BytesIO

from ttkbootstrap.constants import DANGER, WARNING, INFO, SUCCESS


def calculate_entropy(password: str) -> float:
    if not password:
        return 0.0
    pool = 0
    if re.search(r'[a-z]', password): pool += 26
    if re.search(r'[A-Z]', password): pool += 26
    if re.search(r'[0-9]', password): pool += 10
    if re.search(r'[^a-zA-Z0-9]', password): pool += 32
    return round(len(password) * math.log2(pool) if pool > 0 else 0, 2)


def password_strength(entropy: float) -> tuple[str, str]:
    if entropy < 28:   return "Very Weak", DANGER
    if entropy < 40:   return "Weak", WARNING
    if entropy < 60:   return "Moderate", INFO
    return "Strong", SUCCESS


def password_suggestions(password: str) -> list[str]:
    tips = []
    if len(password) < 12:
        tips.append("Use at least 12–16 characters")
    if not re.search(r'[A-Z]', password):
        tips.append("Add uppercase letters")
    if not re.search(r'[a-z]', password):
        tips.append("Add lowercase letters")
    if not re.search(r'[0-9]', password):
        tips.append("Add numbers")
    if not re.search(r'[^a-zA-Z0-9]', password):
        tips.append("Add special characters")
    if re.search(r'(.)\1{2,}', password):
        tips.append("Avoid repeated characters (aaa, 111…)")

    return tips if tips else ["Good password — follows recommended practices"]


def estimate_crack_time(password: str) -> str:
    if not password:
        return "N/A"
    entropy = calculate_entropy(password)
    seconds = 2 ** entropy / 10_000_000_000  # 10 billion attempts/sec
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    mins = seconds / 60
    if mins < 60:
        return f"{mins:.1f} minutes"
    hours = mins / 60
    if hours < 24:
        return f"{hours:.1f} hours"
    days = hours / 24
    if days < 365:
        return f"{days:.1f} days"
    years = days / 365
    return f"{years:.1e} years" if years > 1000 else f"{years:.1f} years"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_encryption_key() -> str:
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode('utf-8')


def get_fernet(key_b64: str) -> Fernet:
    return Fernet(base64.urlsafe_b64decode(key_b64))


def encrypt_bytes(data: bytes, key_b64: str) -> bytes:
    return get_fernet(key_b64).encrypt(data)


def decrypt_bytes(encrypted: bytes, key_b64: str) -> bytes:
    return get_fernet(key_b64).decrypt(encrypted)


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp(secret: str) -> pyotp.TOTP:
    return pyotp.TOTP(secret)


def verify_totp(secret: str, token: str, window: int = 2) -> bool:
    """
    Verify TOTP token with tolerance for time drift

    Args:
        secret: The TOTP secret key
        token: The 6-digit code to verify
        window: Number of time steps to check (default 2 = ±60 seconds)

    Returns:
        True if valid, False otherwise
    """
    return get_totp(secret).verify(token, valid_window=window)


def generate_qr_for_totp(secret: str, username: str, issuer: str = "Secure Vault") -> str:
    uri = get_totp(secret).provisioning_uri(name=username, issuer_name=issuer)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"


def log_action(username: str, action: str, log_file="logs.txt"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {username} {action}\n"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line)
    except:
        pass