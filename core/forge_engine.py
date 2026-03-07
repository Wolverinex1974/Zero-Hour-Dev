# =========================================================
# ZERO HOUR CORE: CLOUD FORGE ENGINE - v20.8
# =========================================================
# ROLE: Background Master Deployment & Software Distro
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 17.5 FIX:
# FIX: The URL Amnesia Bug. DeployWorker now extracts the true
#      internal XML name from the metadata and passes it to the
#      manifest. This stops the Ghost Purge guardrail from 
#      deleting valid URLs attached to mismatched folder names.
# FIX: 100% Bracket-Free Syntax Enforcement.
# =========================================================
import os
import json
import base64
import logging
from PySide6.QtCore import QThread, Signal

# Custom Industrial Logic Imports
from core.hasher import calculate_mod_hash
from core.archiver import zip_mod_folder
from core.xml_scraper import scrape_mod_metadata
from core.manifest_manager import (
    get_manifest, 
    add_mod_to_manifest, 
    update_payload_metric
)

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class DeployWorker(QThread):
    """ 
    The Sequential Master Deployer.
    Handles the end-to-end lifecycle of a mod deployment.
    """
    progress_signal = Signal(str, int)
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, targets, github_engine, manifest_path):
        super().__init__()
        self.targets = targets
        self.github = github_engine
        self.manifest_path = manifest_path

    def run(self):
        """
        Executes the atomic deployment sequence for all mods.
        """
        accumulated_payload_bytes = 0
        total_mod_count = len(self.targets)
        
        log.info("---------------------------------------------------------")
        log.info(f"[FORGE] MASTER DEPLOYMENT INITIATED: {total_mod_count} MODS")
        self.log_signal.emit("STARTING MASTER DEPLOYMENT SEQUENCE...")

        try:
            for index, mod_path in enumerate(self.targets):
                folder_name = os.path.basename(mod_path)
                
                # --- STAGE 1: INTELLIGENCE SCRAPE ---
                metadata = scrape_mod_metadata(mod_path)
                
                # --- STAGE 2: DIGITAL FINGERPRINTING ---
                mod_hash = calculate_mod_hash(mod_path)
                
                # --- STAGE 3: THE FORGE (ZIPPING) ---
                self.log_signal.emit(f"ARCHIVING: {folder_name}...")
                zipped_parts = zip_mod_folder(mod_path)
                
                if not zipped_parts:
                    error_msg = f"Archiver failed to process {folder_name}"
                    log.error(f"[FORGE] {error_msg}")
                    raise Exception(error_msg)

                # --- STAGE 4: CLOUD DELIVERY (IRON BRIDGE) ---
                upload_urls = list()
                
                for zip_file in zipped_parts:
                    zip_filename = os.path.basename(zip_file)
                    file_size = os.path.getsize(zip_file)
                    accumulated_payload_bytes = accumulated_payload_bytes + file_size
                    
                    self.log_signal.emit(f"UPLOADING: {zip_filename} ({file_size / (1024*1024):.2f} MB)")
                    
                    # Execute Iron Bridge Handoff
                    url = self.github.upload_mod_to_release(zip_file)
                    
                    if url:
                        upload_urls.append(url)
                    else:
                        raise Exception(f"GitHub rejected binary: {zip_filename}")

                # --- STAGE 5: VAULT INTEGRATION ---
                manifest_data = get_manifest(self.manifest_path)
                mod_tier = 1
                
                for entry in manifest_data.get("mods", list()):
                    if entry.get("folder_name") == folder_name:
                        mod_tier = entry.get("tier", 1)
                        break
                
                # FIX: Extract the true internal name from the XML metadata
                # This prevents Ghost Purges from mismatched physical folder names.
                true_mod_name = metadata.get("name", folder_name)
                
                add_mod_to_manifest(
                    self.manifest_path, 
                    true_mod_name, 
                    folder_name, 
                    upload_urls, 
                    mod_hash, 
                    metadata, 
                    tier=mod_tier
                )
                
                # Disk Hygiene: Remove temp zips
                for zip_file in zipped_parts:
                    try:
                        os.remove(zip_file)
                    except Exception:
                        pass
                
                # Progress Update
                completion_percent = int(((index + 1) / total_mod_count) * 100)
                self.progress_signal.emit(f"Completed {folder_name}", completion_percent)

            # Update Payload Metrics
            update_payload_metric(self.manifest_path, accumulated_payload_bytes)

            log.info("[FORGE] MASTER DEPLOYMENT SUCCESSFUL")
            self.finished_signal.emit(True)
            
        except Exception as e:
            log.error(f"[FORGE] CRITICAL FAILURE: {str(e)}")
            self.finished_signal.emit(False)

