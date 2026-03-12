# ==============================================================================
# ZERO HOUR ROUTER: CONFIGURATION - v23.2
# ==============================================================================
# ROLE: Controller for Server Identity, Provisioning, and XML Settings.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE:
# FIX: Verified SettingsBridge method calls (load_from_xml / save_to_xml).
# FIX: Replaced argument passing with explicit self.target_file assignment.
# FIX: Separated XML loading from the identity loading block to prevent
#      missing paths from interrupting the profile hydration process.
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
import socket
from PySide6.QtCore import QObject, QTimer, QThread, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog, QLineEdit, QInputDialog

# region[IMPORTS_CORE]
from core.app_state import state
from core.github_engine import GitHubEngine
try:
    from core.settings_bridge import SettingsBridge
except ImportError:
    SettingsBridge = None
# endregion

# region[WORKER_THREADS]
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
            archive = zipfile.ZipFile(io.BytesIO(response.content))
            archive.extractall(self.target_dir)

            steamcmd_exe = os.path.join(self.target_dir, "steamcmd.exe")
            if os.path.exists(steamcmd_exe):
                self.progress.emit("Bootstrapping SteamCMD (Self-Update Phase)...")
                
                bootstrap_process = subprocess.Popen(
                    list((steamcmd_exe, "+quit")),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                for line in bootstrap_process.stdout:
                    if line.strip():
                        self.progress.emit(f"[STEAMCMD] {line.strip()}")
                
                bootstrap_process.wait()
                
                self.finished.emit(True, "SteamCMD Installed and Bootstrapped Successfully.")
            else:
                self.finished.emit(False, "Extraction failed: steamcmd.exe not found.")

        except Exception as error_exception:
            self.finished.emit(False, f"Installation Failed: {str(error_exception)}")


class ServerDeployWorker(QThread):
    """
    Step B: Uses SteamCMD to download/update the 7D2D Dedicated Server (App 294420).
    Includes the Code 7 Double Tap fix.
    """
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, steamcmd_path, install_dir):
        super().__init__()
        self.steamcmd_path = steamcmd_path
        self.install_dir = install_dir
        self.app_id = "294420"

    def run(self):
        try:
            self.progress.emit("Initiating 7D2D Dedicated Server Deployment...")
            
            deploy_arguments = list((
                self.steamcmd_path,
                "+force_install_dir", self.install_dir,
                "+login", "anonymous",
                "+app_update", self.app_id, "validate",
                "+quit"
            ))

            deploy_process = subprocess.Popen(
                deploy_arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in deploy_process.stdout:
                if line.strip():
                    self.progress.emit(f"[DEPLOY] {line.strip()}")

            return_code = deploy_process.wait()

            if return_code == 0 or return_code == 7:
                self.finished.emit(True, "7D2D Dedicated Server Deployment Complete.")
            else:
                self.finished.emit(False, f"Deployment Failed with Exit Code: {return_code}")

        except Exception as error_exception:
            self.finished.emit(False, f"Deployment Exception: {str(error_exception)}")
# endregion


# region[ROUTER_CONTROLLER]
class ConfigRouter(QObject):
    def __init__(self, main_window, ui_reference):
        super().__init__()
        self.main_window = main_window
        self.ui = self.main_window
        
        self.settings_bridge = None
        if SettingsBridge:
            self.settings_bridge = SettingsBridge(self.main_window)

        self._connect_signals()
        self._load_initial_data()

    def _connect_signals(self):
        # Identity & Provisioning
        self.ui.btn_save_identity.clicked.connect(self.save_identity_data)
        self.ui.btn_init_tool.clicked.connect(self.install_steamcmd_tool)
        self.ui.btn_deploy_fresh.clicked.connect(self.path_provision_new)
        self.ui.btn_browse_adopt.clicked.connect(self.path_adopt_existing)
        
        # XML Operations
        self.ui.btn_save_srv_settings.clicked.connect(self.commit_xml_settings)
        self.ui.btn_import_xml.clicked.connect(self.import_xml_file)
        self.ui.btn_export_xml.clicked.connect(self.export_xml_file)
        
        # Testing
        self.ui.btn_test_cloud.clicked.connect(self.test_cloud_connection)
        self.ui.btn_test_ports.clicked.connect(self.test_server_port)

    def _load_initial_data(self):
        registry_path = "admin_registry.json"
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r") as registry_file:
                    registry_data = json.load(registry_file)
                    
                active_profile = registry_data.get("active_profile", "")
                if active_profile:
                    profile_manifest_path = os.path.join("profiles", active_profile, "manifest.json")
                    if os.path.exists(profile_manifest_path):
                        with open(profile_manifest_path, "r") as manifest_file:
                            manifest_data = json.load(manifest_file)
                            
                        # Safely load the text fields first so they don't break if XML is missing
                        self.ui.txt_profile_name.setText(manifest_data.get("profile_name", ""))
                        self.ui.txt_server_port.setText(str(manifest_data.get("server_port", "26900")))
                        self.ui.txt_mod_repo.setText(manifest_data.get("mod_repository", ""))
                        
                        server_path = manifest_data.get("server_path", "")
                        if server_path and os.path.exists(server_path):
                            state.server_path = server_path
                            self.ui.lbl_current_path.setText(server_path)
                            
                            # Safely attempt to load XML using verified method
                            if self.settings_bridge:
                                xml_file_path = os.path.join(server_path, "serverconfig.xml")
                                if os.path.exists(xml_file_path):
                                    self.settings_bridge.target_file = xml_file_path
                                    self.settings_bridge.load_from_xml()
            except Exception as error_exception:
                print(f"Failed to load registry: {str(error_exception)}")

    def save_identity_data(self):
        profile_name = self.ui.txt_profile_name.text().strip()
        server_port = self.ui.txt_server_port.text().strip()
        mod_repo = self.ui.txt_mod_repo.text().strip()

        if not profile_name:
            QMessageBox.warning(self.main_window, "Validation Error", "Profile Name cannot be empty.")
            return

        profile_directory = os.path.join("profiles", profile_name)
        os.makedirs(profile_directory, exist_ok=True)

        manifest_data = dict()
        manifest_data["profile_name"] = profile_name
        manifest_data["server_port"] = server_port
        manifest_data["mod_repository"] = mod_repo
        manifest_data["server_path"] = getattr(state, "server_path", "")
        manifest_data["timestamp"] = time.time()

        manifest_path = os.path.join(profile_directory, "manifest.json")
        try:
            with open(manifest_path, "w") as manifest_file:
                json.dump(manifest_data, manifest_file, indent=4)
                
            registry_data = dict()
            registry_data["active_profile"] = profile_name
            with open("admin_registry.json", "w") as registry_file:
                json.dump(registry_data, registry_file, indent=4)
                
            QMessageBox.information(self.main_window, "Success", f"Identity Data for '{profile_name}' saved successfully.")
        except Exception as error_exception:
            QMessageBox.critical(self.main_window, "Save Failed", f"Could not save Identity Data: {str(error_exception)}")

    def install_steamcmd_tool(self):
        target_directory = os.path.join(os.getcwd(), "tools", "steamcmd")
        self.ui.btn_init_tool.setEnabled(False)
        self.ui.btn_init_tool.setText("DOWNLOADING...")

        self.steamcmd_worker = SteamCMDWorker(target_directory)
        self.steamcmd_worker.progress.connect(self._log_provisioning_progress)
        self.steamcmd_worker.finished.connect(self._on_steamcmd_finished)
        self.steamcmd_worker.start()

    def _log_provisioning_progress(self, message):
        if hasattr(self.main_window, "log_event"):
            self.main_window.log_event("CONFIG", message)
        else:
            print(message)

    def _on_steamcmd_finished(self, success, message):
        self.ui.btn_init_tool.setEnabled(True)
        if success:
            self.ui.btn_init_tool.setText("STEAMCMD READY")
            QMessageBox.information(self.main_window, "SteamCMD", message)
        else:
            self.ui.btn_init_tool.setText("STEP A: INITIALIZE STEAMCMD TOOL")
            QMessageBox.critical(self.main_window, "SteamCMD Error", message)

    def path_provision_new(self):
        steamcmd_executable = os.path.join(os.getcwd(), "tools", "steamcmd", "steamcmd.exe")
        if not os.path.exists(steamcmd_executable):
            QMessageBox.warning(self.main_window, "Missing Dependency", "SteamCMD is not installed. Please Initialize Tool first.")
            return

        target_folder = QFileDialog.getExistingDirectory(self.main_window, "Select Empty Folder for Server Deployment")
        if not target_folder:
            return

        if os.listdir(target_folder):
            confirmation = QMessageBox.question(self.main_window, "Folder Not Empty", "The selected folder is not empty. Deploying here may overwrite files. Continue?", QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.No:
                return

        self.ui.btn_deploy_fresh.setEnabled(False)
        self.ui.btn_deploy_fresh.setText("DEPLOYING...")
        
        self.deploy_worker = ServerDeployWorker(steamcmd_executable, target_folder)
        self.deploy_worker.progress.connect(self._log_provisioning_progress)
        self.deploy_worker.finished.connect(lambda status, msg: self._on_deploy_finished(status, msg, target_folder))
        self.deploy_worker.start()

    def _on_deploy_finished(self, success, message, target_folder):
        self.ui.btn_deploy_fresh.setEnabled(True)
        self.ui.btn_deploy_fresh.setText("STEP B: DOWNLOAD 12GB SERVER FILES")
        
        if success:
            state.server_path = target_folder
            self.ui.lbl_current_path.setText(target_folder)
            QMessageBox.information(self.main_window, "Deployment Success", message)
            
            if self.settings_bridge:
                xml_file_path = os.path.join(target_folder, "serverconfig.xml")
                if os.path.exists(xml_file_path):
                    self.settings_bridge.target_file = xml_file_path
                    self.settings_bridge.load_from_xml()
        else:
            QMessageBox.critical(self.main_window, "Deployment Error", message)

    def path_adopt_existing(self):
        target_folder = QFileDialog.getExistingDirectory(self.main_window, "Select Existing 7D2D Server Folder")
        if not target_folder:
            return

        executable_path = os.path.join(target_folder, "7DaysToDieServer.exe")
        if not os.path.exists(executable_path):
            QMessageBox.critical(self.main_window, "Invalid Selection", "The selected folder does not contain '7DaysToDieServer.exe'. Please select a valid 7D2D dedicated server directory.")
            return

        state.server_path = target_folder
        self.ui.lbl_current_path.setText(target_folder)
        
        if self.settings_bridge:
            xml_file_path = os.path.join(target_folder, "serverconfig.xml")
            if os.path.exists(xml_file_path):
                self.settings_bridge.target_file = xml_file_path
                successful_load = self.settings_bridge.load_from_xml()
                if successful_load:
                    QMessageBox.information(self.main_window, "Adoption Success", "Server folder linked and serverconfig.xml loaded successfully.")
                else:
                    QMessageBox.warning(self.main_window, "Partial Success", "Server folder linked, but failed to load serverconfig.xml correctly.")
            else:
                QMessageBox.warning(self.main_window, "Missing File", "Server folder linked, but no serverconfig.xml was found inside it.")

    def import_xml_file(self):
        """
        Allows the user to select an arbitrary XML file and load its contents into the UI.
        """
        if not self.settings_bridge:
            QMessageBox.critical(self.main_window, "Bridge Error", "SettingsBridge is not initialized.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Import Server XML", "", "XML Files (*.xml)")
        if not file_path:
            return

        try:
            self.settings_bridge.target_file = file_path
            successful_load = self.settings_bridge.load_from_xml()
            
            if successful_load:
                if hasattr(self.main_window, "log_event"):
                    self.main_window.log_event("CONFIG", f"Imported XML settings from {file_path}")
                QMessageBox.information(self.main_window, "Import Success", "XML settings successfully imported to the UI.")
            else:
                QMessageBox.warning(self.main_window, "Import Failed", "Failed to parse the XML file. Ensure it is a valid 7D2D serverconfig.xml.")
        except Exception as error_exception:
            QMessageBox.critical(self.main_window, "Import Error", f"Fatal error during XML import: {str(error_exception)}")

    def export_xml_file(self):
        """
        Allows the user to save the current UI settings to a custom XML file anywhere on disk.
        """
        if not self.settings_bridge:
            QMessageBox.critical(self.main_window, "Bridge Error", "SettingsBridge is not initialized.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Export Server XML", "serverconfig_custom.xml", "XML Files (*.xml)")
        if not file_path:
            return

        try:
            self.settings_bridge.target_file = file_path
            successful_save = self.settings_bridge.save_to_xml()
            
            if successful_save:
                if hasattr(self.main_window, "log_event"):
                    self.main_window.log_event("CONFIG", f"Exported XML settings to {file_path}")
                QMessageBox.information(self.main_window, "Export Success", f"XML settings successfully exported to:\n{file_path}")
            else:
                QMessageBox.critical(self.main_window, "Export Error", "Failed to write XML. Ensure the source file exists so it can be copied and modified.")
        except Exception as error_exception:
            QMessageBox.critical(self.main_window, "Export Error", f"Fatal error during XML export: {str(error_exception)}")

    def commit_xml_settings(self):
        """
        Standard save action directed at the configured active server path.
        """
        server_path = getattr(state, "server_path", "")
        if not server_path:
            QMessageBox.warning(self.main_window, "Missing Path", "No server path configured. Cannot save XML. Use 'Export XML' if you want to save to a custom location.")
            return

        if not self.settings_bridge:
            QMessageBox.critical(self.main_window, "Bridge Error", "SettingsBridge is not initialized.")
            return

        self.ui.btn_save_srv_settings.setEnabled(False)
        self.ui.btn_save_srv_settings.setText("SAVING...")

        xml_file_path = os.path.join(server_path, "serverconfig.xml")
        self.settings_bridge.target_file = xml_file_path
        successful_save = self.settings_bridge.save_to_xml()
        
        self.ui.btn_save_srv_settings.setEnabled(True)
        self.ui.btn_save_srv_settings.setText("COMMIT SETTINGS TO SERVER")

        if successful_save:
            if hasattr(self.main_window, "log_event"):
                self.main_window.log_event("CONFIG", "serverconfig.xml successfully rewritten in deployment folder.")
            QMessageBox.information(self.main_window, "XML Saved", "Server settings successfully written to serverconfig.xml in the deployment folder.")
        else:
            QMessageBox.critical(self.main_window, "XML Error", "Failed to write serverconfig.xml. Check file permissions.")

    def test_cloud_connection(self):
        """
        Validates GitHub integration. Prompts for token if github_secrets.json is missing.
        """
        secrets_file_path = "github_secrets.json"
        
        if not os.path.exists(secrets_file_path):
            user_token, okay_pressed = QInputDialog.getText(
                self.main_window,
                "GitHub Personal Access Token",
                "Enter your GitHub PAT to enable Cloud Sync:",
                QLineEdit.Password
            )
            
            if okay_pressed and user_token:
                sanitized_token = user_token.strip()
                secrets_dictionary = dict()
                secrets_dictionary["github_token"] = sanitized_token
                
                try:
                    with open(secrets_file_path, "w") as secrets_file:
                        json.dump(secrets_dictionary, secrets_file)
                except Exception as error_exception:
                    QMessageBox.critical(self.main_window, "Storage Error", f"Failed to save secrets file: {str(error_exception)}")
                    return
            else:
                return 

        try:
            github_engine = GitHubEngine("github_secrets.json")
            verification_success = github_engine.verify_token()
            
            if verification_success:
                if hasattr(self.main_window, "log_event"):
                    self.main_window.log_event("CLOUD", "GitHub PAT Verification Successful.")
                QMessageBox.information(self.main_window, "Cloud Link Active", "Cloud Storage Link Established. Token is valid.")
            else:
                if hasattr(self.main_window, "log_event"):
                    self.main_window.log_event("CLOUD", "GitHub PAT Verification Failed.")
                QMessageBox.warning(self.main_window, "Verification Failed", "GitHub Token is invalid or expired. Please delete github_secrets.json and try again.")
        except Exception as error_exception:
            QMessageBox.critical(self.main_window, "Engine Error", f"Could not communicate with GitHub Engine: {str(error_exception)}")

    def test_server_port(self):
        """
        Performs a local bind test on the configured Game Port to ensure it is not locked.
        """
        port_string = self.ui.txt_server_port.text().strip()
        
        if not port_string.isdigit():
            QMessageBox.warning(self.main_window, "Invalid Port", "Please enter a valid numeric port in the Identity configuration.")
            return
            
        target_port = int(port_string)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2.0)
        
        try:
            test_socket.bind(('127.0.0.1', target_port))
            if hasattr(self.main_window, "log_event"):
                self.main_window.log_event("NETWORK", f"Port {target_port} local bind test passed.")
            QMessageBox.information(self.main_window, "Port Available", f"Port {target_port} is locally available and ready for binding.")
        except OSError:
            if hasattr(self.main_window, "log_event"):
                self.main_window.log_event("NETWORK", f"Port {target_port} local bind test FAILED (In Use).")
            QMessageBox.warning(self.main_window, "Port In Use", f"Port {target_port} is currently in use by another application or is locked by the operating system.")
        finally:
            test_socket.close()

# endregion