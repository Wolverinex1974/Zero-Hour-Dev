# =========================================================
# ZERO HOUR CORE: MOD INSTALLER - v23.2
# =========================================================
# ROLE: Smart Extraction & Mod Verification Engine
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================

import os
import shutil
import zipfile
import logging
import tempfile
from PySide6.QtCore import QThread, Signal

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class ModInstallerWorker(QThread):
    """
    Background worker that handles the intelligent extraction of Mod Archives.
    It solves the 'Nested Folder' problem by hunting for ModInfo.xml.
    """
    progress_signal = Signal(str)      # Status updates for UI
    finished_signal = Signal(bool, str) # Success/Failure, Message/ModName

    def __init__(self, zip_path, mods_directory):
        super().__init__()
        self.zip_path = zip_path
        self.mods_directory = mods_directory

    def run(self):
        self.progress_signal.emit("Analyzing Archive Structure...")
        temp_extract_path = None
        
        try:
            if not os.path.exists(self.zip_path):
                raise Exception("Source file not found.")
                
            if not os.path.exists(self.mods_directory):
                os.makedirs(self.mods_directory, exist_ok=True)

            # 1. Create a temporary staging area
            temp_extract_path = tempfile.mkdtemp(prefix="ZeroHour_ModInstall_")
            
            # 2. Extract the entire zip to staging
            # We do this to inspect structure safely without polluting the server
            self.progress_signal.emit("Extracting payload to staging area...")
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)

            # 3. Hunt for ModInfo.xml
            # This identifies the TRUE root of the mod, ignoring wrapper folders
            self.progress_signal.emit("Scanning for ModInfo.xml signature...")
            mod_root_path = self.find_mod_root(temp_extract_path)
            
            if not mod_root_path:
                raise Exception("Invalid Mod Archive: ModInfo.xml not found.")

            # 4. Determine Mod Folder Name
            # Usually the folder containing ModInfo.xml
            mod_folder_name = os.path.basename(mod_root_path)
            
            # Safety Check: If root path is the temp dir, use the zip name
            if mod_root_path == temp_extract_path:
                mod_folder_name = os.path.splitext(os.path.basename(self.zip_path))[0]
            
            # 5. Check for Collision
            final_destination = os.path.join(self.mods_directory, mod_folder_name)
            if os.path.exists(final_destination):
                self.progress_signal.emit(f"Collision detected. Removing old version of {mod_folder_name}...")
                shutil.rmtree(final_destination)

            # 6. Install (Move from Staging to Live)
            self.progress_signal.emit(f"Installing {mod_folder_name} to server...")
            shutil.move(mod_root_path, final_destination)

            log.info(f"[INSTALLER] Successfully installed: {mod_folder_name}")
            self.finished_signal.emit(True, f"Installed: {mod_folder_name}")

        except zipfile.BadZipFile:
            log.error("[INSTALLER] Corrupt Archive.")
            self.finished_signal.emit(False, "Error: The zip file is corrupt.")
            
        except Exception as e:
            log.error(f"[INSTALLER] Installation Failed: {str(e)}")
            self.finished_signal.emit(False, str(e))
            
        finally:
            # 7. Cleanup Staging
            if temp_extract_path and os.path.exists(temp_extract_path):
                try:
                    shutil.rmtree(temp_extract_path)
                except Exception as cleanup_error:
                    log.warning(f"[INSTALLER] Staging cleanup failed: {cleanup_error}")

    def find_mod_root(self, search_path):
        """
        Recursive search for the directory containing ModInfo.xml.
        Returns the path to that directory.
        """
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.lower() == "modinfo.xml":
                    return root
        return None