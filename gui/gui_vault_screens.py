# gui_vault_screens.py
# Vault Dashboard and File Management UI Screens

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from authentication import load_users
from vault import add_file, list_files, get_file_content, delete_file
from gui_config import ensure_background_behind, create_menu_frame, create_form_frame


def show_vault_dashboard(root, clear_frame_func, current_user, add_file_action_func,
                         show_files_list_func, enable_2fa_func, disable_2fa_func, logout_func):
    """Display the main vault dashboard after successful login"""
    clear_frame_func()
    root.title(f"Secure Vault — {current_user}")

    # Create HORIZONTAL form frame (wider like login/register)
    container = create_form_frame(root)
    main_frame = ttkb.Frame(container, padding=50)
    main_frame.pack(expand=True, fill="both")

    ttkb.Label(main_frame, text=f"Welcome back, {current_user}",
               style="Header.TLabel", bootstyle=SUCCESS).pack(pady=(0, 30))

    users = load_users()
    totp_enabled = users.get(current_user, {}).get("totp_enabled", False)

    ttkb.Label(main_frame,
               text=f"Two-Factor Authentication: {'Enabled' if totp_enabled else 'Disabled'}",
               bootstyle=SUCCESS if totp_enabled else WARNING,
               font=("Helvetica", 14)).pack(pady=15)

    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=50)

    buttons = [
        ("Add New File", SUCCESS, add_file_action_func),
        ("View / Export Files", INFO, show_files_list_func),
        ("Enable 2FA" if not totp_enabled else "Disable 2FA",
         WARNING if not totp_enabled else DANGER,
         enable_2fa_func if not totp_enabled else disable_2fa_func),
        ("Logout", DANGER, logout_func)
    ]

    for i, (text, bootstyle, cmd) in enumerate(buttons):
        ttkb.Button(btn_frame, text=text, bootstyle=bootstyle, width=28,
                    style="Accent.TButton", command=cmd).grid(row=i // 2, column=i % 2, padx=25, pady=20)

    # IMPORTANT: Call this AFTER all widgets are created
    root.update_idletasks()
    ensure_background_behind(root)


def add_file_action(current_user, current_key):
    """Handle adding a new file to the vault"""
    if current_user is None or current_key is None:
        messagebox.showerror("Error", "Not logged in")
        return
    success, msg = add_file(current_user, current_key)
    messagebox.showinfo("Add File", msg)


def show_files_list(root, current_user, current_key):
    """Display list of files in the vault with view/export/delete options"""
    if current_user is None or current_key is None:
        messagebox.showerror("Error", "Not logged in")
        return

    win = ttkb.Toplevel(root)
    win.title("Your Secured Files")
    win.geometry("650x550")

    ttkb.Label(win, text="Secured Files", style="Header.TLabel").pack(pady=15)

    files = list_files(current_user)
    if not files:
        ttkb.Label(win, text="No files stored yet", bootstyle=WARNING,
                   font=("Helvetica", 12)).pack(pady=30)
        return

    listbox = tk.Listbox(win, height=15, font=("Courier", 11), width=55)
    listbox.pack(pady=10, padx=20, fill="both", expand=True)

    for f in files:
        listbox.insert(tk.END, f)

    def view_file():
        sel = listbox.curselection()
        if not sel:
            return
        fname = listbox.get(sel[0])
        success, content = get_file_content(current_user, fname, current_key)
        if success:
            temp_path = f"temp_{fname}"
            with open(temp_path, "wb") as f:
                f.write(content)
            messagebox.showinfo("File Exported", f"Saved temporarily as:\n{temp_path}")
        else:
            messagebox.showerror("Error", content)

    def delete_file_action():
        sel = listbox.curselection()
        if not sel:
            return
        fname = listbox.get(sel[0])
        if messagebox.askyesno("Confirm Delete", f"Delete '{fname}'?"):
            success, msg = delete_file(current_user, fname)
            messagebox.showinfo("Delete", msg)
            win.destroy()
            show_files_list(root, current_user, current_key)

    btn_frame = ttkb.Frame(win)
    btn_frame.pack(pady=15)

    ttkb.Button(btn_frame, text="View / Export", bootstyle=INFO,
                command=view_file).pack(side="left", padx=15)
    ttkb.Button(btn_frame, text="Delete", bootstyle=DANGER,
                command=delete_file_action).pack(side="left", padx=15)
    ttkb.Button(btn_frame, text="Close", bootstyle=SECONDARY,
                command=win.destroy).pack(side="left", padx=15)