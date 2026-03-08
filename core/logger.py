# =========================================================
# ZERO HOUR CORE: TELEMETRY ENGINE - v21.2
# =========================================================
# ROLE: Dual-Stream Flight Recorder (Disk + UI Bridge)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
import logging
import os
import datetime
from PySide6.QtCore import QObject, Signal

class UIHandler(logging.Handler, QObject):
    """ 
    Custom Log Handler that bridges standard Python logging 
    to the PySide6 UI thread via Signals.
    """
    log_signal = Signal(str)

    def __init__(self):
        # Initialize both parents in a vertical, explicit manner
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        """
        Triggered whenever a log event occurs.
        Formats the message and emits the signal to the UI.
        """
        try:
            # Format the log record into a readable string
            message = self.format(record)
            
            # Emit the signal to be caught by the MainWindow console
            self.log_signal.emit(message)
            
        except Exception:
            # Fallback to prevent the logger from crashing the application
            self.handleError(record)

class ParadoxalLogger:
    """
    Orchestrates the global logging system for the Paradoxal Ecosystem.
    Manages the physical log files on disk and the UI telemetry stream.
    """
    def __init__(self, log_dir):
        # Ensure the target log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Initialize the 'Paradoxal' Master Logger
        self.logger = logging.getLogger("Paradoxal")
        
        # Capture all levels of detail for the Flight Recorder (Disk)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to prevent duplicate entries on reload
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # --- STREAM 1: THE FLIGHT RECORDER (DISK LOG) ---
        # Generates a timestamped filename (e.g. zerohour_20240128_120000.log)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"zerohour_{timestamp}.log"
        log_path = os.path.join(log_dir, log_filename)
        
        # Persistent File Handler
        file_handler = logging.FileHandler(
            log_path, 
            encoding='utf-8'
        )
        
        # Disk logs get full DEBUG detail for engineering review
        file_handler.setLevel(logging.DEBUG)
        
        # Format: [Time.Milliseconds] [Level] Message
        file_formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s', 
            datefmt='%H:%M:%S'
        )
        
        file_handler.setFormatter(file_formatter)
        
        # --- STREAM 2: THE UI BRIDGE (REAL-TIME TELEMETRY) ---
        self.ui_handler = UIHandler()
        
        # UI console only shows INFO level and higher to keep it readable for the admin
        self.ui_handler.setLevel(logging.INFO)
        
        # Simplified format for the UI console
        ui_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s', 
            datefmt='%H:%M:%S'
        )
        
        self.ui_handler.setFormatter(ui_formatter)
        
        # Attach both handlers to the Master Logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(self.ui_handler)
        
        self.logger.info(f"[TELEMETRY] Flight Recorder Initialized: {log_filename}")

    def get_logger(self):
        """
        Returns the configured logger instance for use across the application.
        """
        return self.logger