# ==============================================================================
# ZERO HOUR ROUTER: DASHBOARD (REACTOR) - v23.0
# ==============================================================================
# ROLE: Controller for Server Process, Log Streaming, and System Events.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 23 UPDATE (LOGGING REPAIR):
# FIX: Split logging channels.
#      - Channel A: System Events -> txt_system_log (Left Box)
#      - Channel B: Reactor Stream -> txt_reactor_stream (Right Box)
# FIX: Wired 'handle_process_output' exclusively to Channel B.
# ==============================================================================

import os
import sys
import platform
import datetime
from PySide6.QtCore import QObject, QProcess, Signal

class DashboardRouter(QObject):
    # Signal emitted when server state changes (Online/Offline/Booting)
    server_status_changed = Signal(str)

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
        # Server Control Buttons
        if hasattr(self.ui, 'btn_start_server'):
            self.ui.btn_start_server.clicked.connect(self.start_server_sequence)
        
        if hasattr(self.ui, 'btn_stop_server'):
            self.ui.btn_stop_server.clicked.connect(self.initiate_kill_sequence)
        
        if hasattr(self.ui, 'btn_shutdown_dialog'):
             self.ui.btn_shutdown_dialog.clicked.connect(self.initiate_graceful_shutdown)

        # File System Navigation (Tactical Toolbar)
        if hasattr(self.ui, 'btn_open_root'):
            self.ui.btn_open_root.clicked.connect(lambda: self.open_file_explorer("root"))
        if hasattr(self.ui, 'btn_open_logs'):
            self.ui.btn_open_logs.clicked.connect(lambda: self.open_file_explorer("logs"))
        if hasattr(self.ui, 'btn_save_data'):
            self.ui.btn_save_data.clicked.connect(lambda: self.open_file_explorer("saves"))

        # Process Signals (The Reactor Core)
        self.server_process.readyReadStandardOutput.connect(self.handle_process_output)
        self.server_process.stateChanged.connect(self.handle_state_change)
        self.server_process.finished.connect(self.handle_process_finished)

    def _init_ui_state(self):
        """
        Set initial button states based on assumption that server is OFF.
        """
        self.update_status_led("OFFLINE")
        if hasattr(self.ui, 'btn_start_server'): 
            self.ui.btn_start_server.setEnabled(True)
        if hasattr(self.ui, 'btn_stop_server'): 
            self.ui.btn_stop_server.setEnabled(False)
    # endregion

    # region [LOGGING_CHANNELS]
    def append_log(self, text):
        """
        PUBLIC METHOD: Called by main.py and other routers.
        Routes messages to the SYSTEM LOG (Left Box).
        """
        self.append_system_log(text)

    def append_system_log(self, text):
        """
        Writes to 'txt_system_log' (Left Box).
        Used for internal manager events (Config saved, Watchdog triggered, etc).
        """
        if not text: return
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_line = f"{timestamp} {text}"
        
        if hasattr(self.ui, 'txt_system_log'):
            self.ui.txt_system_log.append(formatted_line)
            # Auto-scroll
            sb = self.ui.txt_system_log.verticalScrollBar()
            sb.setValue(sb.maximum())

    def append_reactor_log(self, text):
        """
        Writes to 'txt_reactor_stream' (Right Box).
        Used EXCLUSIVELY for the dedicated server console output.
        """
        if not text: return
        # Note: Server output often has its own timestamps, but we prepend ours just in case
        # timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        # formatted_line = f"{timestamp} {text}"
        
        # Raw output is usually better for the console stream
        if hasattr(self.ui, 'txt_reactor_stream'):
            self.ui.txt_reactor_stream.append(text)
            # Auto-scroll
            sb = self.ui.txt_reactor_stream.verticalScrollBar()
            sb.setValue(sb.maximum())
    # endregion

    # region [REACTOR_LOGIC_START]
    def start_server_sequence(self):
        """
        Executes the server startup sequence.
        """
        self.append_system_log(">> INITIATING STARTUP SEQUENCE...")
        
        # 1. Locate the Executable
        server_executable = "start_dedicated_server.bat" 
        working_dir = os.getcwd() 

        # Check if file exists
        full_path = os.path.join(working_dir, server_executable)
        if not os.path.exists(full_path):
            self.append_system_log(f"!! CRITICAL: Could not find {server_executable}")
            self.append_system_log(f"!! SEARCHED: {full_path}")
            self.append_system_log("!! HINT: Did you run Provisioning Step B?")
            return

        # 2. Lock UI
        if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(False)
        if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(True)
        
        # 3. Launch QProcess
        self.append_system_log(f"LAUNCHING: {server_executable}")
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
        self.append_system_log(">> KILL SIGNAL SENT TO KERNEL.")
        self.server_process.kill()

    def initiate_graceful_shutdown(self):
        """
        Sends a graceful shutdown command via Telnet (Placeholder for Logic).
        """
        self.append_system_log(">> GRACEFUL SHUTDOWN TRIGGERED (Telnet Link Pending).")
    # endregion

    # region [PROCESS_HANDLER]
    def handle_process_output(self):
        """
        Reads stdout from the running process and sends it to the REACTOR LOG.
        """
        data = self.server_process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="ignore")
        
        # Clean up whitespace
        clean_text = text.strip()
        if clean_text:
            self.append_reactor_log(clean_text)

    def handle_state_change(self, new_state):
        """
        Reacts to QProcess state changes (NotRunning, Starting, Running).
        """
        if new_state == QProcess.ProcessState.Running:
            self.update_status_led("ONLINE")
            self.append_system_log(">> REACTOR STATUS: ONLINE")
            self.is_running = True
        elif new_state == QProcess.ProcessState.NotRunning:
            self.update_status_led("OFFLINE")
            self.is_running = False

    def handle_process_finished(self, exit_code, exit_status):
        """
        Triggered when the process actually ends.
        """
        self.append_system_log(f">> PROCESS TERMINATED (Code: {exit_code})")
        
        if hasattr(self.ui, 'btn_start_server'): 
            self.ui.btn_start_server.setEnabled(True)
        if hasattr(self.ui, 'btn_stop_server'): 
            self.ui.btn_stop_server.setEnabled(False)
            
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
        elif target == "saves":
            # Try to guess saves location or use default
            path_to_open = os.path.join(os.getenv('APPDATA'), "7DaysToDie", "Saves")
            
        self.append_system_log(f">> OPENING EXPLORER: {target.upper()}")
        
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