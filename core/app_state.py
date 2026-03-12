# =========================================================
# ZERO HOUR CORE: APP STATE - v23.2
# =========================================================
# ROLE: Global Context Manager (Singleton Pattern)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 12 FIX:
# FIX: Robust 'initialize_registry' with error suppression.
# FEATURE: Global flag management for threaded workers.
# =========================================================

import os
from core.registry import RegistryEngine

class AppState:
    """
    Singleton-style global state manager.
    Holds paths, flags, and the Registry Engine instance.
    """
    def __init__(self):
        # --- PATHS ---
        self.base_directory = ""
        self.server_path = ""
        self.manifest_path = ""
        self.mods_path = ""
        self.disabled_mods_path = ""
        
        # --- IDENTITY ---
        self.current_profile_name = ""
        self.current_profile_id = ""
        self.target_repo = ""
        self.server_port = "26900"
        
        # --- FLAGS ---
        self.is_test_env = False
        self.is_dirty = False
        self.steamcmd_ready = False
        self.server_process_active = False
        self.watchdog_running = False
        self.atlas_status = "OFFLINE"
        
        # --- COMPONENTS ---
        self.registry = None
        
        # --- VERSIONING ---
        self.version = "16.0.30"

    def initialize_registry(self, base_dir):
        """
        Safely initializes the RegistryEngine.
        Swallows errors to prevent boot loops.
        """
        try:
            self.registry = RegistryEngine(base_dir)
        except Exception as e:
            print(f" [STATE] WARNING: Registry failed to load: {e}")
            # Create a dummy registry to prevent NoneType errors later
            class DummyRegistry:
                def get(self, k, d=None): return d
                def set(self, k, v): pass
                def save_local(self): pass
                def get_bool(self, k, d=False): return d
                def get_int(self, k, d=0): return d
            self.registry = DummyRegistry()

    def update_status(self, key, value):
        """ Updates internal state attributes dynamically. """
        if hasattr(self, key):
            setattr(self, key, value)
            # Detect Test Environment based on path
            if key == "base_directory":
                if "TEST" in str(value).upper() or "DEV" in str(value).upper():
                    self.is_test_env = True

    def set_profile_context(self, profile_data):
        """ Hydrates state from a loaded Profile JSON. """
        if not profile_data: return
        self.current_profile_name = profile_data.get("profile_name", "Unknown")
        self.current_profile_id = profile_data.get("profile_id", "0000")
        self.server_path = profile_data.get("install_path", "")
        self.target_repo = profile_data.get("github_repo", "")
        self.server_port = profile_data.get("server_port", "26900")

    def clear_context(self):
        """ Resets profile-specific data. """
        self.current_profile_name = ""
        self.current_profile_id = ""
        self.server_path = ""
        self.target_repo = ""

# Global Singleton Instance
state = AppState()