# =========================================================
# ZERO HOUR CORE: REGISTRY ENGINE - v21.2 (STABLE)
# =========================================================
# ROLE: Persistent Preference Storage (JSON)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 12 FIX:
# FIX: Removed 'shutil'/'tempfile' dependencies (Hard Crash Suspects).
# FIX: Retained 'get(key, default)' signature to fix Boot Error.
# =========================================================

import os
import json
import logging

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class RegistryEngine:
    """
    Manages the 'admin_registry.json' file.
    Stores persistent UI states like 'Keep Alive', 'Admin ID', etc.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.file_path = os.path.join(base_dir, "admin_registry.json")
        self.data = {}
        self.load_local()

    def load_local(self):
        """ Loads the JSON registry from disk into memory. """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.data = json.loads(content)
                    else:
                        self.data = {}
                log.info("[REGISTRY] Local preferences loaded.")
            except Exception as e:
                log.error(f"[REGISTRY] Load failed (Resetting): {e}")
                self.data = {} 
        else:
            log.info("[REGISTRY] No registry found. Creating new context.")
            self.data = {}

    def save_local(self):
        """ Commits memory state to disk. """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            log.error(f"[REGISTRY] Save failed: {e}")

    # --- KEY ACCESSORS ---

    def get(self, key, default=None):
        """ 
        Retrieves a value by key. 
        Returns 'default' if key does not exist.
        """
        return self.data.get(key, default)

    def set(self, key, value):
        """ 
        Updates a key in memory. 
        Note: Does not auto-save. Call save_local() explicitly.
        """
        self.data[key] = value

    # --- TYPE-SAFE HELPERS ---

    def get_bool(self, key, default=False):
        """
        Safely retrieves a boolean value.
        """
        val = self.get(key, default)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ('true', '1', 'yes', 'on')
        return bool(val)

    def get_int(self, key, default=0):
        """
        Safely retrieves an integer value.
        """
        val = self.get(key, default)
        try:
            return int(val)
        except (ValueError, TypeError):
            return default