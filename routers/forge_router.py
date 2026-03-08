import os
import sys
import json
import shutil
import requests
import zipfile
import io
from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtWidgets import QMessageBox, QListWidgetItem

# region [METADATA]
# FILE: routers/forge_router.py
# DESC: Controller for Mod Management
# AUTH: Phase 21 Refactor - v21.2
# endregion

from core.app_state import state

# region [WORKERS]
class ManifestFetcher(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.finished.emit(response.json())
        except Exception as e:
            self.error.emit(str(e))
# endregion

class ForgeRouter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        self.repo_data = []
        self.mods_path = os.path.join(os.getcwd(), "Mods")
        
        self._setup_connections()
        self._init_ui()

    def _setup_connections(self):
        if hasattr(self.ui, 'btn_refresh_repo'):
            self.ui.btn_refresh_repo.clicked.connect(self.fetch_manifest)
        if hasattr(self.ui, 'btn_install_mod'):
            self.ui.btn_install_mod.clicked.connect(self.install_selected_mod)

    def _init_ui(self):
        if not os.path.exists(self.mods_path):
            os.makedirs(self.mods_path, exist_ok=True)
        self.refresh_installed_list()

    def fetch_manifest(self):
        # Default Repo
        url = "https://raw.githubusercontent.com/Wolverinex1974/Paradoxal-7D2D-Repo/main/manifest.json"
        
        self.main_window.log_system_event("FORGE: Fetching Mod List...")
        self.worker = ManifestFetcher(url)
        self.worker.finished.connect(self.on_manifest_received)
        self.worker.start()

    def on_manifest_received(self, data):
        self.repo_data = data.get("mods", [])
        
        list_widget = getattr(self.ui, 'list_repo_mods', None)
        if not list_widget: return
        
        list_widget.clear()
        for mod in self.repo_data:
            name = mod.get("name", "Unknown")
            item = QListWidgetItem(f"{name} [{mod.get('version','v1')}]")
            item.setData(Qt.ItemDataRole.UserRole, mod)
            list_widget.addItem(item)
            
        self.main_window.log_system_event(f"FORGE: Loaded {len(self.repo_data)} mods.")

    def install_selected_mod(self):
        list_widget = getattr(self.ui, 'list_repo_mods', None)
        if not list_widget or not list_widget.selectedItems():
            return
            
        item = list_widget.selectedItems()[0]
        mod_data = item.data(Qt.ItemDataRole.UserRole)
        
        self.main_window.log_system_event(f"FORGE: Installing {mod_data.get('name')}... (Simulation)")
        QMessageBox.information(self.main_window, "Install", f"Installing {mod_data.get('name')}")

    def refresh_installed_list(self):
        list_widget = getattr(self.ui, 'list_installed_mods', None)
        if not list_widget: return
        
        list_widget.clear()
        if os.path.exists(self.mods_path):
            for item in os.listdir(self.mods_path):
                list_widget.addItem(item)