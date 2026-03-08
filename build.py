import os
import shutil
import PyInstaller.__main__

# ======================================================
# ZERO HOUR: BUILD SYSTEM ORCHESTRATOR - v21.0
# ======================================================
# ROLE: PyInstaller Compilation Wrapper
# STRATEGY: Full Vertical Source - Router Aware
# ======================================================
# PHASE 21 UPDATES:
# 1. Added Hidden Imports for new 'routers' package.
# 2. Updated Version Metadata to 21.0.
# 3. Cleaned up asset paths for the Refactor structure.
# ======================================================

def clean_previous_builds():
    """
    Removes the 'build' and 'dist' directories to ensure a clean compilation.
    """
    directories = ["build", "dist"]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f">> Cleaning directory: {directory}...")
            try:
                shutil.rmtree(directory)
            except Exception as e:
                print(f"!! Error cleaning {directory}: {e}")

def compile_application():
    """
    Executes the PyInstaller process with specific arguments for the Zero Hour Suite.
    """
    print(">> INITIATING COMPILATION SEQUENCE v21.0...")

    # 1. Define the Application Name
    app_name = "ZeroHour_Server_Manager"

    # 2. Define the Main Entry Point
    script_file = "main.py"

    # 3. Define Data Files (Assets, UI, Configs)
    # Format: "source_path;dest_path" (Windows uses separator ';')
    # We include the entire 'ui' and 'assets' folders.
    add_data = [
        "ui;ui",
        "assets;assets",
        "core;core",
        # "routers;routers", # Usually code is handled by analysis, but data is safe to add if needed
    ]

    # 4. Define Hidden Imports
    # Crucial for Phase 21: Explicitly tell PyInstaller about the new Routers
    # just in case they are imported dynamically or missed by the analyzer.
    hidden_imports = [
        "PyQt6",
        "requests",
        "routers.dashboard_router",
        "routers.config_router",
        "routers.forge_router",
        "routers.economy_router",
        "routers.automation_router",
        "core.app_state",
        "core.validator",
        "core.provisioning_engine"
    ]

    # 5. Construct the PyInstaller Arguments
    args = [
        script_file,
        f"--name={app_name}",
        "--noconfirm",          # Do not ask for confirmation to overwrite
        "--clean",              # Clean PyInstaller cache
        "--onefile",            # Bundle into a single EXE (Optional: remove for directory based)
        "--windowed",           # No console window (GUI only)
        # "--console",          # UNCOMMENT FOR DEBUGGING (Shows console output)
        "--icon=assets/icon.ico", # Ensure you have an icon or remove this line
    ]

    # Append Data arguments
    for data in add_data:
        args.append(f"--add-data={data}")

    # Append Hidden Import arguments
    for imp in hidden_imports:
        args.append(f"--hidden-import={imp}")

    # 6. Execute
    print(f">> Launching PyInstaller for {app_name}...")
    PyInstaller.__main__.run(args)
    print(">> COMPILATION FINISHED.")

if __name__ == "__main__":
    clean_previous_builds()
    compile_application()
    
    # Optional: Pause at the end if running from a separate terminal window
    print(">> Build process complete. Press Enter to exit.")
    input()