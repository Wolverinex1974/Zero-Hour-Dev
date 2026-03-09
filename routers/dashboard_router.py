# ==============================================================================
# ZERO HOUR ROUTER: DASHBOARD (REACTOR) - v23.2
# ==============================================================================
# ROLE: Controller for Server Process, Log Streaming, and System Events.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 23 UPDATE (RAT PARITY & TELNET):
# FIX: Integrated AdvancedRestartDialog for graceful shutdowns.
# FIX: Created ShutdownWorker (QThread) to execute Telnet countdown sequences
#      without freezing the main UI.
# FIX: Added 'pending_restart' logic to automatically boot the server back up.
# ==============================================================================

import os
import sys
import platform
import datetime
import time
from PySide6.QtCore import QObject, QProcess, Signal, QThread, QTimer

# region[WORKER_THREADS]
class ShutdownWorker(QThread):
    """
    Executes the Telnet connection, broadcasting, and shutdown sequence
    in a background thread to prevent the PyQt UI from freezing.
    """
    progress = Signal(str)
    finished_signal = Signal(bool, bool)

    def __init__(self, port, password, reason, total_seconds, is_countdown, do_restart):
        super().__init__()
        self.port = port
        self.password = password
        self.reason = reason
        self.total_seconds = total_seconds
        self.is_countdown = is_countdown
        self.do_restart = do_restart

    def run(self):
        try:
            from core.paradoxal_telnet import ParadoxalTelnet
            self.progress.emit(">> CONNECTING TO TELNET FOR SHUTDOWN...")
            telnet_client = ParadoxalTelnet("127.0.0.1", self.port)
            
            if not telnet_client.connect(self.password):
                self.progress.emit("!! TELNET CONNECTION FAILED. FALLING BACK TO HARD KILL.")
                self.finished_signal.emit(False, self.do_restart)
                return
                
            self.progress.emit(">> TELNET CONNECTED. SAVING WORLD...")
            telnet_client.send_command("sa")
            time.sleep(1)
            
            telnet_client.send_command(f"say \"[SERVER] {self.reason}\"")
            
            if self.is_countdown and self.total_seconds > 0:
                for remaining in range(self.total_seconds, 0, -1):
                    if remaining % 60 == 0:
                        minutes_left = remaining // 60
                        telnet_client.send_command(f"say \"[SERVER] Restarting in {minutes_left} minute(s)...\"")
                        self.progress.emit(f">> SHUTDOWN COUNTDOWN: {minutes_left} minute(s) remaining.")
                    elif remaining == 30 or remaining == 10 or remaining <= 5:
                        telnet_client.send_command(f"say \"[SERVER] Restarting in {remaining} seconds...\"")
                        self.progress.emit(f">> SHUTDOWN COUNTDOWN: {remaining} seconds remaining.")
                    
                    time.sleep(1)
            else:
                self.progress.emit(">> NO COUNTDOWN SELECTED. WAITING 5 SECONDS FOR BROADCAST.")
                time.sleep(5)
                
            self.progress.emit(">> FINAL SAVE BEFORE SHUTDOWN...")
            telnet_client.send_command("sa")
            time.sleep(1)
            
            self.progress.emit(">> SENDING SHUTDOWN COMMAND...")
            telnet_client.send_command("shutdown")
            time.sleep(2)
            
            telnet_client.close()
            self.finished_signal.emit(True, self.do_restart)
            
        except Exception as error_exception:
            self.progress.emit(f"!! TELNET ERROR: {str(error_exception)}")
            self.finished_signal.emit(False, self.do_restart)
# endregion

