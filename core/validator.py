# =========================================================
# ZERO HOUR CORE: VALIDATOR ENGINE - v20.8
# =========================================================
# ROLE: Sovereign Sentry & Live-Sync Guard
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16.5 UPDATE:
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# REVERT: Abandoned Sovereign Log Path. get_dynamic_log_path 
#         now points strictly to the native _Data directories 
#         or the SaveData folder, matching Unity's native behavior.
# FEATURE: Live-Sync Guard - Detects active server processes (WMI).
# FEATURE: Deep-Scan Port Collision detection (Netstat).
# =========================================================

import os
import socket
import json
import subprocess
import logging

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

def get_active_server_pid(instance_path):
    """
    The Vein Method: Queries Windows WMI to find running 7D2D server processes.
    Matches the ExecutablePath against the provided instance_path to find the exact PID
    belonging to this specific server profile, ignoring other instances (like LIVE vs TEST).
    
    Returns:
        tuple: (is_running: bool, pid: int or None)
    """
    if not instance_path:
        return False, None
        
    # Normalize the target path to ensure matching works regardless of slashes
    target_path = os.path.normpath(instance_path).lower()
    
    try:
        # Hide the command prompt window during the background check
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # Execute WMI query to get all running 7D2D servers and their exact hard drive paths
        process = subprocess.Popen(list(("wmic", "process", "where", "name='7DaysToDieServer.exe'", "get", "ExecutablePath,ProcessId")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        # WMI Output Format:
        # ExecutablePath                                 ProcessId
        # C:\Servers\7D2D_TEST\7DaysToDieServer.exe      10516
        
        lines = stdout.strip().splitlines()
        
        for line in lines: # Skip the header row
            line = line.strip()
            if not line:
                continue
                
            # Split from the right to separate the PID from the file path safely
            parts = line.rsplit(None, 1)
            if len(parts) == 2:
                exe_path = parts.pop(0).strip()
                pid_str = parts.pop(0).strip()
                
                exe_dir = os.path.normpath(os.path.dirname(exe_path)).lower()
                
                # If the process folder matches our Profile's root directory, we found our target
                if exe_dir == target_path:
                    log.warning(f" Active Server Process detected via WMI: PID {pid_str}")
                    return True, int(pid_str)
                    
    except Exception as e:
        log.error(f" WMI Process Discovery failed: {str(e)}")
        
    log.debug(" No active server process found for this profile.")
    return False, None

def is_server_process_running(instance_path):
    """
    Legacy wrapper for the Vein Method. Returns only the boolean for backwards
    compatibility with other modules checking for active instances.
    """
    is_running, pid = get_active_server_pid(instance_path)
    return is_running

def get_dynamic_log_path(instance_path):
    """
    Dynamically locates the correct output_log.txt path based on the folder structure.
    Checks for native '_Data' directories or the 'SaveData' fallback.
    
    Returns:
        str: The absolute path to the output_log.txt file.
    """
    if not instance_path:
        return ""
        
    dedicated_path = os.path.join(instance_path, "7DaysToDieServer_Data", "output_log.txt")
    standard_path = os.path.join(instance_path, "7DaysToDie_Data", "output_log.txt")
    save_data_path = os.path.join(instance_path, "SaveData", "output_log.txt")
    
    # Priority 1: Native Dedicated Server Folder
    if os.path.exists(os.path.dirname(dedicated_path)):
        return dedicated_path
        
    # Priority 2: Standard Client-as-Server Folder
    if os.path.exists(os.path.dirname(standard_path)):
        return standard_path
        
    # Priority 3: Fallback in case Unity drops it in the UserDataFolder
    if os.path.exists(os.path.dirname(save_data_path)):
        return save_data_path
        
    # Ultimate Fallback: Default to Dedicated Path
    return dedicated_path

def get_dynamic_save_path(instance_path):
    """
    Generates the Sovereign SaveData path to ensure world files are locked to the root directory
    and never escape into the Windows AppData/Roaming folder.
    
    Returns:
        str: The absolute path to the sovereign SaveData folder.
    """
    if not instance_path:
        return ""
        
    return os.path.join(instance_path, "SaveData")

def validate_server_heartbeat(instance_path):
    """
    Performs a structural audit of the server folder.
    Ensures that the core binaries and Unity data structures are present.
    Now supports both potential data folder naming conventions.
    """
    if not instance_path:
        return False

    exe_filename = "7DaysToDieServer.exe"
    dll_filename = "UnityPlayer.dll"

    path_to_exe = os.path.join(instance_path, exe_filename)
    path_to_dll = os.path.join(instance_path, dll_filename)
    
    path_to_data_dedicated = os.path.join(instance_path, "7DaysToDieServer_Data")
    path_to_data_standard = os.path.join(instance_path, "7DaysToDie_Data")

    # Individual Integrity Gates
    exe_found = os.path.exists(path_to_exe)
    dll_found = os.path.exists(path_to_dll)
    
    # Data folder can be either variant
    data_found = os.path.exists(path_to_data_dedicated) or os.path.exists(path_to_data_standard)

    if exe_found and dll_found and data_found:
        log.info(f" Heartbeat confirmed for instance: {instance_path}")
        return True
                
    log.warning(f" Heartbeat failure! Profile points to incomplete installation: {instance_path}")
    return False

def scan_port_collision(target_port):
    """
    Performs a two-stage network scan to identify if the 
    requested server port is already claimed by another process.
    Replaced psutil with standard OS socket and netstat bindings.
    """
    try:
        port_int = int(target_port)
    except ValueError:
        log.error(f" Invalid port string: {target_port}")
        return True

    # --- STAGE 1: SOCKET BIND ATTEMPT ---
    # Quick probe to see if the OS rejects a listener on this port
    collision_identified = False
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        test_socket.bind(tuple(("127.0.0.1", port_int)))
    except socket.error:
        collision_identified = True
    finally:
        test_socket.close()

    if collision_identified:
        log.error(f" Port {port_int} is locked by another application.")
        return True

    # --- STAGE 2: ACTIVE CONNECTION PROBE (NETSTAT) ---
    # Deep scan to find listeners in different states
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        output = subprocess.check_output(list(("netstat", "-ano")), 
            startupinfo=startupinfo, 
            text=True
        )
        
        for line in output.splitlines():
            # Look for active listening ports matching our target
            if f":{port_int} " in line and "LISTENING" in line:
                log.error(f" Port {port_int} collision found in active net-stack.")
                return True
                
    except Exception as e:
        log.debug(f" Netstat deep scan skipped or failed: {str(e)}")
            
    return False

def verify_secrets_integrity(secrets_path):
    """
    Ensures the GitHub Secrets vault is structurally sound and contains 
    the mandatory API credentials.
    """
    if not os.path.exists(secrets_path):
        return False

    try:
        with open(secrets_path, "r", encoding="utf-8") as f_secrets:
            data = json.load(f_secrets)
            
        # Check for mandatory keys
        has_token = "github_token" in data
        has_repo = "github_repo" in data
        
        if has_token and has_repo:
            return True
                
    except Exception as e:
        log.error(f" Secrets corruption detected: {str(e)}")
        return False
        
    return False

def check_instance_isolation(path_a, path_b):
    """
    Industrial Safety Check: Prevents two server profiles from 
    targeting the same physical directory.
    """
    if not path_a or not path_b:
        return True
        
    normalized_a = os.path.normpath(path_a).lower()
    normalized_b = os.path.normpath(path_b).lower()
    
    if normalized_a == normalized_b:
        log.critical(" Profile collision! Both profiles target the same folder.")
        return False
        
    return True