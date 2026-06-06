# gui_activity_log.py  
# Activity Log Viewer Screen

import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_config import ensure_background_behind, create_form_frame
import os


def show_activity_log(root, clear_frame_func, current_user, show_vault_dashboard_func):
    """Display activity log professionally"""
    clear_frame_func()
    root.title(f"Activity Log — {current_user}")

    container = create_form_frame(root)
    main_frame = ttkb.Frame(container)
    main_frame.pack(expand=True, pady=50)

    # Header
    ttkb.Label(main_frame, text="Activity Log", 
              font=("Helvetica", 28, "bold"), bootstyle=INFO).pack(pady=(0, 10))
    ttkb.Label(main_frame, text=f"User: {current_user}", 
              font=("Helvetica", 13), bootstyle=SECONDARY).pack(pady=(0, 30))

    # Load logs
    try:
        log_file = "logs.txt"
        if not os.path.exists(log_file):
            user_logs = []
        else:
            with open(log_file, 'r') as f:
                all_logs = f.readlines()
            user_logs = [log.strip() for log in all_logs if current_user in log]
    except:
        user_logs = []

    # Log display
    log_frame = ttkb.Frame(main_frame)
    log_frame.pack(pady=20, fill="both", expand=True)

    scrollbar = ttkb.Scrollbar(log_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    log_text = tk.Text(log_frame, font=("Courier", 10), height=20, width=80,
                      yscrollcommand=scrollbar.set, wrap=tk.WORD, 
                      bg="#2b2b2b", fg="#e0e0e0", padx=15, pady=15)
    log_text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=log_text.yview)

    # Display logs
    if user_logs:
        log_text.insert(tk.END, "="*80 + "\n")
        log_text.insert(tk.END, f"  ACTIVITY LOG FOR: {current_user}\n")
        log_text.insert(tk.END, f"  Total Activities: {len(user_logs)}\n")
        log_text.insert(tk.END, "="*80 + "\n\n")

        for i, log in enumerate(reversed(user_logs), 1):
            if "]" in log:
                timestamp_part = log.split("]")[0] + "]"
                action_part = log.split("]", 1)[1].strip()
                log_text.insert(tk.END, f"{i}. {timestamp_part}\n")
                log_text.insert(tk.END, f"   Action: {action_part}\n\n")
            else:
                log_text.insert(tk.END, f"{i}. {log}\n\n")
    else:
        log_text.insert(tk.END, "\n\n" + " "*30 + "No activity found\n")

    log_text.config(state=tk.DISABLED)

    # Stats
    stats_frame = ttkb.Frame(main_frame)
    stats_frame.pack(pady=15)
    
    login_count = sum(1 for log in user_logs if "login" in log.lower())
    logout_count = sum(1 for log in user_logs if "logout" in log.lower())
    
    ttkb.Label(stats_frame, text=f"📊 Logins: {login_count}  •  Logouts: {logout_count}  •  Total: {len(user_logs)}", 
              font=("Helvetica", 11), bootstyle=INFO).pack()

    # Back button
    ttkb.Button(main_frame, text="← Back to Dashboard", bootstyle=SECONDARY, width=25,
               command=show_vault_dashboard_func).pack(pady=20)

    root.update_idletasks()
    ensure_background_behind(root)