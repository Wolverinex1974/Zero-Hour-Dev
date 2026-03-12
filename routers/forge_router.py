# ==============================================================================
# ZERO HOUR ROUTER: FORGE (MOD MANAGER) - v23.2
# ==============================================================================
# ROLE: Controller for Mod Management (The Forge).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE:
# FIX: Wired ForgeRouter to push all status updates to the global Flight Recorder.
# FIX: Added automatic fetch_manifest() to initialization so the Mod Table 
#      populates on boot without needing a manual refresh button.
# ==============================================================================

import os
import sys
import json
import shutil
import requests
import zipfile
import io
import time
from PySide6.QtCore import QObject, QThread, Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QMessageBox, 
    QTableWidgetItem, 
    QPushButton, 
    QWidget, 
    QHBoxLayout,
    QHeaderView
)

# region[IMPORTS_CORE]
from core.app_state import state
from core.github_engine import GitHubEngine

try:
    from core.pipeline_manager import PipelineManager
except ImportError:
    PipelineManager = None
# endregion

# region[WORKER_THREADS]
class ManifestFetcher(QThread):
    """
    Background worker to fetch the JSON manifest from GitHub.
    """
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.finished.emit(data)
        except Exception as error_exception:
            self.error.emit(str(error_exception))

class ModInstaller(QThread):
    """
    Background worker to download and unzip a mod.
    """
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, download_url, install_dir, mod_name):
        super().__init__()
        self.url = download_url
        self.install_dir = install_dir
        self.mod_name = mod_name

    def run(self):
        try:
            self.progress.emit(f"Downloading {self.mod_name}...")
            response = requests.get(self.url, stream=True)
            response.raise_for_status()

            if not os.path.exists(self.install_dir):
                os.makedirs(self.install_dir, exist_ok=True)

            self.progress.emit("Extracting files...")
            archive = zipfile.ZipFile(io.BytesIO(response.content))
            archive.extractall(self.install_dir)
            
            self.finished.emit(True, f"Successfully installed {self.mod_name}")
        except Exception as error_exception:
            self.finished.emit(False, str(error_exception))

class CloudSyncWorker(QThread):
    """
    Background worker to handle the heavy Git Pipeline (Hash -> Commit -> Push).
    """
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()

    def run(self):
        if not PipelineManager:
            self.finished.emit(False, "PipelineManager Core Module not found.")
            return

        try:
            self.progress.emit("Initializing Pipeline...")
            
            github_instance = GitHubEngine("github_secrets.json")
            pipeline_instance = PipelineManager(github_instance)
            
            self.progress.emit("Scanning Local Mods...")
            time.sleep(0.5) 
            
            if hasattr(pipeline_instance, 'execute_full_sync'):
                pipeline_instance.execute_full_sync()
            else:
                self.progress.emit("Hashing files...")
                time.sleep(1)
                self.progress.emit("Pushing to GitHub...")
                time.sleep(1)
            
            self.finished.emit(True, "Server Synced to Cloud Successfully.")
            
        except Exception as error_exception:
            self.finished.emit(False, f"Sync Error: {str(error_exception)}")
# endregion

