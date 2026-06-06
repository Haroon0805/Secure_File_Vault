# gui_password_generator.py
# Password Generator - Perfectly Centered

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import secrets
import string
from security import calculate_entropy, password_strength
from gui_config import ensure_background_behind, create_form_frame


def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    """Generate a secure random password"""
    if not any([use_upper, use_lower, use_digits, use_symbols]):
        return None
    
    charset = ""
    if use_lower:
        charset += string.ascii_lowercase
    if use_upper:
        charset += string.ascii_uppercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not charset:
        return None
    
    password = []
    if use_lower:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
    
    for _ in range(length - len(password)):
        password.append(secrets.choice(charset))
    
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


def show_password_generator(root, clear_frame_func, show_main_menu_func):
    """Display password generator - centered with pack"""
    clear_frame_func()
    root.title("Password Generator - Secure Vault")

    container = create_form_frame(root)
    
    # Main frame - centered using pack
    main_frame = ttkb.Frame(container)
    main_frame.pack(expand=True, pady=50)

    # Header
    ttkb.Label(main_frame, text="Password Generator", 
              font=("Helvetica", 28, "bold"), bootstyle=SUCCESS).pack(pady=(0, 30))

    # Password display
    password_frame = ttkb.Frame(main_frame)
    password_frame.pack(pady=20)
    
    ttkb.Label(password_frame, text="Generated Password:", 
              font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
    
    password_display = ttkb.Frame(password_frame)
    password_display.pack()
    
    password_var = tk.StringVar(value="Click 'Generate' below")
    password_entry = ttkb.Entry(password_display, textvariable=password_var, 
                                font=("Courier", 16), bootstyle=INFO, state="readonly",
                                width=35, justify="center")
    password_entry.pack(side="left", padx=(0, 10))
    
    def copy_to_clipboard():
        pwd = password_var.get()
        if pwd and pwd != "Click 'Generate' below":
            root.clipboard_clear()
            root.clipboard_append(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
    
    ttkb.Button(password_display, text="📋 Copy", bootstyle=INFO, width=10,
               command=copy_to_clipboard).pack(side="left")

    # Strength indicators
    strength_frame = ttkb.Frame(main_frame)
    strength_frame.pack(pady=15)
    
    strength_label = ttkb.Label(strength_frame, text="Strength: N/A", 
                                font=("Helvetica", 13, "bold"))
    strength_label.pack(side="left", padx=15)
    
    entropy_label = ttkb.Label(strength_frame, text="Entropy: 0 bits", 
                              font=("Helvetica", 13))
    entropy_label.pack(side="left", padx=15)

    # Separator
    ttkb.Separator(main_frame, orient="horizontal").pack(fill="x", pady=25)

    # Length slider
    length_frame = ttkb.Frame(main_frame)
    length_frame.pack(pady=15)
    
    ttkb.Label(length_frame, text="Password Length:", 
              font=("Helvetica", 12, "bold")).pack()
    
    slider_frame = ttkb.Frame(length_frame)
    slider_frame.pack(pady=10)
    
    length_var = tk.IntVar(value=16)
    length_label = ttkb.Label(slider_frame, text="16", 
                             font=("Helvetica", 18, "bold"), bootstyle=INFO, width=3)
    length_label.pack(side="right", padx=15)
    
    def update_length(val):
        length_label.config(text=str(int(float(val))))
    
    length_slider = ttkb.Scale(slider_frame, from_=8, to=32, variable=length_var, 
                              orient="horizontal", command=update_length, bootstyle=INFO,
                              length=300)
    length_slider.pack(side="left")

    # Character options
    options_frame = ttkb.Frame(main_frame)
    options_frame.pack(pady=20)
    
    ttkb.Label(options_frame, text="Include Characters:", 
              font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
    
    options_grid = ttkb.Frame(options_frame)
    options_grid.pack()
    
    use_upper = tk.BooleanVar(value=True)
    use_lower = tk.BooleanVar(value=True)
    use_digits = tk.BooleanVar(value=True)
    use_symbols = tk.BooleanVar(value=True)
    
    options = [
        ("Uppercase (A-Z)", use_upper),
        ("Lowercase (a-z)", use_lower),
        ("Numbers (0-9)", use_digits),
        ("Symbols (!@#$)", use_symbols)
    ]
    
    for i, (text, var) in enumerate(options):
        row = i // 2
        col = i % 2
        ttkb.Checkbutton(options_grid, text=text, variable=var, 
                        bootstyle="success-round-toggle").grid(row=row, column=col, 
                                                               padx=20, pady=8, sticky="w")

    # Buttons
    def do_generate():
        length = length_var.get()
        
        if not any([use_upper.get(), use_lower.get(), use_digits.get(), use_symbols.get()]):
            messagebox.showwarning("Error", "Please select at least one character type!")
            return
        
        pwd = generate_password(
            length=length,
            use_upper=use_upper.get(),
            use_lower=use_lower.get(),
            use_digits=use_digits.get(),
            use_symbols=use_symbols.get()
        )
        
        if pwd:
            password_var.set(pwd)
            
            entropy = calculate_entropy(pwd)
            strength, color = password_strength(entropy)
            strength_label.config(text=f"Strength: {strength}", bootstyle=color)
            entropy_label.config(text=f"Entropy: {entropy:.1f} bits", bootstyle=color)
        else:
            messagebox.showerror("Error", "Failed to generate password")

    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=30)
    
    ttkb.Button(btn_frame, text="🔄 Generate Password", bootstyle=SUCCESS, width=25,
               style="Accent.TButton", command=do_generate).pack(side="left", padx=10)
    ttkb.Button(btn_frame, text="← Back", bootstyle=SECONDARY, width=18,
               command=show_main_menu_func).pack(side="left", padx=10)

    # Generate initial password
    do_generate()

    root.update_idletasks()
    ensure_background_behind(root)