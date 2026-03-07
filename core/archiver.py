# =========================================================
# ZERO HOUR CORE: ARCHIVER ENGINE - v20.8 (SPLITTER ENABLED)
# =========================================================
# ROLE: Data Preservation, Log Rotation, & Mod Compression
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 14 PART 6: THE SPLIT PROTOCOL
# FEATURE: 'zip_mod_folder' now implements Smart Chunking.
# REASON: GitHub Release Limit is 2.0GB.
# LOGIC: Split Archives at 1.5GB to ensure safe transport.
# =========================================================

import os
import shutil
import time
import logging
import datetime
import zipfile
from PySide6.QtCore import QThread, Signal

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

# CONSTANTS
# 1.5 GB in Bytes (Safety Margin for GitHub's 2.0 GB Limit)
MAX_ARCHIVE_SIZE_BYTES = 1610612736 

def zip_mod_folder(source_dir):
    """
    SMART ARCHIVER: Compresses a mod folder for Cloud Upload.
    Implements 'Bin Packing' to split large mods into multiple parts.
    """
    created_archives = []
    
    try:
        if not os.path.exists(source_dir):
            log.error(f"[ARCHIVER] Source not found: {source_dir}")
            return []

        mod_name = os.path.basename(source_dir)
        root_dir = os.path.dirname(source_dir)
        
        # Initialize Splitting Variables
        part_number = 1
        current_archive_size = 0
        
        # Prepare the first archive container
        current_zip_path = os.path.join(root_dir, f"{mod_name}.part{part_number}.zip")
        
        # Ensure we don't append to old files
        if os.path.exists(current_zip_path):
            os.remove(current_zip_path)
            
        # Open the first Zip File
        current_zip_handle = zipfile.ZipFile(
            current_zip_path, 
            'w', 
            zipfile.ZIP_DEFLATED, 
            allowZip64=True
        )
        
        created_archives.append(current_zip_path)
        log.info(f"[ARCHIVER] Started Archive Volume: {mod_name}.part{part_number}.zip")

        # Walk through the entire directory tree
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Calculate the relative path (internal zip structure)
                # Example: "ModName/Config/items.xml"
                relative_path = os.path.relpath(file_path, os.path.join(source_dir, ".."))
                
                # Get the size of the file we are about to add
                file_size = os.path.getsize(file_path)
                
                # CHECK: Will adding this file exceed the Limit?
                # We add a small buffer (1MB) for zip headers
                if (current_archive_size + file_size) > MAX_ARCHIVE_SIZE_BYTES:
                    
                    # 1. Close the current full zip
                    log.info(f"[ARCHIVER] Volume {part_number} Full ({current_archive_size/1024/1024:.2f} MB). Splitting...")
                    current_zip_handle.close()
                    
                    # 2. Increment Part Number
                    part_number = part_number + 1
                    current_archive_size = 0
                    
                    # 3. Create the next zip path
                    current_zip_path = os.path.join(root_dir, f"{mod_name}.part{part_number}.zip")
                    
                    if os.path.exists(current_zip_path):
                        os.remove(current_zip_path)
                        
                    # 4. Open the new zip handle
                    current_zip_handle = zipfile.ZipFile(
                        current_zip_path, 
                        'w', 
                        zipfile.ZIP_DEFLATED, 
                        allowZip64=True
                    )
                    
                    created_archives.append(current_zip_path)
                    log.info(f"[ARCHIVER] Started Archive Volume: {mod_name}.part{part_number}.zip")

                # WRITE: Add the file to the active zip
                current_zip_handle.write(file_path, relative_path)
                current_archive_size = current_archive_size + file_size

        # Cleanup: Close the final open zip
        if current_zip_handle:
            current_zip_handle.close()
            
        # Post-Process: Rename Single-Part Archives
        # If the mod fit into just one file, remove the ".part1" suffix for cleanliness.
        # This keeps the URL looking standard for small mods.
        if len(created_archives) == 1:
            single_part_path = created_archives[0]
            clean_name = f"{mod_name}.zip"
            clean_path = os.path.join(root_dir, clean_name)
            
            if os.path.exists(clean_path):
                os.remove(clean_path)
                
            os.rename(single_part_path, clean_path)
            created_archives = [clean_path]
            log.info(f"[ARCHIVER] Single volume detected. Renamed to {clean_name}")
        else:
            log.info(f"[ARCHIVER] Multi-volume Archive Complete. Total Parts: {len(created_archives)}")

        return created_archives
        
    except Exception as e:
        log.error(f"[ARCHIVER] Compression failed: {str(e)}")
        # Cleanup on failure to prevent partial uploads
        for bad_zip in created_archives:
            if os.path.exists(bad_zip):
                try:
                    os.remove(bad_zip)
                except Exception:
                    pass
        return []

