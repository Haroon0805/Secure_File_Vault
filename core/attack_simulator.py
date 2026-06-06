# attack_simulator.py
import os
import time
import hashlib
from security import (
    calculate_entropy, password_strength,
    password_suggestions, estimate_crack_time,
    log_action
)

WORDLIST_PATH = "wordlist.txt"

def simulate_attack(test_password: str) -> str:
    if not test_password:
        return "No password provided for simulation"

    entropy = calculate_entropy(test_password)
    strength, _ = password_strength(entropy)
    suggestions = password_suggestions(test_password)
    crack_time = estimate_crack_time(test_password)

    sha_hash = hashlib.sha256(test_password.encode()).hexdigest()

    output = f"Password Analysis:\n"
    output += f"Length: {len(test_password)} characters\n"
    output += f"Entropy: {entropy:.2f} bits\n"
    output += f"Strength: {strength}\n"
    output += f"Estimated brute-force crack time: {crack_time}\n\n"
    output += "Improvement Suggestions:\n"
    output += "\n".join(suggestions) if suggestions else "No major improvements needed — strong password!\n"
    output += "\n"

    if not os.path.exists(WORDLIST_PATH):
        output += "wordlist.txt not found — dictionary simulation skipped\n"
    else:
        output += "Dictionary Attack Simulation (using wordlist.txt):\n"
        found = False
        attempts = 0
        start = time.time()
        with open(WORDLIST_PATH, encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if not word: continue
                attempts += 1
                if hashlib.sha256(word.encode()).hexdigest() == sha_hash:
                    found = True
                    break
                if attempts % 10000 == 0:
                    time.sleep(0.005)  # slow for visibility

        duration = time.time() - start
        if found:
            output += f"→ Password cracked via dictionary!\n"
            output += f"Matched word: {word}\n"
            output += f"Attempts: {attempts:,}\n"
            output += f"Time taken: {duration:.2f} seconds\n"
        else:
            output += f"→ Not found in dictionary after {attempts:,} attempts\n"
            output += f"Time taken: {duration:.2f} seconds\n"

    return output