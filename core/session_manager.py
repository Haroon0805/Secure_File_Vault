# session_manager.py
# Auto-logout session timeout management

import time
import threading


class SessionManager:
    """Manages user session timeout with automatic logout"""
    
    def __init__(self, timeout_minutes=5):
        self.timeout_seconds = timeout_minutes * 60
        self.last_activity = time.time()
        self.is_active = False
        self.timer_thread = None
        self.logout_callback = None
        self.warning_callback = None
        self.lock = threading.Lock()
    
    def start_session(self, logout_callback, warning_callback=None):
        """Start monitoring session timeout"""
        self.logout_callback = logout_callback
        self.warning_callback = warning_callback
        self.is_active = True
        self.reset_activity()
        
        # Start monitoring thread
        self.timer_thread = threading.Thread(target=self._monitor_timeout, daemon=True)
        self.timer_thread.start()
    
    def end_session(self):
        """Stop monitoring session"""
        self.is_active = False
        self.logout_callback = None
        self.warning_callback = None
    
    def reset_activity(self):
        """Reset the activity timer (call on user interaction)"""
        with self.lock:
            self.last_activity = time.time()
    
    def get_time_remaining(self):
        """Get seconds remaining before timeout"""
        with self.lock:
            elapsed = time.time() - self.last_activity
            remaining = self.timeout_seconds - elapsed
            return max(0, remaining)
    
    def extend_session(self, minutes=5):
        """Extend session by specified minutes"""
        with self.lock:
            self.last_activity = time.time()
    
    def _monitor_timeout(self):
        """Background thread to monitor timeout - OPTIMIZED"""
        warning_shown = False
        
        while self.is_active:
            time.sleep(10)  # Check every 10 seconds (was 5) - less CPU usage
            
            if not self.is_active:
                break
            
            remaining = self.get_time_remaining()
            
            # Show warning at 1 minute remaining
            if remaining <= 60 and remaining > 0 and not warning_shown:
                if self.warning_callback:
                    self.warning_callback(int(remaining))
                warning_shown = True
            
            # Reset warning flag if user is active again
            if remaining > 60:
                warning_shown = False
            
            # Timeout reached
            if remaining <= 0:
                if self.logout_callback:
                    self.logout_callback()
                self.is_active = False
                break


# Global session manager instance
session_manager = SessionManager(timeout_minutes=5)