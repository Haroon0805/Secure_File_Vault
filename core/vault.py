# vault.py
import os
from tkinter import filedialog
from security import encrypt_bytes, decrypt_bytes, log_action

VAULT_DIR = "vault_storage"

def get_user_vault_path(username: str) -> str:
    path = os.path.join(VAULT_DIR, username)
    os.makedirs(path, exist_ok=True)
    return path


def add_file(username: str, key_b64: str) -> tuple[bool, str]:
    vault_path = get_user_vault_path(username)
    file_path = filedialog.askopenfilename(title="Select file to secure")
    if not file_path:
        return False, "No file selected"

    filename = os.path.basename(file_path)
    safe_name = filename.replace(" ", "_")

    try:
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = encrypt_bytes(data, key_b64)
        dest = os.path.join(vault_path, safe_name + ".enc")
        with open(dest, "wb") as f:
            f.write(encrypted)
        log_action(username, f"added file {safe_name}")
        return True, f"File '{filename}' secured successfully"
    except Exception as e:
        return False, f"Error securing file: {str(e)}"


def list_files(username: str) -> list[str]:
    vault_path = get_user_vault_path(username)
    files = [f for f in os.listdir(vault_path) if f.endswith(".enc")]
    return [f[:-4] for f in files]


def get_file_content(username: str, filename: str, key_b64: str) -> tuple[bool, bytes | str]:
    vault_path = get_user_vault_path(username)
    enc_path = os.path.join(vault_path, filename + ".enc")
    if not os.path.exists(enc_path):
        return False, "File not found"
    try:
        with open(enc_path, "rb") as f:
            encrypted = f.read()
        decrypted = decrypt_bytes(encrypted, key_b64)
        return True, decrypted
    except Exception as e:
        return False, f"Decryption failed: {str(e)}"


def delete_file(username: str, filename: str) -> tuple[bool, str]:
    vault_path = get_user_vault_path(username)
    enc_path = os.path.join(vault_path, filename + ".enc")
    if not os.path.exists(enc_path):
        return False, "File not found"
    try:
        os.remove(enc_path)
        log_action(username, f"deleted file {filename}")
        return True, "File deleted"
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"