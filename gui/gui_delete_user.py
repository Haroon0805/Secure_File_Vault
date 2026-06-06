# gui_delete_user.py
# User Deletion with 2FA Verification

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import load_users, delete_user
from security import verify_password, verify_totp
from gui_config import ensure_background_behind, create_form_frame


# State for delete flow
delete_state = {"stage": "password", "username": None}


def show_delete_user(root, clear_frame_func, show_main_menu_func, show_delete_user_func):
    """Display user deletion with 2FA verification"""
    clear_frame_func()
    root.title("Delete User - Secure Vault")

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=30)
    main_frame.pack(expand=True, pady=50)

    users = load_users()
    user_list = list(users.keys())

    if not user_list:
        ttkb.Label(main_frame, text="No users exist", bootstyle=WARNING,
                  font=("Helvetica", 16)).pack(pady=40)
        ttkb.Button(main_frame, text="Back", bootstyle=SECONDARY, width=20,
                   command=show_main_menu_func).pack(pady=30)
        root.update_idletasks()
        ensure_background_behind(root)
        return

    if delete_state["stage"] == "password":
        # Stage 1: Select user and enter password
        ttkb.Label(main_frame, text="Delete User Account", 
                  font=("Helvetica", 24, "bold"), bootstyle=DANGER).pack(pady=(0, 30))

        ttkb.Label(main_frame, text="Select user to delete:", 
                  font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        
        combo = ttkb.Combobox(main_frame, values=user_list, width=45, 
                             font=("Helvetica", 12), state="readonly")
        combo.pack(pady=10, padx=20, fill="x")
        if user_list:
            combo.current(0)

        ttkb.Label(main_frame, text="Enter password:", 
                  font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))

        pass_frame = ttkb.Frame(main_frame)
        pass_frame.pack(fill="x", padx=20, pady=10)
        e_pass = ttkb.Entry(pass_frame, show="*", font=("Helvetica", 11))
        e_pass.pack(side="left", fill="x", expand=True)
        show_var = tk.BooleanVar()
        ttkb.Checkbutton(pass_frame, text="Show", variable=show_var,
                        command=lambda: e_pass.config(show="" if show_var.get() else "*"),
                        bootstyle=INFO).pack(side="right", padx=10)

        def verify_password_stage():
            target = combo.get().strip()
            password = e_pass.get()

            if not target or target not in users:
                messagebox.showwarning("Error", "Please select a valid user")
                return
            if not password:
                messagebox.showwarning("Error", "Password required")
                return

            # Verify password
            if verify_password(password, users[target]["password"]):
                # Check if user has 2FA enabled
                if users[target].get("totp_enabled", False):
                    # Proceed to 2FA stage
                    delete_state["stage"] = "2fa"
                    delete_state["username"] = target
                    show_delete_user(root, clear_frame_func, show_main_menu_func, show_delete_user_func)
                else:
                    # No 2FA, ask for final confirmation
                    if messagebox.askyesno("Final Confirmation",
                                          f"⚠️ Delete user '{target}' permanently?\n\n"
                                          f"This action CANNOT be undone!"):
                        success, msg = delete_user(target)
                        messagebox.showinfo("Deleted", msg)
                        delete_state.update({"stage": "password", "username": None})
                        show_delete_user_func()
            else:
                messagebox.showerror("Error", "Incorrect password")

        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=30)

        ttkb.Button(btn_frame, text="Next →", bootstyle=DANGER, width=20,
                   command=verify_password_stage).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, width=15,
                   command=lambda: (delete_state.update({"stage": "password", "username": None}), show_main_menu_func())).pack(side="left", padx=10)

    elif delete_state["stage"] == "2fa":
        # Stage 2: 2FA Verification
        ttkb.Label(main_frame, text="2FA Verification Required", 
                  font=("Helvetica", 24, "bold"), bootstyle=WARNING).pack(pady=(0, 20))
        
        ttkb.Label(main_frame, text=f"Deleting user: {delete_state['username']}", 
                  font=("Helvetica", 13), bootstyle=DANGER).pack(pady=10)
        
        ttkb.Label(main_frame, text="Enter your 6-digit 2FA code to confirm deletion:", 
                  font=("Helvetica", 12)).pack(pady=(20, 10))

        code_entry = ttkb.Entry(main_frame, width=15, font=("Courier", 18), 
                               justify="center", bootstyle=DANGER)
        code_entry.pack(pady=15)
        code_entry.focus_set()

        ttkb.Label(main_frame, text="💡 Open your authenticator app", 
                  font=("Helvetica", 10), bootstyle=INFO).pack(pady=5)

        def verify_2fa_and_delete():
            code = code_entry.get().strip()
            
            if len(code) != 6 or not code.isdigit():
                messagebox.showwarning("Invalid", "Enter exactly 6 digits")
                return

            username = delete_state["username"]
            totp_secret = users[username].get("totp_secret", "")

            if verify_totp(totp_secret, code, window=2):
                # 2FA verified, final confirmation
                if messagebox.askyesno("Final Confirmation",
                                      f"⚠️ Delete user '{username}' permanently?\n\n"
                                      f"This action CANNOT be undone!"):
                    success, msg = delete_user(username)
                    messagebox.showinfo("Deleted", msg)
                    delete_state.update({"stage": "password", "username": None})
                    show_delete_user_func()
            else:
                messagebox.showerror("Failed", "Invalid 2FA code")
                code_entry.delete(0, tk.END)

        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(pady=30)

        ttkb.Button(btn_frame, text="✓ Verify & Delete", bootstyle=DANGER, width=20,
                   command=verify_2fa_and_delete).pack(side="left", padx=10)
        ttkb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, width=15,
                   command=lambda: (delete_state.update({"stage": "password", "username": None}), show_main_menu_func())).pack(side="left", padx=10)

    root.update_idletasks()
    ensure_background_behind(root)