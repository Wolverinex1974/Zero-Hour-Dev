# ==============================================================================
# ZERO HOUR CORE: LOGGER - v23.2 (BLACK BOX FLIGHT RECORDER)
# ==============================================================================
# ROLE: A reliable file-writer that catches fatal application crashes.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE:
# FIX: Removed the aggressive StreamInterceptor that was suffocating PyInstaller
#      and causing silent instant-crashes. Reverted to a pure sys.excepthook.
# ==============================================================================

import os
import sys
import datetime
import traceback

class BlackBoxLogger:
    """
    A persistent file logger that acts as a Flight Recorder for the application.
    It catches system errors and manual router log events.
    """
    def __init__(self):
        self.log_directory = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(self.log_directory):
            try:
                os.makedirs(self.log_directory, exist_ok=True)
            except Exception:
                pass 
                
        timestamp_string = datetime.datetime.now().strftime("%Y-%m-%d")
        self.log_file_path = os.path.join(self.log_directory, f"zerohour_sys_{timestamp_string}.log")
        
        self.original_excepthook = sys.excepthook

    def write_to_file(self, message_text, level="INFO"):
        """
        Appends a formatted string directly to the physical log file.
        """
        if not message_text or message_text.isspace():
            return
            
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_message = f"{timestamp} [{level}] {message_text.strip()}\n"
        
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(formatted_message)
        except Exception:
            pass

    def hook_system_streams(self):
        """
        Reroutes ONLY unhandled fatal crashes into the physical file.
        Leaves standard stdout/stderr completely untouched so the console works.
        """
        sys.excepthook = self.handle_uncaught_exception

    def handle_uncaught_exception(self, exception_type, exception_value, exception_traceback):
        """
        Catches fatal thread crashes right before the application dies.
        """
        traceback_details = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
        error_message = f"FATAL CRASH DETECTED:\n{traceback_details}"
        
        # 1. Write the crash to our logs/zerohour_sys.log file
        self.write_to_file(error_message, "CRITICAL")
        
        # 2. Let the original system error handler print it to the console
        self.original_excepthook(exception_type, exception_value, exception_traceback)


# Instantiate a global singleton instance
flight_recorder = BlackBoxLogger()