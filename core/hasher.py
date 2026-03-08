# =========================================================
# ZERO HOUR CORE: DIGITAL FINGERPRINTING ENGINE - v23.0
# =========================================================
# ROLE: Deterministic SHA-256 Mod Hashing
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
import hashlib
import os
import logging

log = logging.getLogger("Paradoxal")

def calculate_mod_hash(directory):
    """
    Generates a unique SHA-256 fingerprint for a mod folder.
    
    This engine performs a recursive binary scan of every file.
    To ensure the fingerprint is identical across different 
    OS file systems (Windows vs Linux) or different hardware,
    it strictly sorts the directory and file lists during the walk.
    """
    # Initialize the SHA-256 accumulator
    sha256_hash = hashlib.sha256()
    
    # Verification: Does the directory exist?
    if not os.path.exists(directory):
        log.error(f"[HASHER] Target directory missing: {directory}")
        return "MISSING"

    log.info(f"[HASHER] Commencing Digital Audit: {directory}")

    # Step 1: Deterministic Directory Walk
    # We use topdown=True to allow sorting of the 'dirs' list in place.
    for root, dirs, files in os.walk(directory, topdown=True):
        
        # Sort directories in place to ensure consistent traversal order
        dirs.sort()
        
        # Sort filenames to ensure consistent file processing order
        for name in sorted(files):
            filepath = os.path.join(root, name)
            
            try:
                # Open each file in binary-read mode
                with open(filepath, "rb") as binary_file:
                    
                    # Step 2: Chunked Processing
                    # We read in 4KB blocks (4096 bytes).
                    # This is critical for industrial stability. It prevents the
                    # program from trying to load a 2GB mod asset into RAM, 
                    # which would crash the Admin tool on low-spec server VPS.
                    while True:
                        byte_block = binary_file.read(4096)
                        
                        # If no more data is found, exit the file loop
                        if not byte_block:
                            break
                            
                        # Feed the binary chunk into the SHA-256 algorithm
                        sha256_hash.update(byte_block)
                        
            except PermissionError:
                # Occurs if the 7D2D server process has a file locked
                log.warning(f"[HASHER] Permission Denied (File Locked): {name}")
                continue
                
            except Exception as e:
                # Catch-all for unexpected IO failures
                log.error(f"[HASHER] Failed to audit file {name}: {str(e)}")
                continue
                
    # Step 3: Finalize the Fingerprint
    final_fingerprint = sha256_hash.hexdigest()
    
    log.info(f"[HASHER] Audit Complete. Hash: {final_fingerprint[:16]}...")
    
    return final_fingerprint