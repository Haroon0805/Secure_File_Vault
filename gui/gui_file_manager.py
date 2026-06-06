# gui_file_manager.py
# File Manager with Search - Perfectly Centered

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from vault import list_files, get_file_content, delete_file
from gui_config import ensure_background_behind, create_form_frame


def show_files_with_search(root, clear_frame_func, current_user, current_key, show_vault_dashboard_func):
    """Display file manager - centered with pack"""
    clear_frame_func()
    root.title(f"My Files — {current_user}")

    container = create_form_frame(root)
    
    # Main frame - centered using pack
    main_frame = ttkb.Frame(container)
    main_frame.pack(expand=True, pady=50)

    # Header
    ttkb.Label(main_frame, text="My Encrypted Files", 
              font=("Helvetica", 28, "bold"), bootstyle=INFO).pack(pady=(0, 25))

    # Search and Filter
    search_frame = ttkb.Frame(main_frame)
    search_frame.pack(pady=15)
    
    ttkb.Label(search_frame, text="🔍", font=("Helvetica", 16)).grid(row=0, column=0, padx=5)
    
    search_var = tk.StringVar()
    search_entry = ttkb.Entry(search_frame, textvariable=search_var, width=30, 
                             bootstyle=INFO, font=("Helvetica", 11))
    search_entry.grid(row=0, column=1, padx=5)
    
    ttkb.Label(search_frame, text="Filter:", 
              font=("Helvetica", 11)).grid(row=0, column=2, padx=(20, 5))
    
    filter_var = tk.StringVar(value="All Files")
    filter_options = ["All Files", ".txt", ".pdf", ".jpg", ".png", ".docx", ".xlsx", ".zip"]
    filter_combo = ttkb.Combobox(search_frame, textvariable=filter_var, 
                                values=filter_options, width=12, state="readonly")
    filter_combo.grid(row=0, column=3, padx=5)

    # File list
    list_frame = ttkb.Frame(main_frame)
    list_frame.pack(pady=20)

    scrollbar = ttkb.Scrollbar(list_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    file_listbox = tk.Listbox(list_frame, font=("Courier", 11), height=12, width=60,
                              yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
    file_listbox.pack(side="left")
    scrollbar.config(command=file_listbox.yview)

    # Results counter
    results_frame = ttkb.Frame(main_frame)
    results_frame.pack(pady=10)
    
    results_label = ttkb.Label(results_frame, text="", font=("Helvetica", 10), bootstyle=INFO)
    results_label.pack()

    def update_file_list():
        file_listbox.delete(0, tk.END)
        files = list_files(current_user)
        
        search_term = search_var.get().lower()
        filter_ext = filter_var.get()
        
        filtered_files = []
        for f in files:
            if search_term and search_term not in f.lower():
                continue
            if filter_ext != "All Files" and not f.endswith(filter_ext):
                continue
            filtered_files.append(f)
        
        if not filtered_files:
            file_listbox.insert(tk.END, "No files found")
            results_label.config(text="0 files")
        else:
            for f in sorted(filtered_files):
                file_listbox.insert(tk.END, f)
            results_label.config(text=f"{len(filtered_files)} file(s)")
    
    search_var.trace("w", lambda *args: update_file_list())
    filter_var.trace("w", lambda *args: update_file_list())
    update_file_list()

    # Action buttons
    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=20)

    def do_export():
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        filename = file_listbox.get(selection[0])
        if filename == "No files found":
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension="",
            initialfile=filename,
            title="Save Decrypted File As"
        )
        if save_path:
            content = get_file_content(current_user, filename, current_key)
            if content:
                with open(save_path, 'wb') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"File exported!")

    def do_delete():
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        filename = file_listbox.get(selection[0])
        if filename == "No files found":
            return

        if messagebox.askyesno("Confirm", f"Delete '{filename}'?\nCannot be undone."):
            success, msg = delete_file(current_user, filename)
            messagebox.showinfo("Delete", msg)
            update_file_list()

    ttkb.Button(btn_frame, text="📥 Export", bootstyle=SUCCESS, width=18,
               command=do_export).pack(side="left", padx=8)
    ttkb.Button(btn_frame, text="🗑️ Delete", bootstyle=DANGER, width=18,
               command=do_delete).pack(side="left", padx=8)
    ttkb.Button(btn_frame, text="← Back", bootstyle=SECONDARY, width=15,
               command=show_vault_dashboard_func).pack(side="left", padx=8)

    root.update_idletasks()
    ensure_background_behind(root)