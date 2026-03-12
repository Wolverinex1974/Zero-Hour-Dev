import os
import shutil
import zipfile
import datetime
import requests
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QMessageBox

# region [METADATA]
# FILE: routers/automation_router.py
# DESC: Controller for Automation
# AUTH: Phase 21 Refactor - v23.2
# endregion

class BackupWorker(QThread):
    finished = Signal(bool, str)
    
    def __init__(self, source, dest):
        super().__init__()
        self.source = source
        self.dest = dest
        
    def run(self):
        try:
            with zipfile.ZipFile(self.dest, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(self.source):
                    for file in files:
                        path = os.path.join(root, file)
                        zf.write(path, os.path.relpath(path, self.source))
            self.finished.emit(True, self.dest)
        except Exception as e:
            self.finished.emit(False, str(e))

class AutomationRouter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        self._setup_connections()

    def _setup_connections(self):
        if hasattr(self.ui, 'btn_backup_now'):
            self.ui.btn_backup_now.clicked.connect(self.force_backup_now)
            
        if hasattr(self.ui, 'btn_test_webhook'):
            self.ui.btn_test_webhook.clicked.connect(self.test_webhook)

    def force_backup_now(self):
        source = os.path.join(os.getcwd(), "Saves") # Example path
        if not os.path.exists(source):
            self.main_window.log_system_event("AUTOMATION ERROR: Save folder not found.")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = os.path.join(os.getcwd(), "Backups", f"Backup_{timestamp}.zip")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        self.main_window.log_system_event("AUTOMATION: Backup Started...")
        self.worker = BackupWorker(source, dest)
        self.worker.finished.connect(self.on_backup_finished)
        self.worker.start()

    def on_backup_finished(self, success, result):
        if success:
            self.main_window.log_system_event(f"BACKUP COMPLETE: {result}")
            QMessageBox.information(self.main_window, "Success", "Backup Complete.")
        else:
            QMessageBox.critical(self.main_window, "Error", f"Backup Failed: {result}")

    def test_webhook(self):
        self.main_window.log_system_event("AUTOMATION: Sending Webhook Test...")
        # Webhook logic here