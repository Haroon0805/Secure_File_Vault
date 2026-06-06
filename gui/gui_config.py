# gui_config.py
# UI Configuration, Theme Management, and Background Handling

import tkinter as tk
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# Global background variables
bg_photo = None
bg_label = None
bg_image_cache = None  # Cache the PIL image


def init_background(root):
    """Initialize the background image for the application - OPTIMIZED"""
    global bg_photo, bg_label, bg_image_cache
    
    try:
        # Load image only once
        if bg_image_cache is None:
            bg_image_cache = Image.open("cyber-security-concept-digital-art.png")
        
        # Resize to match initial window
        pil_img = bg_image_cache.resize((1100, 800), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(pil_img)
        
        # Create label with image
        bg_label = tk.Label(root, image=bg_photo, bd=0, highlightthickness=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()  # Put it in the back immediately
        
        print("✅ Background image loaded successfully!")
        
    except FileNotFoundError:
        print("❌ ERROR: 'cyber-security-concept-digital-art.png' not found!")
        print("📁 Please place the image file in the same directory as main.py")
        # Fallback to dark color
        bg_label = tk.Label(root, bg="#1e1e2e", bd=0, highlightthickness=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()
    except Exception as e:
        print(f"❌ Failed to load background image: {e}")
        bg_label = tk.Label(root, bg="#1e1e2e", bd=0, highlightthickness=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()


def ensure_background_behind(root):
    """Make sure background label stays behind all widgets - OPTIMIZED"""
    global bg_label
    if bg_label and bg_label.winfo_exists():
        # Only update if background isn't already at the bottom
        try:
            bg_label.lower()  # More efficient than lift() on all widgets
        except:
            pass  # Silently fail if widget doesn't exist


def apply_theme():
    """Apply custom theme styling to the application"""
    style = ttkb.Style()
    style.configure("TButton", font=("Helvetica", 12, "bold"), padding=10)
    style.configure("Accent.TButton", font=("Helvetica", 13, "bold"), padding=14)
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("Header.TLabel", font=("Helvetica", 26, "bold"))
    style.configure("SubHeader.TLabel", font=("Helvetica", 15, "bold"))
    style.map("Accent.TButton",
              background=[("active", "#388E3C"), ("!disabled", "#1976D2")],
              foreground=[("active", "white")])
    style.configure("Danger.Outline.TButton", font=("Helvetica", 12, "bold"))


def get_bg_label():
    """Return the background label reference"""
    return bg_label


def create_menu_frame(root):
    """Create a VERTICAL frame for main menu - NO FLICKER"""
    # Quick destroy of old frames
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_manager() == 'place':
            widget.destroy()
    
    container = tk.Frame(root, bg='#1e1e2e', bd=0, relief='flat', highlightthickness=3, 
                        highlightbackground='#4a90e2', highlightcolor='#4a90e2')
    
    # DON'T place yet - wait for content
    
    # Simple centered frame
    content_frame = tk.Frame(container, bg='#1e1e2e')
    content_frame.place(relx=0.5, rely=0.5, anchor='center')
    
    # NOW place the container after content frame exists
    container.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.35, relheight=0.8)
    
    return content_frame


def create_form_frame(root):
    """Create a SQUARE frame for login, register, etc. - NO FLICKER"""
    # Quick destroy of old frames
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_manager() == 'place':
            widget.destroy()
    
    container = tk.Frame(root, bg='#1e1e2e', bd=0, relief='flat', highlightthickness=3, 
                        highlightbackground='#4a90e2', highlightcolor='#4a90e2')
    
    # DON'T place yet
    
    # Add canvas for scrolling
    canvas = tk.Canvas(container, bg='#1e1e2e', highlightthickness=0)
    
    # Create frame inside canvas
    scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
    
    # Configure canvas scroll region
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    # Create window in canvas - CENTERED
    canvas_window = canvas.create_window(
        (300, 0),
        window=scrollable_frame, 
        anchor="n"
    )
    
    # Recenter when canvas resizes
    def recenter_content(event=None):
        if event:
            canvas.coords(canvas_window, event.width // 2, 0)
    
    canvas.bind("<Configure>", recenter_content)
    
    # Pack canvas
    canvas.pack(side="left", fill="both", expand=True)
    
    # Bind mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", _on_mousewheel)
    
    # NOW place the container after everything is ready
    container.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.55, relheight=0.85)
    
    return scrollable_frame


# Keep old name for backwards compatibility
def create_content_frame(root):
    """Alias for create_form_frame"""
    return create_form_frame(root)


def resize_background(event, root):
    """Resize background image when window is resized - OPTIMIZED"""
    global bg_photo, bg_label, bg_image_cache
    if bg_label and bg_label.winfo_exists() and bg_image_cache:
        try:
            # Get new dimensions
            width = event.width
            height = event.height
            
            # Don't resize on tiny changes
            if width < 100 or height < 100:
                return
            
            # Use cached image instead of reloading from disk
            pil_img = bg_image_cache.resize((width, height), Image.LANCZOS)
            bg_photo = ImageTk.PhotoImage(pil_img)
            bg_label.configure(image=bg_photo)
            bg_label.image = bg_photo
            bg_label.lower()  # Keep it in back
        except Exception as e:
            pass  # Silently fail
            
            # Update label
            bg_label.configure(image=bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Ensure background stays behind
            root.update_idletasks()
            for widget in root.winfo_children():
                if widget != bg_label:
                    widget.lift()
        except:
            pass  # Silently fail if image not found