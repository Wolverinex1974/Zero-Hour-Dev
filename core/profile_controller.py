# =========================================================
# ZERO HOUR CORE: PROFILE CONTROLLER - v23.2
# =========================================================
# ROLE: Sovereign Identity & Instance Management
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 18: MODULARIZATION REFACTOR
# FEATURE: Decoupled all Profile selection, loading, creation,
#          and deletion logic from the main UI thread.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer

from core.app_state import state
from core.validator import validate_server_heartbeat, get_active_server_pid

class ProfileController:
    """
    Handles all interactions with Server Profiles, including loading 
    environments, switching contexts, and validating server health.
    """
    def __init__(self, main_window_ref):
        # Hold a reference to the main application hub for UI/log access
        self.hub = main_window_ref

    def refresh_profile_list(self, select_name=None):
        """ Scans the database and populates the Top UI dropdown. """
        self.hub.ui.combo_profile_selector.blockSignals(True)
        self.hub.ui.combo_profile_selector.clear()
        
        profiles = self.hub.profiles_nexus.list_profiles()
        
        if len(profiles) == 0: 
            self.hub.ui.combo_profile_selector.addItem("NO PROFILES FOUND")
            self.hub.toggle_ui_lock(False)
        else:
            for p in profiles: 
                self.hub.ui.combo_profile_selector.addItem(p)
                
            sel = select_name if select_name in profiles else profiles.pop(0)
            self.load_profile_context(sel)
            
        self.hub.ui.combo_profile_selector.blockSignals(False)

    def load_profile_context(self, profile_name):
        """ 
        Loads the selected profile into the Global State and hydrates the UI. 
        Also checks if the server is already running and auto-hooks it.
        """
        data = self.hub.profiles_nexus.load_profile(profile_name)
        if not data: 
            return
            
        state.set_profile_context(data)
        
        # Hydrate the Distro/Atlas UI Tab
        self.hub.ui.txt_atlas_desc.setText(data.get("atlas_description", "A Paradoxal Server"))
        status_val = data.get("atlas_status", "ONLINE")
        idx = self.hub.ui.combo_atlas_status.findText(status_val)
        
        if idx >= 0: 
            self.hub.ui.combo_atlas_status.setCurrentIndex(idx)
        
        # Build strict dynamic paths
        MANIFEST_VAULT = os.path.join(state.base_directory, "manifests")
        v_name = data.get("manifest_name", f"manifest_{profile_name.lower()}.json")
        state.update_status("manifest_path", os.path.join(MANIFEST_VAULT, v_name))
        state.update_status("mods_path", os.path.join(state.server_path, "Mods"))
        
        disabled_path = os.path.join(state.server_path, "Disabled_Mods")
        if not os.path.exists(disabled_path): 
            os.makedirs(disabled_path, exist_ok=True)
            
        state.disabled_mods_path = disabled_path
        
        # Context switch the Iron Bridge
        if self.hub.github: 
            self.hub.github.set_target_repo(state.target_repo)
            
        # Hydrate the Setup Tab
        self.hub.ui.lbl_instance_info.setText(f"PROFILE: {profile_name} | ID: {state.current_profile_id}")
        self.hub.ui.txt_prof_name.setText(profile_name)
        self.hub.ui.txt_server_port.setText(str(state.server_port))
        self.hub.ui.txt_target_repo.setText(state.target_repo)
        
        # Validate the Server Exe heartbeat
        is_healthy = validate_server_heartbeat(state.server_path)
        self.hub.toggle_ui_lock(is_healthy)
        
        if is_healthy: 
            # Staggered loading to prevent UI hitching
            QTimer.singleShot(50, self.hub.mod_ctrl.refresh_mod_list)
            QTimer.singleShot(100, self.hub.settings_bridge.load_settings_into_ui)
            QTimer.singleShot(150, self.hub.refresh_generated_worlds)
            
            # The Sovereign Auto-Hook
            is_running, pid = get_active_server_pid(state.server_path)
            if is_running:
                self.hub.add_system_log(f"AUTO-DETECT: Server is already running (PID {pid}). Hooking tools natively...")
                QTimer.singleShot(500, self.hub.reactor.start_reactor)

    def on_profile_switched(self):
        """ Triggered when the user changes the dropdown value. """
        sel = self.hub.ui.combo_profile_selector.currentText()
        if sel != "NO PROFILES FOUND": 
            self.load_profile_context(sel)

    def prepare_new_profile(self):
        """ Clears context and focuses the Setup tab for fresh creation. """
        state.clear_context()
        self.hub.toggle_ui_lock(False)
        self.hub.ui.txt_prof_name.clear()
        self.hub.ui.txt_target_repo.clear()
        self.hub.ui.tabWidget.setCurrentIndex(3)

    def delete_active_profile(self):
        """ Prompts for deletion and completely purges the profile data. """
        if state.current_profile_name:
            confirm = QMessageBox.question(
                self.hub, 
                "Delete", 
                f"Purge {state.current_profile_name}?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.hub.profiles_nexus.delete_profile(state.current_profile_name)
                self.refresh_profile_list()