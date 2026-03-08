# ==============================================================================
# ZERO HOUR ROUTER: CONFIGURATION - v23.0
# ==============================================================================
# ROLE: Controller for Server Identity, Provisioning, and XML Settings.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 22 UPDATE (STEAMCMD FIX):
# FIX: 'ServerDeployWorker' now uses a "Double Tap" strategy.
#      - Pass 1: Bootstrap (steamcmd +quit) to allow self-update.
#      - Pass 2: Deploy (steamcmd +app_update) to download content.
# FIX: Prevents "Exit Code 7" errors on fresh installs.
# ==============================================================================

import os
import sys
import json
import shutil
import requests
import zipfile
import io
import subprocess
import time
from PySide6.QtCore import QObject, QTimer, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog, QLineEdit

# region [IMPORTS_CORE]
from core.app_state import state
# We try to import the bridge, fallback if missing to prevent boot crash
try:
    from core.settings_bridge import SettingsBridge
except ImportError:
    SettingsBridge = None
# endregion

# region [WORKER_THREADS]
class SteamCMDWorker(QThread):
    """
    Step A: Downloads and installs SteamCMD from Valve.
    """
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        self.download_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"

    def run(self):
        try:
            if not os.path.exists(self.target_dir):
                os.makedirs(self.target_dir, exist_ok=True)

            self.progress.emit("Downloading SteamCMD from Valve...")
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()

            self.progress.emit("Extracting Zip Archive...")
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall(self.target_dir)

            exe_path = os.path.join(self.target_dir, "steamcmd.exe")
            if os.path.exists(exe_path):
                self.finished.emit(True, "SteamCMD Installed Successfully.")
            else:
                self.finished.emit(False, "Extraction failed. steamcmd.exe not found.")

        except Exception as e:
            self.finished.emit(False, str(e))

class ServerDeployWorker(QThread):
    """
    Step B: Uses SteamCMD to download the 7D2D Dedicated Server (AppID 294420).
    Implements 'Double Tap' to handle first-run self-updates.
    """
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, steamcmd_path, install_dir):
        super().__init__()
        self.steamcmd_exe = steamcmd_path
        self.install_dir = install_dir
        self.app_id = "294420" # 7 Days to Die Dedicated Server

    def run(self):
        # --- PASS 1: BOOTSTRAP (Self-Update) ---
        self.log_signal.emit(">> PHASE 1: BOOTSTRAPPING STEAMCMD (SELF-UPDATE)...")
        if not self._run_steamcmd_process(["+quit"]):
            # Note: Code 7 implies update happened but restart needed. 
            # We don't fail here; we proceed to Pass 2 which acts as the restart.
            self.log_signal.emit(">> BOOTSTRAP COMPLETE. PROCEEDING TO DEPLOYMENT.")
        else:
            self.log_signal.emit(">> BOOTSTRAP COMPLETE.")

        # Small delay to ensure file locks are released
        time.sleep(2)

        # --- PASS 2: DEPLOYMENT (Download Game) ---
        self.log_signal.emit(f">> PHASE 2: DEPLOYING SERVER TO {self.install_dir}")
        
        # Command: +force_install_dir "PATH" +login anonymous +app_update 294420 validate +quit
        deploy_args = [
            "+force_install_dir", self.install_dir,
            "+login", "anonymous",
            "+app_update", self.app_id,
            "validate",
            "+quit"
        ]
        
        if self._run_steamcmd_process(deploy_args):
            self.finished_signal.emit(True, "Server Files Downloaded Successfully.")
        else:
            self.finished_signal.emit(False, "SteamCMD Download Failed (Check Logs).")

    def _run_steamcmd_process(self, args):
        """
        Helper to run steamcmd with specific args and stream output.
        Returns True if returncode is 0, else False.
        """
        cmd = [self.steamcmd_exe] + args
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Stream Output
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.log_signal.emit(clean_line)

            process.wait()
            
            # Special Case: Code 7 often means "I updated and quit". 
            # For the bootstrap phase, this is acceptable.
            # For deployment, it's usually an error.
            if process.returncode == 0:
                return True
            elif process.returncode == 7 and "+quit" in args and len(args) == 1:
                # Bootstrap code 7 is fine
                return True
            else:
                self.log_signal.emit(f"!! PROCESS EXITED WITH CODE: {process.returncode}")
                return False

        except Exception as e:
            self.log_signal.emit(f"!! EXCEPTION: {str(e)}")
            return False
