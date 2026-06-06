# main.py
# Main Application Entry Point - Secure Vault

import ttkbootstrap as ttkb
from tkinter import messagebox
from security import log_action
from gui_config import (
    init_background, ensure_background_behind, apply_theme, 
    get_bg_label, resize_background
)
# Import from separate GUI modules
from gui_main_menu import show_main_menu
from gui_register import show_register
from gui_login import show_login
from gui_reset_password import show_reset_password
from gui_delete_user import show_delete_user
from gui_vault_screens import (
    show_vault_dashboard, add_file_action, show_files_list
)
from gui_security_screens import (
    show_attack_simulator, enable_2fa_action, disable_2fa_action
)
# NEW FEATURES
from gui_password_generator import show_password_generator
from gui_file_manager import show_files_with_search
from gui_enhanced_dashboard import show_enhanced_dashboard
from gui_change_password import show_change_password
from gui_activity_log import show_activity_log
from session_manager import session_manager


# ==================== GLOBAL STATE ====================
CURRENT_USER = None
CURRENT_KEY = None

# Login flow state
login_state = {
    "stage": "password",
    "username": "",
    "user_data": None
}


# ==================== UTILITY FUNCTIONS ====================

def clear_frame():
    """Clear only content widgets — keep background label alive - OPTIMIZED FOR SMOOTH TRANSITIONS"""
    bg_label = get_bg_label()
    
    # Instead of destroying, just hide widgets - MUCH FASTER
    for widget in root.winfo_children():
        if widget is not bg_label:
            # Use place_forget or pack_forget to hide instantly
            try:
                if widget.winfo_manager() == 'place':
                    widget.place_forget()
                elif widget.winfo_manager() == 'pack':
                    widget.pack_forget()
                elif widget.winfo_manager() == 'grid':
                    widget.grid_forget()
                # Only destroy after hiding (prevents flicker)
                widget.after(10, widget.destroy)
            except:
                pass  # Widget already destroyed
    
    # Single update - much faster than multiple updates
    root.update_idletasks()
    root.update_idletasks()


def set_current_user(username, key):
    """Set the currently logged-in user"""
    global CURRENT_USER, CURRENT_KEY
    CURRENT_USER = username
    CURRENT_KEY = key


def logout():
    """Log out the current user and return to main menu"""
    global CURRENT_USER, CURRENT_KEY
    if CURRENT_USER:
        log_action(CURRENT_USER, "logged out")
    
    # Stop session monitoring
    session_manager.end_session()
    
    CURRENT_USER = None
    CURRENT_KEY = None
    show_main_menu_wrapper()


def on_session_timeout():
    """Called when session times out"""
    messagebox.showwarning(
        "Session Expired",
        "Your session has expired due to inactivity.\nPlease login again."
    )
    logout()


def on_session_warning(seconds_remaining):
    """Called 1 minute before timeout"""
    response = messagebox.askokcancel(
        "Session Timeout Warning",
        f"Your session will expire in {seconds_remaining} seconds due to inactivity.\n\n"
        "Click OK to extend your session, or Cancel to logout now."
    )
    if response:
        session_manager.extend_session()
    else:
        logout()


# ==================== SCREEN WRAPPERS ====================

def show_main_menu_wrapper():
    """Wrapper for main menu"""
    show_main_menu(
        root, 
        clear_frame, 
        show_register_wrapper, 
        show_login_wrapper,
        show_attack_simulator_wrapper, 
        show_delete_user_wrapper,
        show_password_generator_wrapper  # NEW: Add password generator
    )


def show_register_wrapper():
    """Wrapper for register screen with 2FA setup"""
    show_register(root, clear_frame, show_main_menu_wrapper)


def show_login_wrapper():
    """Wrapper for login screen"""
    show_login(
        root, 
        clear_frame, 
        show_main_menu_wrapper, 
        show_vault_dashboard_wrapper,
        show_reset_password_wrapper, 
        login_state, 
        set_current_user
    )


def show_reset_password_wrapper():
    """Wrapper for reset password screen"""
    show_reset_password(root, clear_frame, show_main_menu_wrapper)


def show_delete_user_wrapper():
    """Wrapper for delete user screen"""
    show_delete_user(root, clear_frame, show_main_menu_wrapper, show_delete_user_wrapper)


def show_attack_simulator_wrapper():
    """Wrapper for attack simulator screen"""
    show_attack_simulator(root, clear_frame, show_main_menu_wrapper)


def show_vault_dashboard_wrapper():
    """Wrapper for enhanced vault dashboard"""
    session_manager.start_session(on_session_timeout, on_session_warning)
    
    show_enhanced_dashboard(
        root, 
        clear_frame, 
        CURRENT_USER, 
        add_file_action_wrapper,
        show_files_list_wrapper,
        enable_2fa_wrapper, 
        disable_2fa_wrapper, 
        logout,
        show_change_password_wrapper,  # Change password
        show_activity_log_wrapper  # Activity log
    )


def show_change_password_wrapper():
    """Wrapper for change password"""
    session_manager.reset_activity()
    show_change_password(root, clear_frame, CURRENT_USER, show_vault_dashboard_wrapper)


def show_activity_log_wrapper():
    """Wrapper for activity log"""
    session_manager.reset_activity()
    show_activity_log(root, clear_frame, CURRENT_USER, show_vault_dashboard_wrapper)
    show_activity_log(root, clear_frame, CURRENT_USER, show_vault_dashboard_wrapper)


def add_file_action_wrapper():
    """Wrapper for add file action"""
    add_file_action(CURRENT_USER, CURRENT_KEY)


def show_files_list_wrapper():
    """Wrapper for files list with search"""
    session_manager.reset_activity()  # Track activity
    show_files_with_search(root, clear_frame, CURRENT_USER, CURRENT_KEY, show_vault_dashboard_wrapper)


def show_password_generator_wrapper():
    """Wrapper for password generator"""
    session_manager.reset_activity()  # Track activity
    show_password_generator(root, clear_frame, show_main_menu_wrapper)


def enable_2fa_wrapper():
    """Wrapper for enable 2FA"""
    session_manager.reset_activity()  # Track activity
    enable_2fa_action(root, CURRENT_USER, show_vault_dashboard_wrapper)


def disable_2fa_wrapper():
    """Wrapper for disable 2FA"""
    session_manager.reset_activity()  # Track activity
    disable_2fa_action(CURRENT_USER, show_vault_dashboard_wrapper)


# ==================== MAIN APPLICATION ====================

if __name__ == "__main__":
    # Initialize main window
    root = ttkb.Window(themename="darkly")
    root.geometry("1100x800")
    root.title("Secure Vault")

    # Apply theme
    apply_theme()

    # Initialize background image
    init_background(root)

    # Keep background visible and properly sized on resize
    root.bind("<Configure>", lambda e: resize_background(e, root))

    # Show main menu
    show_main_menu_wrapper()

    # Start application
    root.mainloop()