import os
import sys
import platform
import datetime
from PySide6.QtCore import QObject, QProcess, Signal

# region [METADATA]
# FILE: routers/dashboard_router.py
# DESC: Controller logic for the Main Dashboard (Reactor)
# AUTH: Phase 21 Refactor - v21.2
# -----------------------------------------------------------------------------
# RESPONSIBILITIES:
# 1. Server Process Management (Start/Stop/Kill)
# 2. Log Streaming (Standard Output capture)
# 3. Quick Actions (Folder navigation)
# 4. Status LED Updates
# endregion

class DashboardRouter(QObject):
    # region [SIGNALS]
    server_status_changed = Signal(str)  # "ONLINE", "OFFLINE", "BOOTING"
    # endregion

    def __init__(self, main_window):
        """
        Initialize the Dashboard Router.
        :param main_window: Reference to the main application window (UI access).
        """
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui  # Direct access to ZeroHourLayout
        
        # Process Management
        self.server_process = QProcess()
        self.server_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        # State Tracking
        self.is_running = False
        
        # Initialize Connections
        self._setup_connections()
        self._init_ui_state()

    # region [INITIALIZATION]
    def _setup_connections(self):
        """
        Bind UI buttons to Logic functions.
        """
        # Server Control Buttons - Direct Access
        if hasattr(self.ui, 'btn_start_server'):
            self.ui.btn_start_server.clicked.connect(self.start_server_sequence)
        
        if hasattr(self.ui, 'btn_stop_server'):
            self.ui.btn_stop_server.clicked.connect(self.initiate_kill_sequence)
        
        if hasattr(self.ui, 'btn_shutdown_dialog'):
             self.ui.btn_shutdown_dialog.clicked.connect(self.initiate_graceful_shutdown)

        # File System Navigation
        if hasattr(self.ui, 'btn_open_root'):
            self.ui.btn_open_root.clicked.connect(lambda: self.open_file_explorer("root"))
        if hasattr(self.ui, 'btn_open_logs'):
            self.ui.btn_open_logs.clicked.connect(lambda: self.open_file_explorer("logs"))

        # Process Signals
        self.server_process.readyReadStandardOutput.connect(self.handle_process_output)
        self.server_process.stateChanged.connect(self.handle_state_change)
        self.server_process.finished.connect(self.handle_process_finished)

    def _init_ui_state(self):
        """
        Set initial button states based on assumption that server is OFF.
        """
        self.update_status_led("OFFLINE")
        if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(True)
        if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(False)
    # endregion

    # region [REACTOR_LOGIC_START]
    def start_server_sequence(self):
        """
        Executes the server startup sequence.
        """
        self.append_log(">> INITIATING STARTUP SEQUENCE...")
        
        # 1. Locate the Executable
        server_executable = "start_dedicated_server.bat" 
        working_dir = os.getcwd() 

        # Check if file exists
        full_path = os.path.join(working_dir, server_executable)
        if not os.path.exists(full_path):
            self.append_log(f"!! CRITICAL: Could not find {server_executable}")
            self.append_log(f"!! SEARCHED: {full_path}")
            return

        # 2. Lock UI
        if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(False)
        if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(True)
        
        # 3. Launch QProcess
        self.server_process.setWorkingDirectory(working_dir)
        self.server_process.setProgram(full_path)
        self.server_process.start()
        
        self.update_status_led("BOOTING")
    # endregion

    # region [REACTOR_LOGIC_STOP]
    def initiate_kill_sequence(self):
        """
        Forcefully terminates the server process.
        """
        self.append_log(">> KILL SIGNAL SENT.")
        self.server_process.kill()

    def initiate_graceful_shutdown(self):
        """
        Sends a graceful shutdown command via Telnet (Placeholder for Logic).
        """
        self.append_log(">> GRACEFUL SHUTDOWN TRIGGERED (Telnet Link Pending).")
    # endregion

    # region [LOG_STREAMING]
    def handle_process_output(self):
        """
        Reads stdout from the running process and appends it to the text area.
        """
        data = self.server_process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore")
        self.append_log(text.strip())

    def append_log(self, text):
        """
        Helper to append text to the dashboard console widget.
        """
        if not text: return
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_line = f"{timestamp} {text}"
        
        # Direct Access to Widget
        if hasattr(self.ui, 'txt_reactor_stream'):
            self.ui.txt_reactor_stream.append(formatted_line)
            # Auto-scroll logic is usually handled by the widget's default behavior or:
            # sb = self.ui.txt_reactor_stream.verticalScrollBar()
            # sb.setValue(sb.maximum())
    # endregion

    # region [PROCESS_STATE_HANDLING]
    def handle_state_change(self, new_state):
        """
        Reacts to QProcess state changes (NotRunning, Starting, Running).
        """
        if new_state == QProcess.ProcessState.Running:
            self.update_status_led("ONLINE")
            self.is_running = True
        elif new_state == QProcess.ProcessState.NotRunning:
            self.update_status_led("OFFLINE")
            self.is_running = False

    def handle_process_finished(self, exit_code, exit_status):
        """
        Triggered when the process actually ends.
        """
        self.append_log(f">> PROCESS TERMINATED (Code: {exit_code})")
        if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(True)
        if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(False)
        self.update_status_led("OFFLINE")
    # endregion

    # region [UTILITIES]
    def open_file_explorer(self, target):
        """
        Opens Windows Explorer to a specific directory.
        """
        path_to_open = os.getcwd()
        
        if target == "logs":
            path_to_open = os.path.join(path_to_open, "7DaysToDie_Data")
            
        self.append_log(f">> OPENING EXPLORER: {target.upper()}")
        
        if platform.system() == "Windows":
            os.startfile(path_to_open)

    def update_status_led(self, status):
        """
        Updates the Status Label color and text.
        """
        if not hasattr(self.ui, 'lbl_watchdog_status'): return
        label = self.ui.lbl_watchdog_status
        
        if status == "ONLINE":
            label.setText("SYSTEM ONLINE")
            label.setStyleSheet("color: #00FF00; font-weight: bold;") # Green
        elif status == "BOOTING":
            label.setText("BOOTING UP")
            label.setStyleSheet("color: #FFFF00; font-weight: bold;") # Yellow
        else:
            label.setText("SYSTEM OFFLINE")
            label.setStyleSheet("color: #FF0000; font-weight: bold;") # Red
            
        self.server_status_changed.emit(status)
    # endregion