class LogRotator:
    """
    Static utility to preserve server logs.
    Executed Pre-Flight (Before Server Start) to save the PREVIOUS run's log.
    """
    @staticmethod
    def rotate_logs(server_path):
        try:
            # 1. Identify Source (Default Unity Log Path)
            source_log = os.path.join(server_path, "7DaysToDieServer_Data", "output_log.txt")
            
            if not os.path.exists(source_log):
                log.warning("[ARCHIVER] No previous log found to rotate.")
                return

            # 2. Identify/Create Destination (Standard 'logs' folder)
            dest_folder = os.path.join(server_path, "logs")
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder, exist_ok=True)

            # 3. Generate Timestamped Filename
            # Format: output_log_2026-02-14__12-30-00.txt
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
            dest_filename = f"output_log_{timestamp}.txt"
            dest_path = os.path.join(dest_folder, dest_filename)

            # 4. Execute Copy
            shutil.copy2(source_log, dest_path)
            log.info(f"[ARCHIVER] Log Rotated: {dest_filename}")

        except Exception as e:
            log.error(f"[ARCHIVER] Log Rotation Failed: {str(e)}")

class WorldArchiver(QThread):
    """
    Background worker that creates a ZIP snapshot of the World State.
    Includes: Saves Folder, serverconfig.xml, serveradmin.xml
    """
    progress_signal = Signal(str) # Status messages
    finished_signal = Signal(bool, str) # Success, Message

    def __init__(self, server_path):
        super().__init__()
        self.server_path = server_path

    def run(self):
        self.progress_signal.emit("Initializing Sovereign Backup...")
        
        try:
            # 1. Locate Critical Data
            # We must intelligently find the Saves folder (Local vs AppData)
            saves_path = self.locate_saves_folder()
            config_path = os.path.join(self.server_path, "serverconfig.xml")
            admin_path = os.path.join(self.server_path, "serveradmin.xml")
            
            if not saves_path or not os.path.exists(saves_path):
                raise Exception("CRITICAL: Could not locate Saves folder.")

            # 2. Prepare Backup Directory
            backup_root = os.path.join(self.server_path, "Backups")
            if not os.path.exists(backup_root):
                os.makedirs(backup_root, exist_ok=True)

            # 3. Create Staging Area (Temp folder to zip)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
            staging_dir = os.path.join(backup_root, f"temp_stage_{timestamp}")
            os.makedirs(staging_dir, exist_ok=True)
            
            self.progress_signal.emit("Staging Configuration Files...")
            # Copy XMLs
            if os.path.exists(config_path): shutil.copy2(config_path, staging_dir)
            if os.path.exists(admin_path): shutil.copy2(admin_path, staging_dir)

            self.progress_signal.emit("Staging World Data (This may take time)...")
            # Copy Saves (Recursive)
            # We copy to Staging/Saves
            dest_saves = os.path.join(staging_dir, "Saves")
            shutil.copytree(saves_path, dest_saves)

            # 4. Compress
            self.progress_signal.emit("Compressing Archive...")
            zip_filename = os.path.join(backup_root, f"Backup_{timestamp}")
            shutil.make_archive(zip_filename, 'zip', staging_dir)
            
            # 5. Cleanup Staging
            shutil.rmtree(staging_dir)
            
            # 6. Retention Policy (Keep Last 5)
            self.enforce_retention_policy(backup_root)

            final_name = f"Backup_{timestamp}.zip"
            log.info(f"[ARCHIVER] Backup Complete: {final_name}")
            self.finished_signal.emit(True, f"Backup Saved: {final_name}")

        except Exception as e:
            log.error(f"[ARCHIVER] Backup Failed: {str(e)}")
            self.finished_signal.emit(False, str(e))

    def locate_saves_folder(self):
        """ Smart Discovery of the Saves path. """
        # Priority 1: Local 'Saves' folder (Zero Hour Standard)
        local = os.path.join(self.server_path, "Saves")
        if os.path.exists(local): return local
        
        # Priority 2: UserSaveData/Saves (V1.0 Configurable)
        usd = os.path.join(self.server_path, "UserSaveData", "Saves")
        if os.path.exists(usd): return usd
        
        # Priority 3: AppData (Windows Standard)
        appdata = os.getenv('APPDATA')
        if appdata:
            roaming = os.path.join(appdata, "7DaysToDie", "Saves")
            if os.path.exists(roaming): return roaming
            
        return None

    def enforce_retention_policy(self, backup_dir):
        """ Deletes oldest backups if count > 5. """
        try:
            files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.zip')]
            files.sort(key=os.path.getmtime) # Sort by time (Oldest first)
            
            while len(files) > 5:
                oldest = files.pop(0)
                os.remove(oldest)
                log.info(f"[ARCHIVER] Retention Policy: Deleted {os.path.basename(oldest)}")
        except Exception as e:
            log.warning(f"[ARCHIVER] Retention check failed: {e}")