# authentication.py
import json
import os
import time
from datetime import datetime
from security import (
    hash_password, verify_password,
    calculate_entropy, password_strength,
    password_suggestions, generate_encryption_key,
    generate_totp_secret, verify_totp,
    log_action
)

USERS_FILE = "users.json"
LOCKOUT_MINUTES = 15
MAX_ATTEMPTS = 5


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def register(username: str, password: str) -> tuple[bool, str]:
    users = load_users()
    if username in users:
        return False, "Username already exists"

    entropy = calculate_entropy(password)
    strength, _ = password_strength(entropy)

    if entropy < 30:
        return False, f"Password too weak ({strength}, {entropy:.1f} bits)\n" + "\n".join(
            password_suggestions(password))

    hashed = hash_password(password)
    key_b64 = generate_encryption_key()

    users[username] = {
        "password": hashed,
        "failed_attempts": 0,
        "lock_until": 0,
        "encryption_key": key_b64,
        "totp_enabled": False,
        "created": datetime.now().isoformat()
    }

    save_users(users)
    log_action(username, "registered")
    return True, "Registration successful"


def login(username: str, password: str, totp_code: str | None = None) -> tuple[bool, str, dict | None, bool]:
    users = load_users()
    if username not in users:
        return False, "User not found", None, False

    user = users[username]
    now = time.time()

    if user["lock_until"] > now:
        remaining = int(user["lock_until"] - now)
        return False, f"Account locked — try again in {remaining // 60} min", None, False

    # If password is provided, verify it first
    if password:
        if not verify_password(password, user["password"]):
            user["failed_attempts"] += 1
            if user["failed_attempts"] >= MAX_ATTEMPTS:
                user["lock_until"] = now + (LOCKOUT_MINUTES * 60)
                msg = f"Too many failed attempts — locked for {LOCKOUT_MINUTES} minutes"
                log_action(username, "account locked")
            else:
                msg = f"Invalid password ({user['failed_attempts']}/{MAX_ATTEMPTS})"
            save_users(users)
            log_action(username, f"failed login attempt")
            return False, msg, None, False

        user["failed_attempts"] = 0

        # Password is correct - check if 2FA is needed
        if user.get("totp_enabled", False):
            if totp_code is None:
                save_users(users)
                return False, "Enter your 2FA code", None, True
        else:
            # No 2FA - login successful
            user["lock_until"] = 0
            save_users(users)
            log_action(username, "login success (no 2FA)")
            return True, "Login successful", user, False

    # If we get here, verify TOTP (called with empty password after password was already verified)
    if user.get("totp_enabled", False) and totp_code:
        # DEBUG: Print what we're verifying
        print(f"\n{'=' * 60}")
        print(f"DEBUG: 2FA Verification")
        print(f"{'=' * 60}")
        print(f"Username: {username}")
        print(f"Secret: {user['totp_secret']}")
        print(f"Code entered: {totp_code}")
        print(f"Code type: {type(totp_code)}")
        print(f"Code length: {len(totp_code)}")

        # Try verification
        result = verify_totp(user["totp_secret"], totp_code, window=2)
        print(f"Verification result: {result}")

        # Also try with window=10 to see if it's a time issue
        result_wide = verify_totp(user["totp_secret"], totp_code, window=10)
        print(f"Verification with window=10: {result_wide}")
        print(f"{'=' * 60}\n")

        if result:
            user["lock_until"] = 0
            save_users(users)
            log_action(username, "login success with 2FA")
            return True, "Login successful", user, False
        else:
            save_users(users)
            return False, "Invalid 2FA code", None, True

    return False, "Invalid login attempt", None, False


def enable_2fa(username: str) -> tuple[bool, str, str | None]:
    users = load_users()
    if username not in users:
        return False, "User not found", None

    if users[username].get("totp_enabled", False):
        return False, "2FA already enabled", None

    secret = generate_totp_secret()
    users[username]["totp_secret"] = secret
    users[username]["totp_enabled"] = True
    save_users(users)
    log_action(username, "enabled 2FA")
    return True, "2FA enabled – scan QR code", secret


def disable_2fa(username: str) -> tuple[bool, str]:
    users = load_users()
    if username not in users:
        return False, "User not found"

    if not users[username].get("totp_enabled", False):
        return False, "2FA not enabled"

    users[username].pop("totp_secret", None)
    users[username]["totp_enabled"] = False
    save_users(users)
    log_action(username, "disabled 2FA")
    return True, "2FA disabled"


def reset_password(username: str, new_password: str, totp_code: str | None = None) -> tuple[bool, str, bool]:
    """
    Reset password with 2FA verification if enabled

    Returns: (success, message, needs_totp)
    """
    users = load_users()
    if username not in users:
        return False, "User not found", False

    user = users[username]

    # If user has 2FA enabled, require TOTP verification
    if user.get("totp_enabled", False):
        if totp_code is None:
            return False, "2FA verification required", True

        # Verify TOTP code
        if not verify_totp(user["totp_secret"], totp_code, window=2):
            log_action(username, "failed password reset (invalid 2FA)")
            return False, "Invalid 2FA code", True

    # Validate new password strength
    entropy = calculate_entropy(new_password)
    strength, _ = password_strength(entropy)

    if entropy < 30:
        return False, f"New password too weak ({strength}, {entropy:.1f} bits)\n" + "\n".join(
            password_suggestions(new_password)), user.get("totp_enabled", False)

    # Reset password
    hashed = hash_password(new_password)
    users[username]["password"] = hashed
    users[username]["failed_attempts"] = 0
    users[username]["lock_until"] = 0
    save_users(users)
    log_action(username, "password reset successful")
    return True, "Password reset successful", False


def delete_user(username: str) -> tuple[bool, str]:
    users = load_users()
    if username not in users:
        return False, "User not found"

    del users[username]
    save_users(users)
    log_action("system", f"deleted user {username}")
    return True, "User deleted successfully"