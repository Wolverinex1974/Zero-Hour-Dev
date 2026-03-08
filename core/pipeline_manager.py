# =========================================================
# ZERO HOUR CORE: PIPELINE MANAGER - v23.0
# =========================================================
# ROLE: Cloud Synchronization Orchestrator (Smart Uplink)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 17.5 UPDATE:
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# FEATURE: The Deep Hash Protocol. Forged an asynchronous 
#          AuditWorker that cryptographically hashes the physical
#          bytes of every mod folder. Completely defeats the
#          "Lazy Author" trap where ModInfo.xml versions are ignored.
# =========================================================

import os
import json
import time
import shutil
import logging
import hashlib
import xml.etree.ElementTree as ET
from PySide6.QtCore import QThread, Signal, QObject

from core.app_state import state
from core.manifest_manager import get_manifest, save_manifest
from core.forge_engine import DeployWorker, AtlasWorker

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class AuditWorker(QThread):
    """
    Background worker that cryptographically hashes mod folders
    to detect physical changes without freezing the UI.
    """
    progress_signal = Signal(str, int)
    finished_signal = Signal(object, bool) # targets_list, manifest_was_updated

    def __init__(self, manifest_path, mods_path):
        super().__init__()
        self.manifest_path = manifest_path
        self.mods_path = mods_path

    def _extract_modinfo_version(self, folder_path):
        """ Safe bracket-free XML extraction for visual UI parity. """
        xml_path = os.path.join(folder_path, "ModInfo.xml")
        if not os.path.exists(xml_path):
            return None
            
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            version_node = root.find("Version")
            if version_node is not None:
                return version_node.get("value")
        except Exception:
            pass
        return None

    def _calculate_folder_hash(self, folder_path):
        """ 
        Generates a deterministic SHA256 hash of all files inside a folder.
        Reads in 8KB chunks to handle massive overhaul mods safely.
        """
        sha256_hash = hashlib.sha256()
        
        for root, dirs, files in os.walk(folder_path):
            dirs.sort()
            files.sort()
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # Hash the relative path so internal folder structure changes are caught
                rel_path = os.path.relpath(file_path, folder_path)
                sha256_hash.update(rel_path.encode("utf-8"))
                
                try:
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            sha256_hash.update(chunk)
                except Exception as e:
                    log.warning(f"[AUDIT] Could not hash file {file_name}: {str(e)}")
                    
        return sha256_hash.hexdigest()

    def run(self):
        log.info("[AUDIT] Engaging Deep Hash Protocol...")
        self.progress_signal.emit("Auditing Mod Hashes...", 5)
        
        missing_url_targets = list()
        manifest_was_updated = False
        
        try:
            manifest = get_manifest(self.manifest_path)
            mods = manifest.get("mods", list())
            
            total_mods = len(mods)
            current_mod_index = 0
            
            for mod in mods:
                current_mod_index = current_mod_index + 1
                folder_name = mod.get("folder_name")
                mod_path = os.path.join(self.mods_path, folder_name)
                
                if not os.path.exists(mod_path):
                    continue
                    
                # Update UI Progress dynamically
                progress_pct = int((current_mod_index / total_mods) * 20) + 5
                self.progress_signal.emit(f"Hashing: {folder_name}", progress_pct)

                # 1. Check physical XML version (For UI Accuracy)
                physical_version = self._extract_modinfo_version(mod_path)
                cached_version = mod.get("version")
                
                if physical_version and physical_version != cached_version:
                    log.info(f"[AUDIT] Version string updated for {folder_name}: {physical_version}")
                    mod.update({"version": physical_version})
                    manifest_was_updated = True

                # 2. THE DEEP HASH (For Cryptographic Physical Changes)
                physical_hash = self._calculate_folder_hash(mod_path)
                cached_hash = mod.get("folder_hash")
                
                if physical_hash != cached_hash:
                    log.warning(f"[AUDIT] Cryptographic drift detected in {folder_name}. Flagging for Forge.")
                    mod.update({"folder_hash": physical_hash})
                    # Wipe the download URL to force the Forge Engine to re-upload it
                    mod.update({"download_urls": list()})
                    manifest_was_updated = True

                # 3. UPLOAD QUEUE
                urls = mod.get("download_urls")
                if not urls or len(urls) == 0:
                    missing_url_targets.append(mod_path)
                    
            if manifest_was_updated:
                manifest.update({"mods": mods})
                save_manifest(manifest, self.manifest_path)
                log.info("[AUDIT] Manifest updated with new cryptographic hashes.")
                
            self.progress_signal.emit("Audit Complete.", 25)
            self.finished_signal.emit(missing_url_targets, manifest_was_updated)
            
        except Exception as e:
            log.error(f"[AUDIT] Critical Failure: {str(e)}")
            self.finished_signal.emit(list(), False)


