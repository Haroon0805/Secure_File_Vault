# gui_security_screens.py
# Security Features UI: 2FA Setup/Disable and Password Attack Simulator

import base64
import tkinter as tk
from io import BytesIO
from tkinter import messagebox, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from authentication import enable_2fa, disable_2fa
from attack_simulator import simulate_attack
from security import generate_qr_for_totp, verify_totp
from gui_config import ensure_background_behind, create_menu_frame, create_form_frame


def show_attack_simulator(root, clear_frame_func, show_main_menu_func):
    """Display the password strength and attack simulator screen"""
    clear_frame_func()
    root.title("Password Strength & Attack Simulator")

    # Create container that appears over background
    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=30)
    main_frame.pack(expand=True, fill="both")

    # Header - Centered
    header_frame = ttkb.Frame(main_frame)
    header_frame.pack(pady=(0, 40))
    ttkb.Label(header_frame, text="Password Strength & Attack Simulator",
               style="Header.TLabel").pack()

    ttkb.Label(main_frame, text="Enter password to analyze:",
               font=("Helvetica", 14)).pack(anchor="w")

    pass_frame = ttkb.Frame(main_frame)
    pass_frame.pack(fill="x", pady=15)
    e_test = ttkb.Entry(pass_frame, width=70, font=("Courier", 13), show="*")
    e_test.pack(side="left", fill="x", expand=True)
    show_var = tk.BooleanVar()
    ttkb.Checkbutton(pass_frame, text="Show", variable=show_var,
                     command=lambda: e_test.config(show="" if show_var.get() else "*"),
                     bootstyle=INFO).pack(side="right", padx=15)

    output_text = scrolledtext.ScrolledText(main_frame, height=22, width=90,
                                            font=("Courier", 11), wrap=tk.WORD)
    output_text.pack(pady=25, fill="both", expand=True)
    output_text.insert(tk.END, "Enter a password and press Enter or click Simulate to see results.\n")

    def run_sim(event=None):
        pwd = e_test.get().strip()
        if not pwd:
            messagebox.showwarning("Input Required", "Please enter a password")
            return
        result = simulate_attack(pwd)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result)
        output_text.see(tk.END)

    e_test.bind("<Return>", run_sim)

    # Centered button frame
    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=30)

    ttkb.Button(btn_frame, text="Simulate", bootstyle=WARNING, width=22,
                style="Accent.TButton", command=run_sim).pack(side="left", padx=10)
    ttkb.Button(btn_frame, text="Back to Main Menu", bootstyle=SECONDARY, width=20,
                command=show_main_menu_func).pack(side="left", padx=10)

    e_test.focus_set()

    # IMPORTANT: Call this AFTER all widgets are created
    root.update_idletasks()
    ensure_background_behind(root)


def enable_2fa_action(root, current_user, show_vault_dashboard_func):
    """Display 2FA setup dialog with QR code"""
    if current_user is None:
        messagebox.showerror("Error", "Not logged in")
        return

    success, msg, secret = enable_2fa(current_user)
    if not success:
        messagebox.showerror("2FA Setup", msg)
        return

    win = ttkb.Toplevel(root)
    win.title("Setup Two-Factor Authentication")
    win.geometry("520x650")

    ttkb.Label(win, text="Scan QR Code", style="Header.TLabel").pack(pady=15)
    ttkb.Label(win, text="Use Google Authenticator, Microsoft Authenticator, etc.",
               font=("Helvetica", 11)).pack()

    qr_data = generate_qr_for_totp(secret, current_user)
    img_data = base64.b64decode(qr_data.split(",")[1])
    img = Image.open(BytesIO(img_data))
    photo = ImageTk.PhotoImage(img.resize((320, 320)))

    qr_label = ttkb.Label(win, image=photo)
    qr_label.image = photo
    qr_label.pack(pady=20)

    ttkb.Label(win, text=f"Or enter manually:\n{secret}",
               font=("Courier", 10), bootstyle=INFO).pack(pady=10)

    ttkb.Label(win, text="Enter the 6-digit code from your app to verify:",
               font=("Helvetica", 11)).pack(pady=(20, 5))

    e_verify = ttkb.Entry(win, width=20, justify="center", font=("Helvetica", 14))
    e_verify.pack(pady=10)

    def verify_setup():
        code = e_verify.get().strip()
        if len(code) != 6 or not code.isdigit():
            messagebox.showwarning("Invalid", "Enter 6 digits")
            return
        if verify_totp(secret, code):
            messagebox.showinfo("Success", "2FA setup completed!")
            win.destroy()
            show_vault_dashboard_func()
        else:
            messagebox.showerror("Error", "Invalid code. Try again.")

    ttkb.Button(win, text="Verify Code", bootstyle=SUCCESS, width=20,
                style="Accent.TButton", command=verify_setup).pack(pady=15)
    ttkb.Button(win, text="Cancel", bootstyle=SECONDARY, command=win.destroy).pack(pady=5)


def disable_2fa_action(current_user, show_vault_dashboard_func):
    """Disable 2FA for the current user"""
    if current_user is None:
        messagebox.showerror("Error", "Not logged in")
        return

    if messagebox.askyesno("Disable 2FA", "Are you sure?\nThis reduces your account security."):
        success, msg = disable_2fa(current_user)
        messagebox.showinfo("2FA", msg)
        show_vault_dashboard_func()