# gui_reset_password.py
# Password Reset Screen with 2FA Support

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import reset_password
from gui_config import ensure_background_behind, create_form_frame


def show_reset_password(root, clear_frame_func, show_main_menu_func, reset_state=None):
    """Display the password reset screen with 2FA support"""
    clear_frame_func()
    root.title("Reset Password - Secure Vault")

    # Initialize reset state if not provided
    if reset_state is None:
        reset_state = {"stage": "password", "username": None, "new_password": None}

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=30)
    main_frame.pack(expand=True, fill="both")

    if reset_state["stage"] == "password":
        # Stage 1: Enter username and new password - Centered
        header_frame = ttkb.Frame(main_frame)
        header_frame.pack(pady=(0, 40))
        ttkb.Label(header_frame, text="Reset Password", style="Header.TLabel").pack()

        ttkb.Label(main_frame, text="Username", style="SubHeader.TLabel").pack(anchor="w")
        e_user = ttkb.Entry(main_frame, width=50, bootstyle=INFO)
        e_user.pack(pady=(8, 20), fill="x")

        ttkb.Label(main_frame, text="New Password", style="SubHeader.TLabel").pack(anchor="w")
        pass_frame = ttkb.Frame(main_frame)
        pass_frame.pack(fill="x", pady=(8, 10))
        e_pass = ttkb.Entry(pass_frame, width=50, show="*")
        e_pass.pack(side="left", fill="x", expand=True)
        show_var = tk.BooleanVar()
        ttkb.Checkbutton(pass_frame, text="Show", variable=show_var,
                         command=lambda: e_pass.config(show="" if show_var.get() else "*"),
                         bootstyle=INFO).pack(side="right", padx=12)

        def do_reset():
            user = e_user.get().strip()
            new_pwd = e_pass.get()
            if not user or not new_pwd:
                messagebox.showwarning("Error", "Both fields required")
                return

            success, msg, needs_totp = reset_password(user, new_pwd)

            if needs_totp:
                reset_state["stage"] = "totp"
                reset_state["username"] = user
                reset_state["new_password"] = new_pwd
                show_reset_password(root, clear_frame_func, show_main_menu_func, reset_state)
            else:
                messagebox.showinfo("Reset Password", msg)
                if success:
                    show_main_menu_func()

        # Centered button frame
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=40)

        ttkb.Button(btn_frame, text="Reset Password", bootstyle=WARNING, width=22,
                    style="Accent.TButton", command=do_reset).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Back", bootstyle=SECONDARY, width=18,
                    command=show_main_menu_func).pack(side="left", padx=10)

    elif reset_state["stage"] == "totp":
        # Stage 2: 2FA Verification - All centered
        header_frame = ttkb.Frame(main_frame)
        header_frame.pack(pady=30)
        ttkb.Label(header_frame, text="2FA Verification Required", style="Header.TLabel").pack()
        
        info_frame1 = ttkb.Frame(main_frame)
        info_frame1.pack(pady=8)
        ttkb.Label(info_frame1, text="This account has 2FA enabled",
                   font=("Helvetica", 13)).pack()
        
        info_frame2 = ttkb.Frame(main_frame)
        info_frame2.pack(pady=8)
        ttkb.Label(info_frame2, text="Enter the 6-digit code from your authenticator app",
                   font=("Helvetica", 13)).pack()
        
        account_frame = ttkb.Frame(main_frame)
        account_frame.pack(pady=5)
        ttkb.Label(account_frame, text=f"Account: {reset_state['username']}",
                   bootstyle=INFO, font=("Helvetica", 12)).pack()

        tip_frame = ttkb.Frame(main_frame)
        tip_frame.pack(pady=5)
        ttkb.Label(tip_frame, text="💡 Tip: Wait for a fresh code (25-30 seconds remaining) before entering",
                   font=("Helvetica", 10), bootstyle=WARNING).pack()

        entry_frame = ttkb.Frame(main_frame)
        entry_frame.pack(pady=25)
        e_totp = ttkb.Entry(entry_frame, width=20, font=("Helvetica", 18), justify="center")
        e_totp.pack()
        e_totp.focus_set()

        def do_totp_verify():
            code = e_totp.get().strip()
            if len(code) != 6 or not code.isdigit():
                messagebox.showwarning("Invalid Code", "Please enter exactly 6 digits (no spaces)")
                return

            success, msg, needs_totp = reset_password(
                reset_state["username"],
                reset_state["new_password"],
                code
            )

            if success:
                messagebox.showinfo("Success", msg)
                reset_state["stage"] = "password"
                show_main_menu_func()
            else:
                messagebox.showerror("2FA Failed",
                                     f"{msg}\n\n💡 Tips:\n"
                                     "• Make sure your phone and computer times are synced\n"
                                     "• Wait for a fresh code (timer at 25-30 seconds)\n"
                                     "• Enter the code immediately\n"
                                     "• Check you're looking at the correct account in your app")
                e_totp.delete(0, tk.END)

        # Centered button frame
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=30)

        ttkb.Button(btn_frame, text="Verify & Reset", bootstyle=SUCCESS, width=22,
                    style="Accent.TButton", command=do_totp_verify).pack(side="left", padx=10)

        def cancel_reset():
            reset_state["stage"] = "password"
            show_main_menu_func()

        ttkb.Button(btn_frame, text="Cancel", bootstyle=DANGER, width=18,
                    command=cancel_reset).pack(side="left", padx=10)

    root.update_idletasks()
    ensure_background_behind(root)