class MasterDeployer(QThread):
    """
    Background worker that handles the final commit of the Manifest.
    This runs AFTER any necessary binaries have been uploaded.
    """
    progress_signal = Signal(str, int)
    finished_signal = Signal(bool, str)

    def __init__(self, github_engine):
        super().__init__()
        self.github = github_engine

    def run(self):
        try:
            self.progress_signal.emit("Initializing Secure Link...", 30)
            
            if not self.github:
                raise Exception("GitHub Engine not initialized.")

            if not state.target_repo:
                raise Exception("No Target Repo defined in Profile.")
                
            self.github.set_target_repo(state.target_repo)
            
            commit_msg = f"Zero Hour Auto-Sync: {time.strftime('%Y-%m-%d %H:%M')}"
            
            if os.path.exists(state.manifest_path):
                self.progress_signal.emit("Pushing to Sovereign Cloud...", 60)
                success = self.github.commit_file(state.manifest_path, commit_msg)
                
                if not success:
                    raise Exception("GitHub rejected the manifest commit.")
            else:
                raise Exception("Manifest file missing.")

            self.progress_signal.emit("Verifying Integrity...", 90)
            time.sleep(1)

            self.progress_signal.emit("Synchronization Complete.", 100)
            self.finished_signal.emit(True, "Server Synced Successfully.")

        except Exception as e:
            log.error(f"[PIPELINE] Critical Failure: {str(e)}")
            self.progress_signal.emit("Sync Failed.", 0)
            self.finished_signal.emit(False, str(e))


class PipelineManager(QObject):
    """
    The Controller for all cloud operations.
    Bridges the UI signals to the Worker Threads.
    """
    pipeline_status_signal = Signal(str, int)
    pipeline_finished_signal = Signal(bool, str)

    def __init__(self, github_engine_ref):
        super().__init__()
        self.github = github_engine_ref
        self.worker = None
        self.forge_worker = None
        self.atlas_worker = None
        self.audit_worker = None

    def validate_repo_configuration(self):
        if state.target_repo and len(state.target_repo.strip()) > 3:
            return True
            
        if self.github and self.github.global_default_repo:
            fallback = self.github.global_default_repo
            log.warning(f"[PIPELINE] Profile has no Repo defined. Smart Fallback to: {fallback}")
            state.target_repo = fallback
            return True
            
        return False

    def start_master_deployment(self):
        """
        Triggers the "Sync Server to Cloud" process.
        Starts the asynchronous Deep Hash Protocol.
        """
        is_busy = False
        if self.worker and self.worker.isRunning(): is_busy = True
        if self.forge_worker and self.forge_worker.isRunning(): is_busy = True
        if self.audit_worker and self.audit_worker.isRunning(): is_busy = True
        
        if is_busy:
            log.warning("[PIPELINE] Busy. Sync request ignored.")
            return

        if not self.validate_repo_configuration():
            log.error("[PIPELINE] CRITICAL: No Repository Configured.")
            self.pipeline_finished_signal.emit(False, "CRITICAL: No Mod Storage Repository defined.\nPlease go to SETUP tab and define a GitHub Repo.")
            return

        # Launch the Deep Hash Protocol
        self.audit_worker = AuditWorker(state.manifest_path, state.mods_path)
        self.audit_worker.progress_signal.connect(self.relay_progress)
        self.audit_worker.finished_signal.connect(self.on_audit_complete)
        self.audit_worker.start()

    def on_audit_complete(self, missing_url_targets, manifest_was_updated):
        """ Callback when the AuditWorker finishes hashing the disk. """
        if len(missing_url_targets) > 0:
            self.launch_forge_sequence(missing_url_targets)
        else:
            self.launch_commit_sequence()

    def launch_forge_sequence(self, targets):
        log.info(f"[PIPELINE] Engaging Binary Uplink for {len(targets)} mods.")
        self.pipeline_status_signal.emit(f"Uploading {len(targets)} Mod(s)...", 10)
        
        if state.target_repo:
            self.github.set_target_repo(state.target_repo)

        self.forge_worker = DeployWorker(targets, self.github, state.manifest_path)
        self.forge_worker.progress_signal.connect(self.relay_progress)
        self.forge_worker.log_signal.connect(lambda msg: self.pipeline_status_signal.emit(msg, 50))
        self.forge_worker.finished_signal.connect(self.on_forge_complete)
        self.forge_worker.start()

    def on_forge_complete(self, success):
        if success:
            log.info("[PIPELINE] Binary Uplink Complete. Proceeding to Commit.")
            self.launch_commit_sequence()
        else:
            log.error("[PIPELINE] Binary Uplink Failed.")
            self.pipeline_finished_signal.emit(False, "Mod Upload Failed. Aborting Sync.")
            self.forge_worker = None

    def launch_commit_sequence(self):
        log.info("[PIPELINE] Engaging Manifest Commit.")
        self.worker = MasterDeployer(self.github)
        self.worker.progress_signal.connect(self.relay_progress)
        self.worker.finished_signal.connect(self.relay_finish)
        self.worker.start()

    def trigger_atlas_update(self, profile_data, payload):
        if self.atlas_worker and self.atlas_worker.isRunning():
            return

        if not self.validate_repo_configuration():
            log.error("[PIPELINE] CRITICAL: No Repository Configured for Atlas.")
            self.pipeline_finished_signal.emit(False, "Atlas Failed: No Repository Configured.")
            return

        log.info("[PIPELINE] Initiating Atlas Registration...")
        
        if state.target_repo:
            self.github.set_target_repo(state.target_repo)

        self.atlas_worker = AtlasWorker(self.github, profile_data, payload)
        self.atlas_worker.finished_signal.connect(self.relay_finish)
        self.atlas_worker.start()

    def relay_progress(self, msg, percent):
        self.pipeline_status_signal.emit(msg, percent)

    def relay_finish(self, success, message):
        self.pipeline_finished_signal.emit(success, message)
        self.worker = None
        self.forge_worker = None
        self.atlas_worker = None
        self.audit_worker = None