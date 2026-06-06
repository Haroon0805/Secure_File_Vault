# gui_register.py
# User Registration with Mandatory 2FA

import tkinter as tk
from tkinter import messagebox, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import register, enable_2fa
from security import (
    calculate_entropy, password_strength, password_suggestions,
    generate_qr_for_totp, verify_totp
)
from gui_config import ensure_background_behind, create_form_frame
from PIL import Image, ImageTk
import base64
from io import BytesIO


# Global state for registration
register_state = {"stage": "credentials", "username": None, "password": None, "totp_secret": None}


def show_register(root, clear_frame_func, show_main_menu_func):
    """Display registration with mandatory 2FA - multi-stage"""
    clear_frame_func()
    root.title("Register - Secure Vault")

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=30)
    main_frame.pack(expand=True, pady=50)

    if register_state["stage"] == "credentials":
        # Stage 1: Username & Password
        ttkb.Label(main_frame, text="Create New Account", 
                  font=("Helvetica", 24, "bold"), bootstyle=SUCCESS).pack(pady=(0, 30))
        
        ttkb.Label(main_frame, text="📌 Note: 2FA is mandatory for all accounts", 
                  font=("Helvetica", 11), bootstyle=WARNING).pack(pady=(0, 20))

        ttkb.Label(main_frame, text="Username", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20)
        e_user = ttkb.Entry(main_frame, width=50, bootstyle=INFO, font=("Helvetica", 11))
        e_user.pack(pady=(5, 15), padx=20, fill="x")

        ttkb.Label(main_frame, text="Password", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20)
        pass_frame = ttkb.Frame(main_frame)
        pass_frame.pack(fill="x", pady=(5, 10), padx=20)
        e_pass = ttkb.Entry(pass_frame, show="*", font=("Helvetica", 11))
        e_pass.pack(side="left", fill="x", expand=True)
        show_var = tk.BooleanVar()
        ttkb.Checkbutton(pass_frame, text="Show", variable=show_var,
                        command=lambda: e_pass.config(show="" if show_var.get() else "*"),
                        bootstyle=INFO).pack(side="right", padx=10)

        # Strength meter
        strength_frame = ttkb.Frame(main_frame)
        strength_frame.pack(pady=10)
        
        strength_label = ttkb.Label(strength_frame, text="Strength: N/A", 
                                    font=("Helvetica", 12, "bold"))
        strength_label.pack()

        suggestions_text = scrolledtext.ScrolledText(main_frame, height=4, width=60,
                                                    font=("Courier", 9), wrap=tk.WORD)
        suggestions_text.pack(pady=10, padx=20)
        suggestions_text.insert(tk.END, "Start typing your password...")
        suggestions_text.config(state=tk.DISABLED)

        def update_strength(event=None):
            pwd = e_pass.get()
            entropy = calculate_entropy(pwd)
            strength, color = password_strength(entropy)
            strength_label.config(text=f"Strength: {strength} ({entropy:.0f} bits)", bootstyle=color)
            
            suggestions = password_suggestions(pwd)
            suggestions_text.config(state=tk.NORMAL)
            suggestions_text.delete("1.0", tk.END)
            suggestions_text.insert(tk.END, "\n".join(suggestions))
            suggestions_text.config(state=tk.DISABLED)

        e_pass.bind("<KeyRelease>", update_strength)

        def proceed_to_2fa():
            username = e_user.get().strip()
            password = e_pass.get()
            
            if not username or not password:
                messagebox.showwarning("Error", "Both fields required")
                return
            
            # Try to register (will check password strength)
            success, msg = register(username, password)
            if not success:
                messagebox.showerror("Registration Failed", msg)
                return
            
            # Registration successful, now enable 2FA
            success_2fa, msg_2fa, secret = enable_2fa(username)
            if success_2fa:
                register_state["stage"] = "setup_2fa"
                register_state["username"] = username
                register_state["totp_secret"] = secret
                show_register(root, clear_frame_func, show_main_menu_func)
            else:
                messagebox.showerror("Error", "Failed to setup 2FA")

        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttkb.Button(btn_frame, text="Next: Setup 2FA →", bootstyle=SUCCESS, width=25,
                   command=proceed_to_2fa).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, width=15,
                   command=lambda: (register_state.update({"stage": "credentials", "username": None, "password": None}), show_main_menu_func())).pack(side="left", padx=10)

    elif register_state["stage"] == "setup_2fa":
        # Stage 2: Setup 2FA
        ttkb.Label(main_frame, text="Setup Two-Factor Authentication", 
                  font=("Helvetica", 24, "bold"), bootstyle=WARNING).pack(pady=(0, 20))
        
        ttkb.Label(main_frame, text="Scan this QR code with your authenticator app:", 
                  font=("Helvetica", 12)).pack(pady=10)

        # Generate and display QR code
        qr_data = generate_qr_for_totp(register_state["totp_secret"], register_state["username"])
        
        # Decode base64 image
        img_data = base64.b64decode(qr_data.split(',')[1])
        img = Image.open(BytesIO(img_data))
        img = img.resize((250, 250))
        photo = ImageTk.PhotoImage(img)
        
        qr_label = tk.Label(main_frame, image=photo)
        qr_label.image = photo  # Keep reference
        qr_label.pack(pady=10)

        # Secret key for manual entry
        secret_frame = ttkb.Frame(main_frame)
        secret_frame.pack(pady=10)
        ttkb.Label(secret_frame, text="Or enter this code manually:", 
                  font=("Helvetica", 10)).pack()
        ttkb.Label(secret_frame, text=register_state["totp_secret"], 
                  font=("Courier", 12, "bold"), bootstyle=INFO).pack()

        # Verify code
        ttkb.Label(main_frame, text="Enter the 6-digit code to verify:", 
                  font=("Helvetica", 12, "bold")).pack(pady=(20, 5))
        
        code_entry = ttkb.Entry(main_frame, width=15, font=("Courier", 18), 
                               justify="center", bootstyle=SUCCESS)
        code_entry.pack(pady=10)
        code_entry.focus_set()

        def verify_and_complete():
            code = code_entry.get().strip()
            if len(code) != 6 or not code.isdigit():
                messagebox.showwarning("Invalid", "Enter 6 digits")
                return
            
            if verify_totp(register_state["totp_secret"], code, window=2):
                messagebox.showinfo("Success", 
                    f"Account created successfully!\n\n"
                    f"Username: {register_state['username']}\n"
                    f"2FA: Enabled ✅\n\n"
                    f"You can now login!")
                register_state.update({"stage": "credentials", "username": None, "password": None, "totp_secret": None})
                show_main_menu_func()
            else:
                messagebox.showerror("Failed", "Invalid code. Try again.")
                code_entry.delete(0, tk.END)

        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttkb.Button(btn_frame, text="✓ Verify & Complete", bootstyle=SUCCESS, width=25,
                   command=verify_and_complete).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Cancel", bootstyle=DANGER, width=15,
                   command=lambda: (register_state.update({"stage": "credentials", "username": None, "password": None}), show_main_menu_func())).pack(side="left", padx=10)

    root.update_idletasks()
    ensure_background_behind(root)