# endregion

class ConfigRouter(QObject):
    def __init__(self, main_window):
        """
        Initialize the Configuration Router.
        """
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        
        # Internal State
        self.steam_worker = None
        self.deploy_worker = None
        self.registry_path = "admin_registry.json"
        
        # Initialize Logic Engines
        if SettingsBridge:
            self.settings_bridge = SettingsBridge(main_window)
        else:
            self.settings_bridge = None
            self.main_window.log_system_event("WARNING: SettingsBridge Module Missing.")
        
        self._setup_connections()
        self._load_initial_data()

    # region [INITIALIZATION]
    def _setup_connections(self):
        # Identity
        if hasattr(self.ui, 'btn_save_identity'):
            self.ui.btn_save_identity.clicked.connect(self.save_identity_data)
            
        # Provisioning
        if hasattr(self.ui, 'btn_init_tool'):
            self.ui.btn_init_tool.clicked.connect(self.install_steamcmd_tool)
            
        if hasattr(self.ui, 'btn_deploy_fresh'):
            self.ui.btn_deploy_fresh.clicked.connect(self.path_provision_new)

        if hasattr(self.ui, 'btn_browse_adopt'):
            self.ui.btn_browse_adopt.clicked.connect(self.path_adopt_existing)

        # XML Settings
        if hasattr(self.ui, 'btn_save_srv_settings'):
            self.ui.btn_save_srv_settings.clicked.connect(self.on_save_xml_settings)

    def _load_initial_data(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    registry = json.load(f)
                last_profile = registry.get("last_profile_id", "Default")
                self._load_profile_specifics(last_profile)
            except Exception as e:
                self.main_window.log_system_event(f"CONFIG LOAD ERROR: {e}")
        
        if self.settings_bridge:
            QTimer.singleShot(1000, self.settings_bridge.load_from_xml)

    def _load_profile_specifics(self, profile_id):
        profile_path = os.path.join("profiles", profile_id, "manifest_server.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                
                if hasattr(self.ui, 'txt_prof_name'):
                    self.ui.txt_prof_name.setText(data.get("server_name", ""))
                if hasattr(self.ui, 'txt_server_port'):
                    self.ui.txt_server_port.setText(data.get("server_port", "26900"))
                if hasattr(self.ui, 'txt_target_repo'):
                    self.ui.txt_target_repo.setText(data.get("mod_repo", ""))
                    
                self.main_window.log_system_event(f"CONFIG: Loaded profile '{profile_id}'")
            except Exception as e:
                pass
    # endregion

    # region [IDENTITY_LOGIC]
    def save_identity_data(self):
        name = self.ui.txt_prof_name.text().strip() if hasattr(self.ui, 'txt_prof_name') else "Unknown"
        port = self.ui.txt_server_port.text().strip() if hasattr(self.ui, 'txt_server_port') else "26900"
        repo = self.ui.txt_target_repo.text().strip() if hasattr(self.ui, 'txt_target_repo') else ""
        
        if not name:
            QMessageBox.warning(self.main_window, "Validation Error", "Profile Name cannot be empty.")
            return

        profile_data = {
            "server_name": name,
            "server_port": port,
            "mod_repo": repo,
            "last_updated": "Just Now"
        }

        profile_dir = os.path.join("profiles", name)
        os.makedirs(profile_dir, exist_ok=True)
        manifest_path = os.path.join(profile_dir, "manifest_server.json")
        
        try:
            with open(manifest_path, 'w') as f:
                json.dump(profile_data, f, indent=4)
                
            self._update_global_registry(name)
            state.target_repo = repo
            state.server_port = port
            
            self.main_window.log_system_event(f"PERSISTENCE: Saved profile '{name}' to disk.")
            QMessageBox.information(self.main_window, "Success", "Server Identity Saved Successfully.")
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Save Error", f"Could not write to disk:\n{e}")

    def _update_global_registry(self, active_profile_id):
        reg_data = {"last_profile_id": active_profile_id}
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(reg_data, f, indent=4)
        except Exception:
            pass
    # endregion

    # region [PROVISIONING_LOGIC]
    def install_steamcmd_tool(self):
        btn = getattr(self.ui, 'btn_init_tool', None)
        if btn:
            btn.setEnabled(False)
            btn.setText("DOWNLOADING...")
        
        target_dir = os.path.join(os.getcwd(), "steamcmd")
        self.main_window.log_system_event("STEAMCMD: Initialization started...")
        
        self.steam_worker = SteamCMDWorker(target_dir)
        self.steam_worker.progress.connect(self._on_steam_progress)
        self.steam_worker.finished.connect(self._on_steam_finished)
        self.steam_worker.start()

    def _on_steam_progress(self, msg):
        self.main_window.log_system_event(f"STEAMCMD: {msg}")

    def _on_steam_finished(self, success, msg):
        btn = getattr(self.ui, 'btn_init_tool', None)
        if success:
            if btn: 
                btn.setText("STEAMCMD READY")
                btn.setStyleSheet("color: #2ecc71; font-weight: bold;")
            QMessageBox.information(self.main_window, "Success", msg)
        else:
            if btn: 
                btn.setEnabled(True)
                btn.setText("RETRY STEP A")
            QMessageBox.critical(self.main_window, "Error", msg)

    def path_provision_new(self):
        steam_exe = os.path.join(os.getcwd(), "steamcmd", "steamcmd.exe")
        if not os.path.exists(steam_exe):
            QMessageBox.warning(self.main_window, "Prerequisite Missing", "Please run STEP A (Initialize SteamCMD) first.")
            return
            
        sel = QFileDialog.getExistingDirectory(self.main_window, "Select Install Location (Empty Folder)")
        if not sel:
            return

        btn = getattr(self.ui, 'btn_deploy_fresh', None)
        if btn:
            btn.setEnabled(False)
            btn.setText("DEPLOYING (CHECK LOGS)...")

        self.deploy_worker = ServerDeployWorker(steam_exe, sel)
        self.deploy_worker.log_signal.connect(self._on_deploy_log)
        self.deploy_worker.finished_signal.connect(self._on_deploy_finished)
        self.deploy_worker.start()

    def _on_deploy_log(self, text):
        log_box = getattr(self.ui, 'txt_setup_log', None)
        if log_box:
            log_box.append(text)
            sb = log_box.verticalScrollBar()
            sb.setValue(sb.maximum())

    def _on_deploy_finished(self, success, msg):
        btn = getattr(self.ui, 'btn_deploy_fresh', None)
        if btn:
            btn.setEnabled(True)
            btn.setText("STEP B: DOWNLOAD COMPLETE")
            
        if success:
            QMessageBox.information(self.main_window, "Success", "Server Installed Successfully.")
            self.main_window.log_system_event("DEPLOY: Installation Complete.")
        else:
            QMessageBox.critical(self.main_window, "Failure", f"Install Failed: {msg}")

    def path_adopt_existing(self):
        sel = QFileDialog.getExistingDirectory(self.main_window, "Select Existing Server")
        if sel:
            self.main_window.log_system_event(f"ADOPT: Targeted {sel}")
            if os.path.exists(os.path.join(sel, "7DaysToDieServer.exe")):
                QMessageBox.information(self.main_window, "Success", "Valid Server Folder Detected.")
                if self.settings_bridge:
                    self.settings_bridge.target_file = os.path.join(sel, "serverconfig.xml")
                    self.settings_bridge.load_from_xml()
            else:
                QMessageBox.warning(self.main_window, "Warning", "Could not find 7DaysToDieServer.exe in that folder.")
    # endregion

    # region [XML_SETTINGS_LOGIC]
    def on_save_xml_settings(self):
        if not self.settings_bridge:
            QMessageBox.critical(self.main_window, "Error", "Settings Bridge not initialized.")
            return

        btn = getattr(self.ui, 'btn_save_srv_settings', None)
        if btn:
            btn.setEnabled(False)
            btn.setText("SAVING TO XML...")

        success = self.settings_bridge.save_to_xml()
        
        if success:
            self.main_window.log_system_event("XML: Settings successfully written to serverconfig.xml")
            QMessageBox.information(self.main_window, "Success", "Settings Saved to XML.")
        else:
            self.main_window.log_system_event("XML: Failed to write file.")
            QMessageBox.warning(self.main_window, "Error", "Failed to save settings. Check permissions/path.")

        if btn:
            btn.setEnabled(True)
            btn.setText("COMMIT SETTINGS TO XML")
    # endregion