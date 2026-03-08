# =========================================================
# ZERO HOUR CORE: BOOT SEQUENCE - v21.2
# =========================================================
# ROLE: Environment Initialization & Pre-Flight Checks
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 18: MODULARIZATION REFACTOR
# FEATURE: Extracted perform_stabilized_boot logic out of main.py
#          to create a decoupled, sequential ignition switch.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import os
import logging
from PySide6.QtCore import Qt

from core.app_state import state
from core.github_engine import GitHubEngine
from core.store_manager import StoreManager

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class BootSequence:
    """
    Handles the heavy lifting of starting the application. 
    Verifies API keys, tests local paths, and hydrates the UI.
    """
    def __init__(self, main_window_ref):
        # We need a reference to the main window to update UI elements and logs
        self.hub = main_window_ref

    def ignite(self):
        """
        The Master Boot Function. Replaces perform_stabilized_boot.
        """
        print(" EXECUTING HEAVY SCAN...", flush=True)
        log.info(" Commencing Heavy Initial Scan...")
        
        if state.is_test_env: 
            self.hub.add_system_log("ENVIRONMENT: TEST INSTANCE DETECTED")
        
        # --- STAGE 1: CLOUD BRIDGE ESTABLISHMENT ---
        secrets_path = os.path.join(state.base_directory, "github_secrets.json")
        if os.path.exists(secrets_path):
            try:
                self.hub.github = GitHubEngine(secrets_path)
                self.hub.pipeline.github = self.hub.github
                log.info(" GitHub bridge established.")
                self.hub.add_system_log("Cloud Bridge: ACTIVE")
            except Exception as e: 
                log.error(f" GitHub failure: {str(e)}")
                self.hub.add_system_log("Cloud Bridge: OFFLINE (Check Secrets)")
                
        # --- STAGE 2: ECONOMY INITIALIZATION ---
        self.hub.store_manager = StoreManager(self.hub.ui, self.hub.database, self.hub.github)

        # --- STAGE 3: ENVIRONMENT VERIFICATION ---
        try:
            # Tell the Profile Controller to fetch the last used profile
            self.hub.profile_ctrl.refresh_profile_list()
            
            # Verify SteamCMD installation
            self.check_steamcmd_readiness()
            
            # Hydrate Global Keep-Alive setting
            if state.registry:
                try:
                    ka = state.registry.get_bool("srv_keep_alive", False)
                    self.hub.ui.chk_keep_alive.blockSignals(True)
                    self.hub.ui.chk_keep_alive.setChecked(ka)
                    self.hub.ui.chk_keep_alive.blockSignals(False)
                except Exception: 
                    pass
                    
        except Exception as e: 
            log.error(f" Sync failure during boot: {str(e)}")
            
        # --- STAGE 4: BOOT COMPLETE ---
        version_str = state.version
        if not version_str:
            version_str = "UNKNOWN"
            
        self.hub.add_system_log(f"Phase 18 Logic: ONLINE (v{version_str})")
        print(" SYSTEM READY.", flush=True)

    def check_steamcmd_readiness(self):
        """
        Verifies the physical presence of the SteamCMD executable 
        and updates the UI status label accordingly.
        """
        path = os.path.join(state.base_directory, "steamcmd", "steamcmd.exe")
        ready = os.path.exists(path)
        
        state.update_status("steamcmd_ready", ready)
        
        status_text = "( TOOL STATUS: READY )" if ready else "( TOOL STATUS: MISSING )"
        status_color = "#2ecc71" if ready else "#e74c3c"
        
        self.hub.ui.lbl_tool_status.setText(status_text)
        self.hub.ui.lbl_tool_status.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        self.hub.ui.btn_deploy_fresh.setEnabled(ready)