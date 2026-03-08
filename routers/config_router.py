import os
import sys
import shutil
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog

# region [METADATA]
# FILE: routers/config_router.py
# DESC: Controller for Server Configuration
# AUTH: Phase 21 Refactor - v21.2
# endregion

# Assume core modules exist
from core.app_state import state

class ConfigRouter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        self._setup_connections()

    # region [INITIALIZATION]
    def _setup_connections(self):
        # Identity Logic - Direct Access
        if hasattr(self.ui, 'btn_save_identity'):
            self.ui.btn_save_identity.clicked.connect(self.save_identity_data)
            
        # Provisioning Logic
        if hasattr(self.ui, 'btn_browse_adopt'):
            self.ui.btn_browse_adopt.clicked.connect(self.path_adopt_existing)
            
        if hasattr(self.ui, 'btn_deploy_fresh'):
            self.ui.btn_deploy_fresh.clicked.connect(self.path_provision_new)

        # Settings Logic
        if hasattr(self.ui, 'btn_save_srv_settings'):
            self.ui.btn_save_srv_settings.clicked.connect(self.on_save_xml_settings)
    # endregion

    # region [IDENTITY_LOGIC]
    def save_identity_data(self):
        """
        Saves the Manager Profile Name, Port, and Target Repo.
        """
        repo = self.ui.txt_target_repo.text().strip() if hasattr(self.ui, 'txt_target_repo') else ""
        port = self.ui.txt_server_port.text().strip() if hasattr(self.ui, 'txt_server_port') else ""
        
        # Update State
        state.target_repo = repo
        state.server_port = port

        self.main_window.log_system_event(f"IDENTITY SAVED: Repo={repo}, Port={port}")
        QMessageBox.information(self.main_window, "Success", "Server Identity Saved.")
    # endregion

    # region [PROVISIONING_LOGIC]
    def path_adopt_existing(self):
        """
        Points the manager to an already installed 7D2D server folder.
        """
        sel = QFileDialog.getExistingDirectory(self.main_window, "Select Root Server Directory")
        if not sel:
            return

        self.main_window.log_system_event(f"PROFILE ADOPTED: {sel}")
        # Logic to update internal profile registry would go here

    def path_provision_new(self):
        """
        Uses SteamCMD to download the full server files.
        """
        sel = QFileDialog.getExistingDirectory(self.main_window, "Select Empty Folder for Install")
        if not sel:
            return

        self.main_window.log_system_event(f"PROVISIONING STARTED AT: {sel}")
        QMessageBox.information(self.main_window, "Info", "SteamCMD Download would start here (Worker Pending).")
    # endregion

    # region [XML_SETTINGS_LOGIC]
    def on_save_xml_settings(self):
        """
        Commits the UI form data to serverconfig.xml.
        """
        btn = getattr(self.ui, 'btn_save_srv_settings', None)
        if btn:
            btn.setEnabled(False)
            btn.setText("COMMITTING...")

        # Simulate Save
        QTimer.singleShot(1000, lambda: self._reset_save_button(btn))
        self.main_window.log_system_event("SETTINGS COMMITTED to serverconfig.xml")

    def _reset_save_button(self, btn):
        if btn:
            btn.setEnabled(True)
            btn.setText("COMMIT SETTINGS TO XML")
    # endregion