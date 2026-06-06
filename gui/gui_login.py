# gui_login.py
# Login Screen with 2FA Support

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import login
from gui_config import ensure_background_behind, create_form_frame


def show_login(root, clear_frame_func, show_main_menu_func, show_vault_dashboard_func,
               show_reset_password_func, login_state, set_current_user_func):
    """Display the login screen with password and optional 2FA stages"""
    clear_frame_func()
    root.title("Login - Secure Vault")

    # Create SQUARE form frame (wider for forms)
    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=30)
    main_frame.pack(expand=True, fill="both")

    # Header - Centered
    header_frame = ttkb.Frame(main_frame)
    header_frame.pack(pady=(0, 40))
    ttkb.Label(header_frame, text="Sign In", style="Header.TLabel").pack()

    if login_state["stage"] == "password":
        # Stage 1: Password
        ttkb.Label(main_frame, text="Username", style="SubHeader.TLabel").pack(anchor="w")
        e_user = ttkb.Entry(main_frame, width=50, bootstyle=INFO)
        e_user.pack(pady=(8, 20), fill="x")

        ttkb.Label(main_frame, text="Password", style="SubHeader.TLabel").pack(anchor="w")
        pass_frame = ttkb.Frame(main_frame)
        pass_frame.pack(fill="x", pady=(8, 10))
        e_pass = ttkb.Entry(pass_frame, width=50, show="*")
        e_pass.pack(side="left", fill="x", expand=True)
        show_var = tk.BooleanVar()
        ttkb.Checkbutton(pass_frame, text="Show", variable=show_var,
                         command=lambda: e_pass.config(show="" if show_var.get() else "*"),
                         bootstyle=INFO).pack(side="right", padx=12)

        def do_password_stage():
            user = e_user.get().strip()
            pwd = e_pass.get()
            success, msg, user_data, needs_totp = login(user, pwd)
            if success:
                set_current_user_func(user, user_data["encryption_key"])
                login_state["stage"] = "password"
                show_vault_dashboard_func()
            elif needs_totp:
                login_state["stage"] = "totp"
                login_state["username"] = user
                login_state["user_data"] = user_data
                show_login(root, clear_frame_func, show_main_menu_func, show_vault_dashboard_func,
                           show_reset_password_func, login_state, set_current_user_func)
            else:
                messagebox.showerror("Login Failed", msg)

        # Centered button frame
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=40)

        ttkb.Button(btn_frame, text="Sign In", bootstyle=INFO, width=22,
                    style="Accent.TButton", command=do_password_stage).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Forgot Password?", bootstyle=WARNING,
                    command=show_reset_password_func).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Back", bootstyle=SECONDARY, width=18,
                    command=show_main_menu_func).pack(side="left", padx=10)

    elif login_state["stage"] == "totp":
        # Stage 2: 2FA - All centered
        totp_header = ttkb.Frame(main_frame)
        totp_header.pack(pady=30)
        ttkb.Label(totp_header, text="Two-Factor Verification", style="Header.TLabel").pack()
        
        info_frame = ttkb.Frame(main_frame)
        info_frame.pack(pady=8)
        ttkb.Label(info_frame, text="Enter the 6-digit code from your authenticator app",
                   font=("Helvetica", 13)).pack()
        
        account_frame = ttkb.Frame(main_frame)
        account_frame.pack(pady=5)
        ttkb.Label(account_frame, text=f"Account: {login_state['username']}",
                   bootstyle=INFO, font=("Helvetica", 12)).pack()

        tip_frame = ttkb.Frame(main_frame)
        tip_frame.pack(pady=5)
        ttkb.Label(tip_frame, text="💡 Tip: Wait for a fresh code (25-30 seconds remaining) before entering",
                   font=("Helvetica", 10), bootstyle=WARNING).pack()

        entry_frame = ttkb.Frame(main_frame)
        entry_frame.pack(pady=25)
        e_totp = ttkb.Entry(entry_frame, width=20, font=("Helvetica", 18), justify="center")
        e_totp.pack()

        def do_totp_stage():
            code = e_totp.get().strip()
            if len(code) != 6 or not code.isdigit():
                messagebox.showwarning("Invalid Code", "Please enter exactly 6 digits (no spaces)")
                return
            success, msg, user_data, _ = login(login_state["username"], "", code)
            if success:
                set_current_user_func(login_state["username"], user_data["encryption_key"])
                login_state["stage"] = "password"
                show_vault_dashboard_func()
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

        ttkb.Button(btn_frame, text="Verify", bootstyle=SUCCESS, width=22,
                    style="Accent.TButton", command=do_totp_stage).pack(side="left", padx=10)

        def cancel_2fa():
            login_state["stage"] = "password"
            show_main_menu_func()

        ttkb.Button(btn_frame, text="Cancel", bootstyle=DANGER, width=18,
                    command=cancel_2fa).pack(side="left", padx=10)

    # IMPORTANT: Call this AFTER all widgets are created
    root.update_idletasks()
    ensure_background_behind(root)