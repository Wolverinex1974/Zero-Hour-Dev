# ==============================================================================
# ZERO HOUR CORE: LOGGER - v24.0 (BLACK BOX FLIGHT RECORDER)
# ==============================================================================
# ROLE: Intercepts all stdout/stderr and UI logs, writing them to a physical file.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================

import os
import sys
import datetime
import traceback

class BlackBoxLogger:
    """
    A persistent file logger that acts as a Flight Recorder for the application.
    It catches all print statements, system errors, and router log events.
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
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

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
        Reroutes all standard print() and error outputs into the physical file.
        """
        sys.stdout = StreamInterceptor(self, "STDOUT", self.original_stdout)
        sys.stderr = StreamInterceptor(self, "STDERR", self.original_stderr)
        sys.excepthook = self.handle_uncaught_exception

    def handle_uncaught_exception(self, exception_type, exception_value, exception_traceback):
        """
        Catches fatal thread crashes before the application dies silently.
        """
        traceback_details = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
        error_message = f"FATAL CRASH DETECTED:\n{traceback_details}"
        self.write_to_file(error_message, "CRITICAL")
        
        if self.original_stderr:
            self.original_stderr.write(error_message)


class StreamInterceptor:
    """
    A helper class to intercept sys.stdout and sys.stderr.
    It writes to the BlackBox file and then passes it along to the original console.
    """
    def __init__(self, logger_instance, stream_name, original_stream):
        self.logger_instance = logger_instance
        self.stream_name = stream_name
        self.original_stream = original_stream

    def write(self, message_data):
        if message_data and not message_data.isspace():
            self.logger_instance.write_to_file(message_data, self.stream_name)
        if self.original_stream:
            self.original_stream.write(message_data)

    def flush(self):
        if self.original_stream:
            self.original_stream.flush()

# Instantiate a global singleton instance
flight_recorder = BlackBoxLogger()