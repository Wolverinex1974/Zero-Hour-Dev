# =========================================================
# ZERO HOUR CORE: REACTOR CONTROLLER - v21.2
# =========================================================
# ROLE: Server Lifecycle Orchestration & Bi-Directional Data
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16.5 UPDATE:
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# SURGERY: Danger Zone Wired. LogTailer feeds EconomyParser.
# FEATURE: Added Asynchronous QTimer Countdown Engine to handle
#          the new Advanced Restart Dialog logic.
# FIX: Added class-level ledger_signal for stable UI binding.
# =========================================================

import os
import logging
import time
import re
from PySide6.QtCore import QObject, Signal, QThread, QTimer

# Custom Industrial Logic Imports
from core.app_state import state
from core.reactor_engine import LogTailer, ServerWatchdog
from core.paradoxal_telnet import ParadoxalTelnet
from core.archiver import LogRotator
from core.validator import get_dynamic_log_path, get_active_server_pid
from core.economy_parser import EconomyParser

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class TelematicsWorker(QThread):
    """
    Background Intelligence Agent.
    Manages the Broadcast Queue.
    Now relies on ReactorController for actual transmission via Signals.
    """
    request_broadcast_signal = Signal(str)
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.broadcast_queue = list()
        self.broadcast_index = 0
        self.last_broadcast_time = 0
        self.broadcast_interval = 600 # 10 Minutes default
        self.siege_active = False # Controlled by Reactor

    def run(self):
        self.is_running = True
        log.info(" Broadcast Engine Active.")
        
        while self.is_running:
            try:
                # Only broadcast if server is running and NOT in siege mode
                if state.server_process_active and not self.siege_active:
                    self.process_broadcast_queue()
                
                # Sleep cycle (Checks every 5 seconds)
                for _ in range(5):
                    if not self.is_running: 
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_signal.emit(f" Loop Error: {str(e)}")
                time.sleep(10)

    def process_broadcast_queue(self):
        """ Rotates through the broadcast list and requests sends. """
        queue_size = len(self.broadcast_queue)
        if queue_size == 0: 
            return
        
        current_time = time.time()
        if (current_time - self.last_broadcast_time) > self.broadcast_interval:
            
            # Safe extraction without brackets
            msg = self.broadcast_queue.__getitem__(self.broadcast_index)
            
            # Request Reactor to send this via Persistent Telnet
            self.request_broadcast_signal.emit(msg)
            
            # Rotate Index safely
            self.broadcast_index = (self.broadcast_index + 1) % queue_size
            self.last_broadcast_time = current_time

    def stop(self):
        self.is_running = False
        self.wait()

