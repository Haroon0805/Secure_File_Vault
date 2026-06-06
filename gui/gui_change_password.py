# gui_change_password.py
# Change Password Screen

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import load_users
from security import verify_password, hash_password, calculate_entropy, password_strength
from gui_config import ensure_background_behind, create_form_frame


def show_change_password(root, clear_frame_func, current_user, show_vault_dashboard_func):
    """Display change password screen"""
    clear_frame_func()
    root.title("Change Password - Secure Vault")

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container)
    main_frame.pack(expand=True, pady=50)

    # Header
    ttkb.Label(main_frame, text="Change Password", 
              font=("Helvetica", 28, "bold"), bootstyle=PRIMARY).pack(pady=(0, 30))

    # Current password
    ttkb.Label(main_frame, text="Current Password:", 
              font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
    
    current_pass_frame = ttkb.Frame(main_frame)
    current_pass_frame.pack(fill="x", padx=20, pady=10)
    e_current = ttkb.Entry(current_pass_frame, show="*", font=("Helvetica", 11))
    e_current.pack(side="left", fill="x", expand=True)
    show_current = tk.BooleanVar()
    ttkb.Checkbutton(current_pass_frame, text="Show", variable=show_current,
                    command=lambda: e_current.config(show="" if show_current.get() else "*"),
                    bootstyle=INFO).pack(side="right", padx=10)

    # New password
    ttkb.Label(main_frame, text="New Password:", 
              font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
    
    new_pass_frame = ttkb.Frame(main_frame)
    new_pass_frame.pack(fill="x", padx=20, pady=10)
    e_new = ttkb.Entry(new_pass_frame, show="*", font=("Helvetica", 11))
    e_new.pack(side="left", fill="x", expand=True)
    show_new = tk.BooleanVar()
    ttkb.Checkbutton(new_pass_frame, text="Show", variable=show_new,
                    command=lambda: e_new.config(show="" if show_new.get() else "*"),
                    bootstyle=INFO).pack(side="right", padx=10)

    # Strength indicator
    strength_label = ttkb.Label(main_frame, text="Strength: N/A", 
                               font=("Helvetica", 12, "bold"))
    strength_label.pack(pady=10)

    def update_strength(event=None):
        pwd = e_new.get()
        if pwd:
            entropy = calculate_entropy(pwd)
            strength, color = password_strength(entropy)
            strength_label.config(text=f"Strength: {strength} ({entropy:.0f} bits)", 
                                 bootstyle=color)
        else:
            strength_label.config(text="Strength: N/A", bootstyle=SECONDARY)

    e_new.bind("<KeyRelease>", update_strength)

    # Confirm password
    ttkb.Label(main_frame, text="Confirm New Password:", 
              font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
    
    confirm_pass_frame = ttkb.Frame(main_frame)
    confirm_pass_frame.pack(fill="x", padx=20, pady=10)
    e_confirm = ttkb.Entry(confirm_pass_frame, show="*", font=("Helvetica", 11))
    e_confirm.pack(side="left", fill="x", expand=True)

    def change_password():
        current = e_current.get()
        new = e_new.get()
        confirm = e_confirm.get()

        if not all([current, new, confirm]):
            messagebox.showwarning("Error", "All fields required")
            return

        # Verify current password
        users = load_users()
        if current_user not in users:
            messagebox.showerror("Error", "User not found")
            return

        if not verify_password(current, users[current_user]["password"]):
            messagebox.showerror("Error", "Current password incorrect")
            return

        # Check new passwords match
        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match")
            return

        # Check password strength
        entropy = calculate_entropy(new)
        if entropy < 30:
            messagebox.showerror("Error", "Password too weak (min 30 bits)")
            return

        # Update password
        users[current_user]["password"] = hash_password(new)
        
        import json
        with open("users.json", 'w') as f:
            json.dump(users, f, indent=2)

        messagebox.showinfo("Success", "Password changed successfully!")
        show_vault_dashboard_func()

    # Buttons
    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=30)

    ttkb.Button(btn_frame, text="✓ Change Password", bootstyle=SUCCESS, width=20,
               command=change_password).pack(side="left", padx=10)
    ttkb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, width=15,
               command=show_vault_dashboard_func).pack(side="left", padx=10)

    root.update_idletasks()
    ensure_background_behind(root)