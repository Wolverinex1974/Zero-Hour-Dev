# =========================================================
# ZERO HOUR CORE: GARBAGE COLLECTOR WORKER - v21.2
# =========================================================
# ROLE: Asynchronous Cloud Cleanup
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 18: MODULARIZATION REFACTOR
# FEATURE: Decoupled from main.py. Runs on a dedicated QThread
#          to prevent the UI from freezing during heavy GitHub
#          API scanning and deletion loops.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import time
import logging
from PySide6.QtCore import QThread, Signal

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class CloudGarbageCollector(QThread):
    """
    Scans the live GitHub Release for .zip files that are no longer
    required by the local manifest.json.
    Operates completely asynchronously.
    """
    log_signal = Signal(str)
    scan_finished_signal = Signal(bool, list, float)  # success, orphaned_assets, total_mb
    delete_finished_signal = Signal(int)              # purged_count

    def __init__(self, github_engine, required_folders):
        super().__init__()
        self.github = github_engine
        self.required_folders = required_folders
        
        # Mode switch: True = Just scanning. False = Executing the purge.
        self.is_scanning = True 
        self.assets_to_delete = list()

    def run(self):
        """
        Routes the thread to either the scanning logic or the deletion logic
        based on the current mode switch.
        """
        if self.is_scanning:
            self._execute_scan()
        else:
            self._execute_purge()

    def _execute_scan(self):
        try:
            self.log_signal.emit("GARBAGE COLLECTOR: Requesting asset manifest from GitHub...")
            cloud_assets = self.github.get_release_assets()
            
            if not cloud_assets:
                self.log_signal.emit("GARBAGE COLLECTOR: GitHub API returned 0 assets.")
                self.scan_finished_signal.emit(False, list(), 0.0)
                return

            orphaned_assets = list()
            total_freed_mb = 0.0
            
            for asset in cloud_assets:
                a_name = asset.get("name", "")
                
                # Sanitize the cloud name to match local folder structures
                clean_name = a_name.replace(".zip", "")
                if "_part" in clean_name:
                    clean_name = clean_name.split("_part")[0]
                    
                is_required = False
                for req in self.required_folders:
                    if req == clean_name:
                        is_required = True
                        break
                        
                if not is_required:
                    orphaned_assets.append(asset)
                    size_bytes = asset.get("size", 0)
                    total_freed_mb = total_freed_mb + (size_bytes / (1024 * 1024))

            self.scan_finished_signal.emit(True, orphaned_assets, total_freed_mb)

        except Exception as e:
            self.log_signal.emit(f"GARBAGE COLLECTOR ERROR: {str(e)}")
            self.scan_finished_signal.emit(False, list(), 0.0)

    def trigger_purge(self, orphaned_assets):
        """
        Configures the thread to execute a purge instead of a scan, 
        and restarts the run loop.
        """
        self.is_scanning = False
        self.assets_to_delete = orphaned_assets
        self.start()

    def _execute_purge(self):
        try:
            purged_count = 0
            
            for asset in self.assets_to_delete:
                a_id = asset.get("id")
                a_name = asset.get("name", "Unknown")
                
                self.log_signal.emit(f" -> Deleting: {a_name}")
                
                if self.github.delete_release_asset(a_id):
                    purged_count = purged_count + 1
                    time.sleep(1) # Prevent GitHub API rate limiting
                    
            self.log_signal.emit(f"GARBAGE COLLECTOR: Complete. {purged_count} files permanently deleted.")
            self.delete_finished_signal.emit(purged_count)
            
        except Exception as e:
            self.log_signal.emit(f"GARBAGE PURGE ERROR: {str(e)}")
            self.delete_finished_signal.emit(0)