class ReactorController(QObject):
    """
    The Command Hub of the Manager.
    Orchestrates the server process and holds the MASTER TELNET CONNECTION.
    """
    # Signals to communicate status and logs back to the Main UI
    status_update_signal = Signal(str, str) 
    log_line_signal = Signal(str) 
    system_log_signal = Signal(str) 
    ledger_signal = Signal() # Phase 16.5: Stable Bridge for UI Tab 6

    def __init__(self, database_instance=None):
        super().__init__()
        
        # Link to the Master Vault (SQLite)
        self.db = database_instance
        
        self.watchdog = None
        self.log_tailer = None
        self.telematics = None
        self.economy_parser = None
        
        # Persistent Telnet Client
        self.telnet_client = None 
        self.telnet_port = 8081
        self.telnet_pass = ""
        
        # Telemetry Timer (Replaces Threaded Polling)
        self.telemetry_timer = QTimer()
        self.telemetry_timer.setInterval(60000) # Poll every 60 seconds
        self.telemetry_timer.timeout.connect(self.perform_telemetry_sweep)
        
        # Advanced Restart Engine (Phase 16.5)
        self.restart_pending = False
        self.pending_restart_args = dict()
        self.is_restarting = False
        self.countdown_remaining = 0
        self.countdown_reason = ""
        
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._countdown_tick)

    def start_reactor(self):
        """
        Initiates the Server Boot Sequence or seamlessly Attaches 
        to a running server if Zero Hour was restarted.
        """
        if not state.server_path:
            log.error(" Aborted: No server path defined.")
            return

        # 0. VEIN METHOD: Check for existing process to enable Self-Healing Reconnection
        is_running, pid = get_active_server_pid(state.server_path)
        attach_mode = False
        
        if is_running:
            log.warning(f" Active server found (PID: {pid}). Initiating Sovereign Reconnection...")
            self.system_log_signal.emit(f"SOVEREIGN RECONNECTION: Attaching to PID {pid}...")
            attach_mode = True
        elif state.server_process_active:
            log.warning(" Blocked: Server is already marked active but no PID found.")
            return
        else:
            # 1. PRE-FLIGHT: ROTATE LOGS (Only if booting a fresh server)
            self.system_log_signal.emit("PRE-FLIGHT: Archiving previous session logs...")
            LogRotator.rotate_logs(state.server_path)

            # 2. Verification of Executable
            exe_path = os.path.join(state.server_path, "7DaysToDieServer.exe")
            if not os.path.exists(exe_path):
                log.error(f" Executable missing: {exe_path}")
                self.system_log_signal.emit("ERROR: 7DaysToDieServer.exe not found.")
                return

        # 3. Config Load (Telnet)
        if state.registry:
            # Safely get port/pass from the loaded registry (Context aware)
            self.telnet_port = int(state.registry.get("srv_TelnetPort", 8081))
            self.telnet_pass = state.registry.get("srv_TelnetPassword", "")
            
        # Initialize Persistent Telnet Object (Does not connect yet)
        self.telnet_client = ParadoxalTelnet("127.0.0.1", self.telnet_port)

        # 4. Initialize Log Tailer (Using Dynamic Path Hunter)
        log_file_path = get_dynamic_log_path(state.server_path)
        log.info(f" Attaching Intelligence Tailer to: {log_file_path}")
        
        self.log_tailer = LogTailer(log_file_path, self.db)
        
        # 4.5 Initialize Economy Parser (The Danger Zone Wiring)
        log.info(" Initializing Economy Parser.")
        self.economy_parser = EconomyParser(self.db)
        self.economy_parser.telnet_signal.connect(self.execute_telnet_command)
        self.economy_parser.ledger_signal.connect(self.ledger_signal.emit)
        
        # Wire Tailer to Hub and Parser
        self.log_tailer.line_signal.connect(self.process_new_log_line)
        self.log_tailer.line_signal.connect(self.economy_parser.process_log_line)
        
        self.log_tailer.start()

        # 5. Initialize Watchdog
        log.info(" Spawning Server Watchdog.")
        self.watchdog = ServerWatchdog(state.server_path)
        
        # Pass attachment flags to the Watchdog so it doesn't double-boot the server
        if attach_mode:
            self.watchdog.attach_mode = True
            self.watchdog.attached_pid = pid
        else:
            self.watchdog.attach_mode = False
            self.watchdog.attached_pid = None
            
        self.watchdog.is_running = True
        self.watchdog.log_signal.connect(self.handle_engine_telemetry)
        self.watchdog.status_signal.connect(self.handle_status_transition)
        self.watchdog.start()
        
        # 6. Initialize Telematics (Broadcast Logic Only)
        log.info(" Spawning Telematics Engine.")
        self.telematics = TelematicsWorker()
        self.telematics.log_signal.connect(self.handle_engine_telemetry)
        
        # Connect broadcast requests to the main executor via safe lambda
        def make_say_cmd(msg):
            return f'say "{msg}"'
            
        self.telematics.request_broadcast_signal.connect(lambda msg: self.execute_telnet_command(make_say_cmd(msg)))
        self.telematics.start()
        
        # 7. Start Telemetry Loop (The Heartbeat)
        self.telemetry_timer.start()
        
        # Update global state
        state.update_status("server_process_active", True)
        state.update_status("watchdog_running", True)
        
        if attach_mode:
            self.handle_status_transition(f"STATUS: ONLINE (PID {pid})", "#2ecc71")

    def stop_reactor(self):
        """
        Gracefully terminates the server process.
        """
        log.info(" Shutdown sequence initiated.")
        self.telemetry_timer.stop()
        self.countdown_timer.stop()
        self.is_restarting = False
        
        # Close persistent connection
        if self.telnet_client:
            self.telnet_client.close()

        if self.telematics:
            self.telematics.stop()

        if self.watchdog:
            self.watchdog.is_running = False
            self.watchdog.auto_restart = False

        if self.log_tailer:
            self.log_tailer.is_running = False
            
        state.update_status("server_process_active", False)
        state.update_status("watchdog_running", False)
        self.handle_status_transition("STATUS: OFFLINE", "#95a5a6")

    def perform_telemetry_sweep(self):
        """
        Executed every 60 seconds by QTimer.
        1. Ensures Telnet is connected.
        2. Sends 'gettime'.
        3. Updates Siege Status.
        """
        if not self.telnet_client: 
            return

        # A. Auto-Connect / Reconnect Logic
        if not self.telnet_client.is_authenticated:
            connected = self.telnet_client.connect(self.telnet_pass)
            if not connected:
                return 

        # B. Send Time Query
        response = self.telnet_client.send_command("gettime")
        
        if response:
            self.parse_game_time(response)

    def parse_game_time(self, response_str):
        """ Parses 'Day 49, 14:30' for Siege Logic. """
        match = re.search(r"Day (\d+), (\d+):(\d+)", response_str)
        if match:
            day = int(match.group(1))
            hour = int(match.group(2))
            
            is_bm_day = (day % 7 == 0)
            is_post_bm_day = (day % 7 == 1)
            siege_active = False
            
            if is_bm_day and hour >= 18:
                siege_active = True
            elif is_post_bm_day and hour < 10:
                siege_active = True
                
            # Update Telematics Worker
            if self.telematics:
                self.telematics.siege_active = siege_active
                
            # Check for Deferred Restart
            if self.restart_pending and not siege_active:
                self.restart_pending = False
                self.system_log_signal.emit("SIEGE LIFTED. EXECUTING DEFERRED RESTART.")
                
                # Fetch pending arguments
                m = self.pending_restart_args.get("minutes", 0)
                s = self.pending_restart_args.get("seconds", 30)
                r = self.pending_restart_args.get("reason", "Server restarting.")
                
                self.schedule_restart(minutes=m, seconds=s, reason=r)

    def schedule_restart(self, minutes=0, seconds=30, reason="Server restarting.", override_siege=False):
        """
        Initiates the Advanced Countdown protocol. 
        """
        is_siege = False
        if self.telematics:
            is_siege = self.telematics.siege_active
        
        if is_siege and not override_siege:
            log.warning(" SIEGE PROTOCOL: Restart Delayed.")
            self.system_log_signal.emit("WARNING: BLOODMOON ACTIVE. RESTART DELAYED.")
            self.execute_telnet_command('say "COMMAND INTERCEPT: Server Restart Delayed due to Bloodmoon."')
            self.restart_pending = True
            
            self.pending_restart_args.update({"minutes": minutes})
            self.pending_restart_args.update({"seconds": seconds})
            self.pending_restart_args.update({"reason": reason})
            return

        self.system_log_signal.emit(f"INITIATING RESTART COUNTDOWN: {minutes}m {seconds}s")
        self.countdown_remaining = (minutes * 60) + seconds
        self.countdown_reason = reason
        self.is_restarting = True
        
        # Immediately announce and start the 1-second background tick
        self._announce_countdown()
        self.countdown_timer.start(1000)

    def _countdown_tick(self):
        """ The asynchronous heart of the countdown sequence. """
        if not self.is_restarting:
            self.countdown_timer.stop()
            return
            
        self.countdown_remaining = self.countdown_remaining - 1
        
        if self.countdown_remaining <= 0:
            self.countdown_timer.stop()
            self.execute_telnet_command('say "SERVER RESTART IMMINENT (INITIATING SHUTDOWN)"')
            self.execute_telnet_command("saveworld")
            # Allow 3 seconds for the saveworld command to commit before dropping the process
            QTimer.singleShot(3000, self.stop_reactor)
            return
            
        # Announce at specific broadcast intervals
        intervals = list((300, 120, 60, 30, 10, 5, 4, 3, 2, 1))
        if self.countdown_remaining in intervals:
            self._announce_countdown()

    def _announce_countdown(self):
        """ Formats and broadcasts the remaining time via Telnet. """
        mins = self.countdown_remaining // 60
        secs = self.countdown_remaining % 60
        
        time_str = ""
        if mins > 0:
            time_str = f"{mins} minute(s)"
            if secs > 0:
                time_str = f"{time_str} and {secs} second(s)"
        else:
            time_str = f"{secs} seconds"
            
        self.execute_telnet_command(f'say "WARNING: {self.countdown_reason} Restart in {time_str}."')

    def process_new_log_line(self, line):
        self.log_line_signal.emit(line)
        
        # Phase 16: Telemetry Router Placeholder
        if "ZH_CORE" in line:
            pass

    def execute_telnet_command(self, command_string):
        """
        Sends a command using the MASTER persistent connection.
        """
        if not self.telnet_client: 
            return

        if not self.telnet_client.is_authenticated:
            if not self.telnet_client.connect(self.telnet_pass):
                self.system_log_signal.emit("TELNET ERROR: Not connected.")
                return

        response = self.telnet_client.send_command(command_string)
        if response:
            log.debug(f" Executed: {command_string}")
        else:
            log.warning(f" Command failed: {command_string}")

    def handle_status_transition(self, label, color):
        if "ONLINE" in label:
            state.update_status("atlas_status", "ONLINE")
        elif "CRASHED" in label:
            state.update_status("atlas_status", "MAINTENANCE")
        else:
            state.update_status("atlas_status", "OFFLINE")
            
        self.status_update_signal.emit(label, color)

    def handle_engine_telemetry(self, message):
        self.system_log_signal.emit(message)