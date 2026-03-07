# =========================================================
# ZERO HOUR CORE: PROFILE MANAGER - v20.8
# =========================================================
# ROLE: JSON Profile Storage & Retrieval
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 14 UPDATE:
# FEATURE: Added 'update_profile_key' for Atlas persistence.
# =========================================================

import os
import json
import uuid
import logging
from datetime import datetime

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class ProfileManager:
    """
    Manages the creation, retrieval, and deletion of Server Profiles.
    Profiles are stored as individual JSON files in the /profiles directory.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.profiles_dir = os.path.join(base_dir, "profiles")
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)

    def create_profile(self, name, install_path, port, manifest_name, repo):
        """
        Creates a new profile JSON file.
        CRITICAL: Uses 'install_path' key to match AppState.
        """
        try:
            profile_id = str(uuid.uuid4())
            # Sanitize filename
            safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
            filename = f"{safe_name}.json"
            file_path = os.path.join(self.profiles_dir, filename)
            
            # Normalize path to prevent slash confusion
            norm_path = os.path.normpath(install_path)

            profile_data = {
                "profile_id": profile_id,
                "profile_name": name,
                "install_path": norm_path,  # <--- MUST MATCH APP_STATE
                "server_port": port,
                "manifest_name": manifest_name,
                "github_repo": repo,
                "created_at": datetime.now().isoformat(),
                "last_loaded": None,
                "atlas_description": "A Paradoxal Server", # Default
                "atlas_status": "ONLINE" # Default
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)

            log.info(f"[PROFILE] Created Sovereign Profile: {name} (ID: {profile_id})")
            return True

        except Exception as e:
            log.error(f"[PROFILE] Creation Failed: {str(e)}")
            return False

    def list_profiles(self):
        """ Scans the profiles directory and returns a list of profile names. """
        profiles = []
        if not os.path.exists(self.profiles_dir):
            return profiles

        for f in os.listdir(self.profiles_dir):
            if f.endswith(".json"):
                # We return the filename without extension as the display name
                # or we could parse the JSON to get the 'profile_name' field.
                # For speed, we try to use the 'profile_name' if possible, else filename.
                try:
                    full_path = os.path.join(self.profiles_dir, f)
                    with open(full_path, 'r', encoding='utf-8') as pf:
                        data = json.load(pf)
                        if "profile_name" in data:
                            profiles.append(data["profile_name"])
                        else:
                            profiles.append(f.replace(".json", ""))
                except:
                    profiles.append(f.replace(".json", ""))
        
        return sorted(profiles)

    def load_profile(self, profile_name):
        """ Retrieves the full dictionary for a given profile name. """
        target_file = self._find_profile_file(profile_name)
        
        if target_file:
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Update Last Loaded timestamp
                    data["last_loaded"] = datetime.now().isoformat()
                    with open(target_file, 'w', encoding='utf-8') as fw:
                        json.dump(data, fw, indent=4)
                        
                    return data
            except Exception as e:
                log.error(f"[PROFILE] Load Failed for {target_file}: {str(e)}")
                return None
        
        log.warning(f"[PROFILE] Profile not found: {profile_name}")
        return None

    def update_profile_key(self, profile_name, key, value):
        """
        PHASE 14: Surgically updates a single key in the profile JSON.
        Used for persisting Atlas Description/Status.
        """
        target_file = self._find_profile_file(profile_name)
        
        if target_file:
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data[key] = value
                
                with open(target_file, 'w', encoding='utf-8') as fw:
                    json.dump(data, fw, indent=4)
                    
                log.info(f"[PROFILE] Updated {key} -> {value}")
                return True
            except Exception as e:
                log.error(f"[PROFILE] Update Failed: {str(e)}")
                return False
        return False

    def delete_profile(self, profile_name):
        """ Removes the profile JSON from disk. """
        target_file = self._find_profile_file(profile_name)
        
        if target_file and os.path.exists(target_file):
            try:
                os.remove(target_file)
                log.info(f"[PROFILE] Deleted: {profile_name}")
                return True
            except Exception as e:
                log.error(f"[PROFILE] Delete failed: {e}")
                return False
        return False

    def _find_profile_file(self, profile_name):
        """ Helper to locate the correct JSON file on disk. """
        # 1. Try direct filename match
        direct_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if os.path.exists(direct_path):
            return direct_path
        
        # 2. Scan content if filename doesn't match
        for f in os.listdir(self.profiles_dir):
            if f.endswith(".json"):
                full_path = os.path.join(self.profiles_dir, f)
                try:
                    with open(full_path, 'r', encoding='utf-8') as pf:
                        data = json.load(pf)
                        if data.get("profile_name") == profile_name:
                            return full_path
                except:
                    continue
        return None