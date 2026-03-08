# =========================================================
# ZERO HOUR CORE: PROVISIONING ENGINE - v21.2
# =========================================================
# ROLE: Script-Injected SteamCMD Deployment & Verification
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16: UI Hardening & Data Era
# FEATURE: Throttled Reporting (Prevents Event Loop Congestion).
# FEATURE: Event Loop Breathing (Allows UI Tactile Feedback).
# FEATURE: High-Res Deployment telemetry.
# =========================================================
import os
import shutil
import requests
import zipfile
import subprocess
import time
import logging
from PySide6.QtCore import QThread, Signal

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class SteamCMDInitializer(QThread):
    """
    STAGE 1: Tool Bootstrap.
    Handles the download, extraction, and binary synchronization 
    of Valve's SteamCMD utility.
    """
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        
        # Resolve the absolute path for the tool directory
        self.steamcmd_dir = os.path.abspath(
            os.path.join(self.base_dir, "steamcmd")
        )
        
        # Path to the final executable
        self.steamcmd_exe = os.path.join(
            self.steamcmd_dir, 
            "steamcmd.exe"
        )

    def run(self):
        try:
            # Step 1: Directory Preparation
            if not os.path.exists(self.steamcmd_dir):
                os.makedirs(self.steamcmd_dir)
            
            # Step 2: Download Sequence
            if not os.path.exists(self.steamcmd_exe):
                self.log_signal.emit("[BOOTSTRAP] Binary missing. Fetching from Valve...")
                
                # Masquerade as a browser to prevent CDN blocks
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                
                url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
                
                response = requests.get(
                    url, 
                    stream=True, 
                    headers=headers
                )
                
                zip_path = os.path.join(self.steamcmd_dir, "steamcmd.zip")
                
                # Write the zip to disk in chunks
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
                
                # Extract the toolset
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(self.steamcmd_dir)
                
                # Cleanup the downloaded archive
                os.remove(zip_path)
                
                self.log_signal.emit("[BOOTSTRAP] Extraction complete.")

            # Step 3: Maintenance Pass
            cache_path = os.path.join(self.steamcmd_dir, "appcache")
            
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    self.log_signal.emit("[MAINTENANCE] AppCache purged.")
                except Exception:
                    pass

            # Step 4: The Stabilization Pass
            # We run steamcmd once with '+quit' to force internal binary updates.
            self.log_signal.emit("[INIT] Synchronizing Steam binaries...")
            
            process = subprocess.Popen(
                [self.steamcmd_exe, "+quit"],
                cwd=self.steamcmd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Pipe the internal SteamCMD output to our UI
            for line in process.stdout:
                output = line.strip()
                if output:
                    self.log_signal.emit(f"[STEAM] {output}")
                    
                    # --- PHASE 16: THROTTLE PULSE ---
                    # Tiny sleep allows the UI Event Loop to process button 
                    # clicks and window movements while SteamCMD floods the stdout.
                    time.sleep(0.01)
            
            process.wait()

            # Step 5: Verification
            time.sleep(2)
            
            binary_exists = os.path.exists(self.steamcmd_exe)
            
            if binary_exists:
                self.log_signal.emit("[SUCCESS] SteamCMD Tool is now Operational.")
                self.finished_signal.emit(True, "READY")
            else:
                self.finished_signal.emit(False, "Binary failed to materialize on disk.")

        except Exception as e:
            error_msg = f"Bootstrap Critical Failure: {str(e)}"
            log.error(error_msg)
            self.finished_signal.emit(False, error_msg)

class SteamCMDDownloader(QThread):
    """
    STAGE 2: Game Deployment.
    Generates a VDF script and executes SteamCMD to download 
    the 12GB 7 Days to Die Dedicated Server engine.
    """
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, base_dir, target_path):
        super().__init__()
        self.base_dir = base_dir
        self.target_path = target_path
        
        self.steamcmd_dir = os.path.abspath(
            os.path.join(self.base_dir, "steamcmd")
        )
        
        self.steamcmd_exe = os.path.join(
            self.steamcmd_dir, 
            "steamcmd.exe"
        )
        
        # Path for the temporary instruction script
        self.script_path = os.path.join(
            self.steamcmd_dir,
            "install_7d2d.txt"
        )

    def run(self):
        try:
            # Step 1: Generate the Script Injection
            self.log_signal.emit("[PRE-FLIGHT] Generating Script Injection...")
            
            # Normalize path for Valve's parser (prefers forward slashes)
            clean_target = os.path.abspath(self.target_path).replace("\\", "/")
            
            script_lines = []
            script_lines.append(f"force_install_dir \"{clean_target}\"\n")
            script_lines.append("login anonymous\n")
            script_lines.append("app_info_update 1\n") 
            script_lines.append("app_update 294420 validate\n")
            script_lines.append("quit\n")
            
            with open(self.script_path, "w") as script_file:
                for line in script_lines:
                    script_file.write(line)
            
            # Step 2: Commencing the 12GB Deployment
            self.log_signal.emit(f"[DEPLOY] Commencing sync to: {clean_target}")

            # Execution Arguments: Run the generated script
            args = [
                self.steamcmd_exe,
                "+runscript", "install_7d2d.txt"
            ]

            process = subprocess.Popen(
                args,
                cwd=self.steamcmd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Stream the 12GB download progress (percent, size) to the UI
            for line in process.stdout:
                output = line.strip()
                if output:
                    # Filter common SteamCMD chatter to keep the UI clean
                    if "progress" in output.lower() or "downloading" in output.lower():
                        self.log_signal.emit(f"[DOWNLOAD] {output}")
                    elif "verifying" in output.lower():
                        self.log_signal.emit(f"[VERIFY] {output}")
                    
                    # --- PHASE 16: THROTTLE PULSE ---
                    # Crucial for 12GB downloads. Prevents the high-volume 
                    # progress updates from starving the UI of CPU cycles.
                    time.sleep(0.01)

            process.wait()

            # Step 3: Cleanup
            if os.path.exists(self.script_path):
                os.remove(self.script_path)

            # Step 4: Verification
            evidence_path = os.path.join(self.target_path, "7DaysToDieServer.exe")
            
            if os.path.exists(evidence_path):
                self.log_signal.emit("[SUCCESS] 7D2D Engine Deployment Verified.")
                self.finished_signal.emit(True, self.target_path)
            else:
                self.finished_signal.emit(False, "Engine executable missing after download attempt.")

        except Exception as e:
            error_msg = f"Deployment Critical Failure: {str(e)}"
            log.error(error_msg)
            self.finished_signal.emit(False, error_msg)