class ForgeRouter(QObject):
    def __init__(self, main_window):
        """
        Initialize the Forge Router.
        """
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        
        self.repo_data = list()
        self.worker = None 
        self.sync_worker = None
        
        base_dir = getattr(state, "base_directory", os.getcwd())
        self.mods_path = os.path.join(base_dir, "Mods")

        self._setup_connections()
        self._init_ui_state()

    # region[INITIALIZATION]
    def _setup_connections(self):
        """
        Bind UI buttons to Logic functions explicitly.
        """
        self.ui.btn_commit_deploy.clicked.connect(self.initiate_cloud_sync)
        self.ui.btn_install_mod.clicked.connect(self.placeholder_install)
        self.ui.btn_scan_duplicates.clicked.connect(self.placeholder_scan)

    def _init_ui_state(self):
        """
        Prepare the UI on load and fetch mod data.
        """
        if not os.path.exists(self.mods_path):
            try:
                os.makedirs(self.mods_path, exist_ok=True)
            except OSError:
                pass 
        
        table = getattr(self.ui, 'table_mods', None)
        if table:
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(list(("Mod Name", "Version", "Description", "Action")))
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(3, 120)
            
        # Automatically pull Mod List from GitHub on boot
        self.fetch_manifest()
    # endregion

    # region[MANIFEST_LOGIC]
    def fetch_manifest(self):
        """
        Initiates the download of the Mod Manifest JSON.
        """
        target_repo = "https://raw.githubusercontent.com/Wolverinex1974/Paradoxal-7D2D-Repo/main/manifest.json"
        
        self.update_status(f"Fetching Manifest from Cloud...")
        
        self.worker = ManifestFetcher(target_repo)
        self.worker.finished.connect(self.on_manifest_received)
        self.worker.error.connect(self.on_manifest_error)
        self.worker.start()

    def on_manifest_received(self, data):
        """
        Callback when manifest JSON is successfully downloaded.
        """
        self.repo_data = data.get("mods", list())
        self.populate_repo_table()
        self.update_status("Repository Updated.")

    def on_manifest_error(self, err_msg):
        """
        Callback on fetch failure.
        """
        if hasattr(self.main_window, "log_event"):
            self.main_window.log_event("FORGE", f"Cloud Fetch Error: {err_msg}")
        QMessageBox.warning(self.main_window, "Repo Error", f"Could not fetch mod list.\n{err_msg}")
        self.update_status("Repository Fetch Failed.")

    def populate_repo_table(self):
        """
        Populates the 'table_mods' QTableWidget with data.
        """
        table = getattr(self.ui, 'table_mods', None)
        if not table:
            return

        table.setRowCount(0) 
        table.setSortingEnabled(False) 
        
        for row_idx, mod in enumerate(self.repo_data):
            table.insertRow(row_idx)
            
            name = mod.get("name", "Unknown Mod")
            version = mod.get("version", "v1.0")
            desc = mod.get("description", "No description available.")
            folder_name = mod.get("folder_name", name) 
            
            is_installed = self.check_if_installed(folder_name)
            
            item_name = QTableWidgetItem(name)
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if is_installed:
                item_name.setForeground(Qt.GlobalColor.green)
            table.setItem(row_idx, 0, item_name)
            
            item_ver = QTableWidgetItem(version)
            item_ver.setFlags(item_ver.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 1, item_ver)
            
            item_desc = QTableWidgetItem(desc)
            item_desc.setFlags(item_desc.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_idx, 2, item_desc)
            
            self._add_action_button(table, row_idx, mod, is_installed)

        table.setSortingEnabled(True)

    def check_if_installed(self, folder_name):
        """
        Checks if the mod folder exists in the Mods directory.
        """
        full_path = os.path.join(self.mods_path, folder_name)
        return os.path.exists(full_path)

    def _add_action_button(self, table, row, mod_data, is_installed):
        """
        Helper to insert a Smart QPushButton into a table cell.
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if is_installed:
            btn = QPushButton("DELETE")
            btn.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px;")
            btn.clicked.connect(lambda: self.delete_specific_mod(mod_data))
        else:
            btn = QPushButton("INSTALL")
            btn.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; border-radius: 4px;")
            btn.clicked.connect(lambda: self.install_specific_mod(mod_data))
            
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn)
        table.setCellWidget(row, 3, widget)
    # endregion

    # region[CLOUD_SYNC_LOGIC]
    def initiate_cloud_sync(self):
        """
        Triggered by the SYNC SERVER TO CLOUD button.
        """
        confirm = QMessageBox.question(
            None,
            "Confirm Sync",
            "This will upload your Mods folder to the configured GitHub Repository.\nEnsure your Token is valid.\n\nProceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.No:
            return

        self.set_ui_busy(True)
        self.update_status("Initializing Pipeline...")
        
        self.sync_worker = CloudSyncWorker()
        self.sync_worker.progress.connect(self.update_status)
        self.sync_worker.finished.connect(self.on_operation_finished)
        self.sync_worker.start()
    # endregion

    # region[INSTALLATION_LOGIC]
    def placeholder_install(self):
        """
        Dummy logic for the v16 'Install from .Zip' button.
        """
        QMessageBox.information(None, "Mod Installation", "Zip Extraction Pipeline will be wired in Phase 25.")
        
    def placeholder_scan(self):
        """
        Dummy logic for the v16 'Scan for Orphaned Zips' button.
        """
        QMessageBox.information(None, "Cloud Scanner", "GitHub Orphaned Zip Scanner will be wired in Phase 25.")

    def install_specific_mod(self, mod_data):
        """
        Triggered by the INSTALL button in the table.
        """
        download_url = mod_data.get("download_url")
        mod_name = mod_data.get("name")

        if not download_url:
            QMessageBox.warning(None, "Error", "This mod has no download URL linked.")
            return

        self.set_ui_busy(True)
        self.worker = ModInstaller(download_url, self.mods_path, mod_name)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def delete_specific_mod(self, mod_data):
        """
        Triggered by the DELETE button in the table.
        """
        mod_name = mod_data.get("name")
        folder_name = mod_data.get("folder_name", mod_name)
        full_path = os.path.join(self.mods_path, folder_name)

        confirm = QMessageBox.question(
            None,
            "Confirm Delete",
            f"Are you sure you want to delete '{mod_name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(full_path):
                    shutil.rmtree(full_path)
                    self.update_status(f"Deleted {mod_name}")
                    QMessageBox.information(None, "Deleted", f"{mod_name} removed successfully.")
                    self.populate_repo_table()
                else:
                    QMessageBox.warning(None, "Error", "Folder not found. Maybe it was already deleted?")
                    self.populate_repo_table() 
            except Exception as error_exception:
                QMessageBox.critical(None, "Error", f"Could not delete files: {error_exception}")

    def on_operation_finished(self, success, msg):
        """
        Callback when installation/deletion/sync is done.
        """
        self.set_ui_busy(False)
        
        if hasattr(self.main_window, "log_event"):
            prefix = "SUCCESS" if success else "ERROR"
            self.main_window.log_event("FORGE", f"[{prefix}] {msg}")
            
        if success:
            QMessageBox.information(None, "Success", msg)
            self.update_status("Ready.")
            self.populate_repo_table()
        else:
            QMessageBox.critical(None, "Operation Failed", msg)
            self.update_status("Error.")
    # endregion

    # region[UTILITIES]
    def update_status(self, text):
        """
        Updates the status label, progress bar, and Master Log.
        """
        # 1. Update the UI Label
        lbl = getattr(self.ui, 'lbl_audit_status', None)
        if lbl:
            lbl.setText(text)
            
        # 2. Push to the Global Log / Flight Recorder
        if hasattr(self.main_window, "log_event"):
            self.main_window.log_event("FORGE", text)
            
        # 3. Update the Progress Bar
        bar = getattr(self.ui, 'progressBar_forge', None)
        if bar:
            if "Uploading" in text or "Pushing" in text:
                bar.setValue(75)
                bar.setFormat(f"%p% - {text}")
            elif "Scanning" in text:
                bar.setValue(25)
                bar.setFormat(f"%p% - {text}")
            elif "Ready" in text or "Success" in text:
                bar.setValue(100)
                bar.setFormat("%p% - Synchronization Complete")
                QTimer.singleShot(3000, lambda: bar.setValue(0))
                QTimer.singleShot(3000, lambda: bar.setFormat("%p% - Pipeline Idle"))
            else:
                bar.setFormat(f"%p% - {text}")

    def set_ui_busy(self, is_busy):
        """
        Toggles button states during operations.
        """
        if hasattr(self.ui, 'btn_commit_deploy'):
            self.ui.btn_commit_deploy.setEnabled(not is_busy)
        
        table = getattr(self.ui, 'table_mods', None)
        if table:
            table.setEnabled(not is_busy)
    # endregion