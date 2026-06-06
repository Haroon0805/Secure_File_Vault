# gui_main_menu.py
# Main Menu Screen

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_config import ensure_background_behind, create_menu_frame


def show_main_menu(root, clear_frame_func, show_register_func, show_login_func,
                   show_attack_simulator_func, show_delete_user_func, show_password_gen_func):
    """Display the main menu screen"""
    clear_frame_func()
    root.title("Secure Vault")

    # Create VERTICAL menu frame (tall & narrow)
    container = create_menu_frame(root)

    # Add padding frame inside
    main_frame = ttkb.Frame(container, padding=50)
    main_frame.pack(expand=True, fill="both")

    ttkb.Label(main_frame, text="Secure Vault", style="Header.TLabel", bootstyle=PRIMARY).pack(pady=(0, 40))

    btn_frame = ttkb.Frame(main_frame)
    btn_frame.pack(pady=20)

    buttons = [
        ("Register New Account", SUCCESS, show_register_func),
        ("Login", INFO, show_login_func),
        ("Password Generator", PRIMARY, show_password_gen_func),  # NEW
        ("Test Password Strength", WARNING, show_attack_simulator_func),
        ("Delete User", DANGER, show_delete_user_func),
        ("Exit", SECONDARY, root.quit)
    ]

    for text, bootstyle, cmd in buttons:
        ttkb.Button(
            btn_frame,
            text=text,
            bootstyle=bootstyle,
            width=35,
            style="Accent.TButton" if bootstyle != DANGER else "Danger.Outline.TButton",
            command=cmd
        ).pack(pady=14, fill="x")

    # IMPORTANT: Call this AFTER all widgets are created
    root.update_idletasks()
    ensure_background_behind(root)