class DashboardRouter(QObject):
    server_status_changed = Signal(str)

    def __init__(self, main_window):
        """
        Initialize the Dashboard Router.
        """
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui 
        
        self.server_process = QProcess()
        self.server_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        self.is_running = False
        self.pending_restart = False
        
        self._setup_connections()
        self._init_ui_state()

    # region [INITIALIZATION]
    def _setup_connections(self):
        """
        Bind UI buttons to Logic functions.
        """
        if hasattr(self.ui, 'btn_start_server'):
            self.ui.btn_start_server.clicked.connect(self.start_server_sequence)
        
        if hasattr(self.ui, 'btn_stop_server'):
            self.ui.btn_stop_server.clicked.connect(self.initiate_kill_sequence)
        
        if hasattr(self.ui, 'btn_shutdown_dialog'):
             self.ui.btn_shutdown_dialog.clicked.connect(self.initiate_graceful_shutdown)

        if hasattr(self.ui, 'btn_open_root'):
            self.ui.btn_open_root.clicked.connect(lambda: self.open_file_explorer("root"))
        if hasattr(self.ui, 'btn_open_logs'):
            self.ui.btn_open_logs.clicked.connect(lambda: self.open_file_explorer("logs"))
        if hasattr(self.ui, 'btn_save_data'):
            self.ui.btn_save_data.clicked.connect(lambda: self.open_file_explorer("saves"))

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
        if hasattr(self.ui, 'btn_shutdown_dialog'): 
            self.ui.btn_shutdown_dialog.setEnabled(False)
    # endregion

    # region[LOGGING_CHANNELS]
    def append_log(self, text):
        """
        PUBLIC METHOD: Called by main.py and other routers.
        """
        self.append_system_log(text)

    def append_system_log(self, text):
        """
        Writes to 'txt_system_log' (Left Box).
        """
        if not text: return
        timestamp_string = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_line = f"{timestamp_string} {text}"
        
        if hasattr(self.ui, 'txt_system_log'):
            self.ui.txt_system_log.append(formatted_line)
            scrollbar_item = self.ui.txt_system_log.verticalScrollBar()
            scrollbar_item.setValue(scrollbar_item.maximum())

    def append_reactor_log(self, text):
        """
        Writes to 'txt_reactor_stream' (Right Box).
        """
        if not text: return
        
        if hasattr(self.ui, 'txt_reactor_stream'):
            self.ui.txt_reactor_stream.append(text)
            scrollbar_item = self.ui.txt_reactor_stream.verticalScrollBar()
            scrollbar_item.setValue(scrollbar_item.maximum())
    # endregion

    # region[REACTOR_LOGIC_START]
    def start_server_sequence(self):
        """
        Executes the server startup sequence.
        """
        self.append_system_log(">> INITIATING STARTUP SEQUENCE...")
        
        server_executable = "start_dedicated_server.bat" 
        working_directory = os.getcwd() 

        full_path = os.path.join(working_directory, server_executable)
        if not os.path.exists(full_path):
            self.append_system_log(f"!! CRITICAL: Could not find {server_executable}")
            self.append_system_log(f"!! SEARCHED: {full_path}")
            self.append_system_log("!! HINT: Did you run Provisioning Step B?")
            return

        if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(False)
        if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(True)
        if hasattr(self.ui, 'btn_shutdown_dialog'): self.ui.btn_shutdown_dialog.setEnabled(True)
        
        self.append_system_log(f"LAUNCHING: {server_executable}")
        self.server_process.setWorkingDirectory(working_directory)
        self.server_process.setProgram(full_path)
        self.server_process.start()
        
        self.update_status_led("BOOTING")
    # endregion

    # region[REACTOR_LOGIC_STOP]
    def initiate_kill_sequence(self):
        """
        Forcefully terminates the server process.
        """
        self.append_system_log(">> KILL SIGNAL SENT TO KERNEL.")
        self.server_process.kill()

    def initiate_graceful_shutdown(self):
        """
        Shows the RAT-Parity Advanced Restart Dialog, then spawns the ShutdownWorker.
        """
        from ui.dialogs import AdvancedRestartDialog
        
        shutdown_dialog = AdvancedRestartDialog(self.main_window)
        if shutdown_dialog.exec():
            reason_text = shutdown_dialog.combo_reason.currentText()
            do_restart_checked = shutdown_dialog.chk_restart.isChecked()
            is_countdown_checked = shutdown_dialog.radio_with_count.isChecked()
            
            minutes_value = shutdown_dialog.spin_min.value()
            seconds_value = shutdown_dialog.spin_sec.value()
            total_seconds_value = int((minutes_value * 60) + seconds_value)
            
            try:
                telnet_port = int(self.ui.txt_TelnetPort.text())
            except ValueError:
                telnet_port = 8081 
                
            telnet_password = self.ui.txt_TelnetPassword.text()
            
            self.append_system_log(">> INITIATING GRACEFUL SHUTDOWN SEQUENCE...")
            
            if hasattr(self.ui, 'btn_start_server'): self.ui.btn_start_server.setEnabled(False)
            if hasattr(self.ui, 'btn_stop_server'): self.ui.btn_stop_server.setEnabled(False)
            if hasattr(self.ui, 'btn_shutdown_dialog'): self.ui.btn_shutdown_dialog.setEnabled(False)
            
            self.shutdown_worker = ShutdownWorker(
                port=telnet_port,
                password=telnet_password,
                reason=reason_text,
                total_seconds=total_seconds_value,
                is_countdown=is_countdown_checked,
                do_restart=do_restart_checked
            )
            self.shutdown_worker.progress.connect(self.append_system_log)
            self.shutdown_worker.finished_signal.connect(self._on_shutdown_worker_finished)
            self.shutdown_worker.start()

    def _on_shutdown_worker_finished(self, success_status, do_restart_status):
        """
        Handles the completion of the background Telnet thread.
        """
        if not success_status:
            self.initiate_kill_sequence()
            
        if do_restart_status:
            self.pending_restart = True
    # endregion

    # region [PROCESS_HANDLER]
    def handle_process_output(self):
        """
        Reads stdout from the running process and sends it to the REACTOR LOG.
        """
        process_data = self.server_process.readAllStandardOutput()
        output_text = bytes(process_data).decode("utf-8", errors="ignore")
        
        clean_text = output_text.strip()
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
            if hasattr(self.ui, 'btn_shutdown_dialog'): self.ui.btn_shutdown_dialog.setEnabled(True)
        elif new_state == QProcess.ProcessState.NotRunning:
            self.update_status_led("OFFLINE")
            self.is_running = False
            if hasattr(self.ui, 'btn_shutdown_dialog'): self.ui.btn_shutdown_dialog.setEnabled(False)

    def handle_process_finished(self, exit_code, exit_status):
        """
        Triggered when the process actually ends.
        """
        self.append_system_log(f">> PROCESS TERMINATED (Code: {exit_code})")
        
        if hasattr(self.ui, 'btn_start_server'): 
            self.ui.btn_start_server.setEnabled(True)
        if hasattr(self.ui, 'btn_stop_server'): 
            self.ui.btn_stop_server.setEnabled(False)
        if hasattr(self.ui, 'btn_shutdown_dialog'): 
            self.ui.btn_shutdown_dialog.setEnabled(False)
            
        self.update_status_led("OFFLINE")
        
        if getattr(self, 'pending_restart', False):
            self.append_system_log(">> PERFORMING SCHEDULED RESTART...")
            self.pending_restart = False
            QTimer.singleShot(3000, self.start_server_sequence)
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
            path_to_open = os.path.join(os.getenv('APPDATA'), "7DaysToDie", "Saves")
            
        self.append_system_log(f">> OPENING EXPLORER: {target.upper()}")
        
        if platform.system() == "Windows":
            os.startfile(path_to_open)

    def update_status_led(self, status):
        """
        Updates the Status Label color and text.
        """
        if not hasattr(self.ui, 'lbl_watchdog_status'): return
        label_widget = self.ui.lbl_watchdog_status
        
        if status == "ONLINE":
            label_widget.setText("SYSTEM ONLINE")
            label_widget.setStyleSheet("color: #00FF00; font-weight: bold;") 
        elif status == "BOOTING":
            label_widget.setText("BOOTING UP")
            label_widget.setStyleSheet("color: #FFFF00; font-weight: bold;") 
        else:
            label_widget.setText("SYSTEM OFFLINE")
            label_widget.setStyleSheet("color: #FF0000; font-weight: bold;") 
            
        self.server_status_changed.emit(status)
    # endregion