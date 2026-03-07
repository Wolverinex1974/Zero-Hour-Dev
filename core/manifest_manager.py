# =========================================================
# ZERO HOUR CORE: MANIFEST MANAGER - v20.8
# =========================================================
# ROLE: Cloud Carrier Logic for the Manifest Vault
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 18 FIX:
# FIX: The Highlander Bug (Duplicate Upload Loops). Changed the 
#      primary matching logic in add_mod_to_manifest, update_mod, 
#      and remove_mod to strictly use 'folder_name' instead of 
#      'name'. This ensures the initial disk scan and the Forge 
#      upload always target the exact same JSON object.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================
import json
import os
import logging

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

def get_manifest(file_path):
    """
    Retrieves the mod manifest from a specific profile vault.
    Returns a standardized template if the file is missing or corrupt.
    """
    default_structure = dict()
    
    launcher_cfg = dict()
    launcher_cfg.update({"version": "1.0.0"})
    launcher_cfg.update({"latest_version": "1.0.0"})
    launcher_cfg.update({"news_text": "Welcome to the Paradoxal World Directory."})
    launcher_cfg.update({"total_payload_size": 0})
    launcher_cfg.update({"registry_overrides": dict()})
    
    server_info = dict()
    server_info.update({"name": "Paradoxal Server"})
    server_info.update({"ip": "0.0.0.0"})
    server_info.update({"port": "26900"})
    server_info.update({"game_version": "V1.0"})
    
    default_structure.update({"launcher_config": launcher_cfg})
    default_structure.update({"server_info": server_info})
    default_structure.update({"mods": list()})

    if not os.path.exists(file_path):
        log.info(f"[MANIFEST] Vault not found. Generating template: {file_path}")
        return default_structure

    try:
        with open(file_path, "r", encoding="utf-8") as f: 
            data = json.load(f)
    except Exception as e:
        log.error(f"[MANIFEST] Vault read failure: {str(e)}")
        return default_structure

    # --- VAULT MAINTENANCE & MIGRATION ---
    updated_required = False
    
    l_config = data.get("launcher_config")
    if not l_config:
        data.update({"launcher_config": default_structure.get("launcher_config")})
        updated_required = True
    else:
        r_overrides = l_config.get("registry_overrides")
        if r_overrides is None:
            l_config.update({"registry_overrides": dict()})
            data.update({"launcher_config": l_config})
            updated_required = True

    current_mods = data.get("mods", list())
    
    for mod in current_mods:
        if not mod.get("source"):
            mod.update({"source": "Auto"})
            updated_required = True
            
        if not mod.get("author"):
            mod.update({"author": "Unknown Author"})
            updated_required = True
            
    if updated_required: 
        log.info(f"[MANIFEST] Schema migration performed: {os.path.basename(file_path)}")
        save_manifest(data, file_path)
        
    return data

def save_manifest(data, file_path):
    """
    Saves the manifest data back to its specific profile vault.
    """
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, "w", encoding="utf-8") as f: 
            json.dump(data, f, indent=4)
            
        return True
    except Exception as e:
        log.error(f"[MANIFEST] Vault write failure: {str(e)}")
        return False

def inject_registry_into_manifest(file_path, registry_engine):
    """
    PHASE 16: Sovereign Control.
    Scans the Registry for Authoritative settings and injects them.
    """
    if not registry_engine:
        return False
        
    data = get_manifest(file_path)
    overrides = dict()
    
    # We must access internal dict safely
    for name, cvar in getattr(registry_engine, "_cvars", dict()).items():
        if getattr(cvar, "is_authoritative", False):
            overrides.update({name: getattr(cvar, "value", None)})
            
    l_config = data.get("launcher_config")
    if l_config:
        l_config.update({"registry_overrides": overrides})
        data.update({"launcher_config": l_config})
        
    return save_manifest(data, file_path)

def add_mod_to_manifest(file_path, mod_name, folder_name, urls, mod_hash, metadata_package, tier=1):
    """
    Adds or updates a mod entry with Phase 14+ Metadata.
    PHASE 18 FIX: Strictly uses 'folder_name' for matching to prevent duplication.
    """
    data = get_manifest(file_path)
    mods = data.get("mods", list())
    
    found = False
    author = metadata_package.get("author", "Unknown Author")
    desc = metadata_package.get("description", "No description provided.")
    version = metadata_package.get("version", "1.0.0")
    
    for mod in mods:
        # THE FIX: Match by the absolute physical folder name, not the display name.
        if mod.get("folder_name") == folder_name:
            mod.update({"name": mod_name}) 
            mod.update({"download_urls": urls})
            mod.update({"hash": mod_hash}) 
            mod.update({"tier": tier})
            mod.update({"author": author})
            mod.update({"description": desc})
            mod.update({"version": version})
            found = True
            break
            
    if not found:
        new_mod = dict()
        new_mod.update({"name": mod_name})
        new_mod.update({"folder_name": folder_name})
        new_mod.update({"version": version})
        new_mod.update({"download_urls": urls})
        new_mod.update({"hash": mod_hash})
        new_mod.update({"tier": tier})
        new_mod.update({"author": author})
        new_mod.update({"description": desc})
        new_mod.update({"source": "Auto"})
        mods.append(new_mod)
    
    data.update({"mods": mods})
    return save_manifest(data, file_path)

def update_mod_metadata(file_path, target_folder_name, new_folder_name, new_tier):
    """
    Updates manual metadata for a mod via UI edits.
    PHASE 18 FIX: Uses target_folder_name to ensure accurate targeting.
    """
    data = get_manifest(file_path)
    mods = data.get("mods", list())
    
    for mod in mods:
        if mod.get("folder_name") == target_folder_name:
            mod.update({"tier": new_tier})
            
            # If the folder name changed, the previous hash and URLs are invalid
            if mod.get("folder_name") != new_folder_name:
                mod.update({"folder_name": new_folder_name})
                mod.update({"download_urls": list()})
                mod.update({"hash": "PENDING"})
                
                # AMNESIA FIX: Wipe the physical folder hash so the Deep Scanner rescans
                mod.update({"folder_hash": ""})
                
            data.update({"mods": mods})
            save_manifest(data, file_path)
            return True
            
    return False

def update_payload_metric(file_path, total_bytes):
    """ Updates the total byte size of the mod-set. """
    data = get_manifest(file_path)
    l_config = data.get("launcher_config")
    
    if not l_config:
        l_config = dict()
        
    l_config.update({"total_payload_size": total_bytes})
    data.update({"launcher_config": l_config})
    
    return save_manifest(data, file_path)

def update_news_feed(file_path, text):
    """ Updates the player news text. """
    data = get_manifest(file_path)
    l_config = data.get("launcher_config")
    
    if not l_config:
        l_config = dict()
        
    l_config.update({"news_text": text})
    data.update({"launcher_config": l_config})
    
    return save_manifest(data, file_path)

def remove_mod_from_manifest(file_path, target_folder_name):
    """ 
    Safely removes a mod entry using the physical folder name.
    """
    data = get_manifest(file_path)
    original_list = data.get("mods", list())
    new_list = list()
    
    for m in original_list:
        if m.get("folder_name") != target_folder_name:
            new_list.append(m)
            
    data.update({"mods": new_list})
    return save_manifest(data, file_path)