class DistroWorker(QThread):
    """ 
    Handles Software Publishing (Launcher and Admin updates). 
    """
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)
    
    def __init__(self, github_engine, file_path, repo_alias, tag_name):
        super().__init__()
        self.github = github_engine
        self.file = file_path
        self.repo = repo_alias
        self.tag = tag_name
        
    def run(self):
        """
        Executes the cloud handoff for compiled software binaries.
        """
        try:
            filename = os.path.basename(self.file)
            
            log.info(f"[DISTRO] Initiating publish for {filename} (Tag: {self.tag})")
            self.log_signal.emit(f"DISTRO: Initiating cloud handoff for {filename}...")
            self.log_signal.emit(f"TARGET REPOSITORY: {self.repo}")

            # Execute the heavy IO binary upload
            url = self.github.upload_software_to_repo(
                self.file, 
                self.repo, 
                self.tag
            )
            
            if url:
                success_msg = f"BUILD LIVE: {url}"
                log.info(f"[DISTRO] {success_msg}")
                self.log_signal.emit(f"SUCCESS: {success_msg}")
                self.finished_signal.emit(True, url)
            else:
                log.error("[DISTRO] GitHub rejected the software build.")
                self.log_signal.emit("ERROR: GitHub rejected the upload. Check Token permissions.")
                self.finished_signal.emit(False, "Cloud Rejection")
                
        except Exception as e:
            error_msg = f"Distro Failure: {str(e)}"
            log.error(f"[DISTRO] {error_msg}")
            self.log_signal.emit(f"CRITICAL: {error_msg}")
            self.finished_signal.emit(False, error_msg)

class AtlasWorker(QThread):
    """ 
    Orchestrates the surgical update of the global atlas.json directory. 
    """
    finished_signal = Signal(bool, str)
    log_signal = Signal(str)

    def __init__(self, github_engine, profile_data, atlas_payload):
        super().__init__()
        self.github = github_engine
        self.profile = profile_data
        self.payload = atlas_payload

    def run(self):
        try:
            atlas_repo = self.github.global_default_repo
            url = f"https://api.github.com/repos/{atlas_repo}/contents/atlas.json"
            
            log.info(f"[ATLAS] Accessing world directory: {atlas_repo}")
            self.log_signal.emit("CONTACTING WORLD DIRECTORY...")
            
            response = self.github.session.get(url)
            
            atlas_data = list()
            
            if response.status_code == 200:
                json_response = response.json()
                content_base64 = json_response.get("content", "")
                raw_json = base64.b64decode(content_base64).decode("utf-8")
                atlas_data = json.loads(raw_json)
            
            # Sovereign ID Filtering
            target_uid = self.profile.get("profile_id")
            filtered_atlas = list()
            
            for entry in atlas_data:
                if entry.get("profile_id") != target_uid:
                    if entry.get("display_name") != self.profile.get("profile_name"):
                        filtered_atlas.append(entry)
            
            final_payload = self.payload
            final_payload.update({"profile_id": target_uid})
            filtered_atlas.append(final_payload)
            
            # Temporary local build (FIXED NAME)
            # Must be 'atlas.json' so GitHub Engine uploads it with the correct name
            temp_path = "atlas.json"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(filtered_atlas, f, indent=4)
                
            # The GitHub Engine uses os.path.basename(temp_path) -> "atlas.json"
            success = self.github.upload_manifest_to_repo(temp_path, "atlas.json")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            if success:
                log.info(f"[ATLAS] Global Sync Complete for ID: {target_uid}")
                self.finished_signal.emit(True, "Atlas Updated")
            else:
                log.error("[ATLAS] Upload Rejected.")
                self.finished_signal.emit(False, "Upload Failed")
                
        except Exception as e:
            log.error(f"[ATLAS] Critical Failure: {str(e)}")
            self.finished_signal.emit(False, str(e))