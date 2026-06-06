# gui_enhanced_dashboard.py
# Clean Centered Dashboard

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import load_users
from vault import list_files
from gui_config import ensure_background_behind, create_form_frame
import json
import os
from datetime import datetime


def export_vault_backup_quick(username):
    """Quick vault backup"""
    try:
        vault_file = f"vault_{username}.json"
        if not os.path.exists(vault_file):
            return False, "No vault found"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = filedialog.asksaveasfilename(
            defaultextension=".vault",
            initialfile=f"vault_backup_{username}_{timestamp}.vault",
            title="Save Vault Backup"
        )
        
        if not output_path:
            return False, "Cancelled"
        
        with open(vault_file, 'r') as f:
            vault_data = json.load(f)
        
        backup_data = {
            "username": username,
            "backup_date": datetime.now().isoformat(),
            "file_count": len(vault_data),
            "vault_data": vault_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return True, f"Backup created!\n{len(vault_data)} files"
    except Exception as e:
        return False, str(e)


def import_vault_backup_quick(username):
    """Quick vault import"""
    try:
        backup_path = filedialog.askopenfilename(
            title="Select Vault Backup",
            filetypes=[("Vault Backup", "*.vault")]
        )
        
        if not backup_path:
            return False, "Cancelled"
        
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        vault_data = backup_data.get("vault_data", {})
        vault_file = f"vault_{username}.json"
        
        if os.path.exists(vault_file):
            if not messagebox.askyesno("Merge?", f"Merge {len(vault_data)} files?"):
                return False, "Cancelled"
            with open(vault_file, 'r') as f:
                existing = json.load(f)
            existing.update(vault_data)
            vault_data = existing
        
        with open(vault_file, 'w') as f:
            json.dump(vault_data, f, indent=2)
        
        return True, f"Imported {len(vault_data)} files"
    except Exception as e:
        return False, str(e)


def show_enhanced_dashboard(root, clear_frame_func, current_user, add_file_action_func,
                           show_files_list_func, enable_2fa_func, disable_2fa_func, 
                           logout_func, change_password_func=None, show_activity_log_func=None):
    """Display centered dashboard"""
    clear_frame_func()
    root.title(f"Secure Vault — {current_user}")

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container)
    main_frame.pack(expand=True, pady=50)

    # Header
    ttkb.Label(main_frame, text=f"Welcome, {current_user}!", 
              font=("Helvetica", 28, "bold"), bootstyle=SUCCESS).pack(pady=(0, 40))

    # Stats
    users = load_users()
    files = list_files(current_user)
    totp_enabled = users.get(current_user, {}).get("totp_enabled", False)
    
    stats_text = f"📁 {len(files)} Files  •  🔐 2FA: {'Enabled ✅' if totp_enabled else 'Disabled ⚠️'}"
    ttkb.Label(main_frame, text=stats_text, font=("Helvetica", 13), 
              bootstyle=SUCCESS if totp_enabled else WARNING).pack(pady=(0, 30))

    # Action buttons - 2x2
    actions_frame = ttkb.Frame(main_frame)
    actions_frame.pack(pady=20)
    
    button_width = 28
    
    ttkb.Button(actions_frame, text="📁 Add New File", bootstyle=SUCCESS, width=button_width,
               command=add_file_action_func).grid(row=0, column=0, padx=12, pady=12)
    ttkb.Button(actions_frame, text="📂 View My Files", bootstyle=INFO, width=button_width,
               command=show_files_list_func).grid(row=0, column=1, padx=12, pady=12)
    
    if change_password_func:
        ttkb.Button(actions_frame, text="🔑 Change Password", bootstyle=PRIMARY, width=button_width,
                   command=change_password_func).grid(row=1, column=0, padx=12, pady=12)
    
    def confirm_disable_2fa():
        if messagebox.askyesno("Disable 2FA", 
                              "⚠️ Are you sure?\nThis makes your account less secure."):
            disable_2fa_func()
    
    ttkb.Button(actions_frame, text="🔓 Disable 2FA", bootstyle=DANGER, width=button_width,
               command=confirm_disable_2fa).grid(row=1, column=1, padx=12, pady=12)

    # Separator
    ttkb.Separator(main_frame, orient="horizontal").pack(fill="x", pady=30)

    # Backup section
    ttkb.Label(main_frame, text="Backup & Activity", 
              font=("Helvetica", 12, "bold")).pack(pady=(0, 15))

    def do_backup():
        success, msg = export_vault_backup_quick(current_user)
        messagebox.showinfo("Backup", msg) if success else messagebox.showerror("Error", msg)

    def do_import():
        success, msg = import_vault_backup_quick(current_user)
        if success:
            messagebox.showinfo("Import", msg)
            show_enhanced_dashboard(root, clear_frame_func, current_user, add_file_action_func,
                                  show_files_list_func, enable_2fa_func, disable_2fa_func, 
                                  logout_func, change_password_func, show_activity_log_func)
        elif msg != "Cancelled":
            messagebox.showerror("Error", msg)

    backup_btns = ttkb.Frame(main_frame)
    backup_btns.pack()
    
    ttkb.Button(backup_btns, text="💾 Backup Vault", bootstyle=INFO, width=18,
               command=do_backup).pack(side="left", padx=8)
    ttkb.Button(backup_btns, text="📥 Import Backup", bootstyle=INFO, width=18,
               command=do_import).pack(side="left", padx=8)
    
    if show_activity_log_func:
        ttkb.Button(backup_btns, text="📊 View Activity Log", bootstyle=SECONDARY, width=18,
                   command=show_activity_log_func).pack(side="left", padx=8)

    # Logout
    ttkb.Button(main_frame, text="🚪 Logout", bootstyle=DANGER, width=25,
               command=logout_func).pack(pady=(40, 0))

    root.update_idletasks()
    ensure_background_behind(root)