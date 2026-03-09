import PyInstaller.__main__
import os
import re
import shutil
import time
import logging

# =========================================================
# ZERO HOUR: INDUSTRIAL BUILDER - v23.0
# =========================================================
# ROLE: Version Control & Executable Compilation
# STRATEGY: Full Vertical Source - Router Aware - PySide6 Native
# =========================================================
# PHASE 23 Fix:
# FIX: Post refactor fixes
# FIX: 
# =========================================================

# --- MASTER CONFIGURATION ---
VERSION = "23.2"
APP_NAME = "ZeroHour_Server_Manager"
ICON_PATH = "assets/logo.ico"
MAIN_SCRIPT = "main.py"

# Logging Setup
logging.basicConfig(level=logging.INFO, format="<BUILD> %(message)s")
log = logging.getLogger("Builder")

# --- AUTO-STAMPER ENGINE ---
class VersionStamper:
    """
    Scans the codebase and updates the version tags in file headers.
    """
    def __init__(self, target_version):
        self.version = target_version
        self.dirs_to_scan = [
            "core", 
            "ui", 
            "routers", 
            "core/workers", 
            "ui/tabs"
        ]
        
        # --- THE FIX IS HERE ---
        # OLD REGEX: r"^(#.*-\sv)(\d+\.\d+\.\d+)(.*)$"  <-- Required 3 numbers
        # NEW REGEX: Matches "v20.8" OR "v20.8.1"
        self.header_pattern = re.compile(r"^(#.*-\sv)(\d+\.\d+(?:\.\d+)?)(.*)$")
        
        # Matches VERSION = "20.8"
        self.var_pattern = re.compile(r'^(VERSION\s*=\s*")(\d+\.\d+(?:\.\d+)?)(".*)$')

    def execute(self):
        log.info(f"Stamping Version {self.version} across ecosystem...")
        count = 0

        for folder in self.dirs_to_scan:
            if not os.path.exists(folder):
                continue

            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        if self.update_file(full_path):
                            count += 1

        if os.path.exists(MAIN_SCRIPT):
            if self.update_file(MAIN_SCRIPT):
                count += 1

        log.info(f"Version Stamp Complete. {count} files updated.")

    def update_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for i, line in enumerate(lines):
                if i < 20: # Check header only
                    # Check Header Comment (# ... - v20.8)
                    header_match = self.header_pattern.match(line)
                    if header_match:
                        current_ver = header_match.group(2)
                        if current_ver != self.version:
                            # Reconstruct line with new version
                            new_line = f"{header_match.group(1)}{self.version}{header_match.group(3)}\n"
                            new_lines.append(new_line)
                            modified = True
                            continue

                    # Check VERSION variable (VERSION = "20.8")
                    var_match = self.var_pattern.match(line)
                    if var_match:
                        current_ver = var_match.group(2)
                        if current_ver != self.version:
                            new_line = f"{var_match.group(1)}{self.version}{var_match.group(3)}\n"
                            new_lines.append(new_line)
                            modified = True
                            continue

                    new_lines.append(line)
                else:
                    new_lines.append(line)

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                log.info(f"Updated: {os.path.basename(file_path)}")
                return True
            return False

        except Exception as e:
            log.warning(f"Could not stamp {file_path}: {e}")
            return False

def main():
    print(f"\n{'='*60}")
    print(f" ZERO HOUR BUILD SYSTEM - v{VERSION}")
    print(f" TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # 1. EXECUTE VERSION STAMPING
    stamper = VersionStamper(VERSION)
    stamper.execute()

    # 2. CLEAN PROTOCOL
    print(" <BUILD> Initiating Workspace Sanitation...")
    dirs_to_clean = ["build", "dist"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f" <CLEAN> Removed: {d}/")
            except Exception as e:
                print(f" <WARNING> Could not remove {d}: {e}")

    # Remove spec file
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

    # 3. DEFINE HIDDEN IMPORTS
    hidden_imports = [
        # --- ROUTERS ---
        "routers.dashboard_router",
        "routers.config_router",
        "routers.forge_router",
        "routers.economy_router",
        "routers.automation_router",

        # --- CORE ---
        "core.app_state",
        "core.validator",
        "core.provisioning_engine",
        "core.registry",
        "core.settings_bridge",
        
        # --- UI ---
        # Note: We must ensure __init__.py exists in 'ui' for these to be found easily
        "ui.admin_layouts", 
        "ui.dialogs",
        "ui.nexus_styler",
        "ui.faq_knowledgebase",
        "ui.tabs.dashboard_tab",
        "ui.tabs.configuration_tab",
        "ui.tabs.forge_tab",
        "ui.tabs.economy_tab",
        "ui.tabs.automation_tab",
        "ui.tabs.faq_tab",

        # --- LIBS ---
        "sqlite3", "logging", "json", "csv", 
        "xml.etree.ElementTree", "zipfile", "shutil", "requests",

        # --- PYSIDE6 ---
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtXml"
    ]

    # 4. ARGUMENTS
    args = [
        MAIN_SCRIPT,
        f"--name={APP_NAME}",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed", 
        
        # --- FORCE PYSIDE6 ---
        "--collect-all=PySide6",
        "--collect-all=requests",
        
        # --- ASSETS ---
        "--add-data=assets;assets",
        "--add-data=ui;ui",
        "--add-data=core;core"
    ]

    if os.path.exists(ICON_PATH):
        args.append(f"--icon={ICON_PATH}")

    for h in hidden_imports:
        args.append(f"--hidden-import={h}")

    print(f" <BUILD> Configuration Locked.")
    print(f" <BUILD> Modules: {len(hidden_imports)} forced imports")
    print(f" <BUILD> Compiling... (This may take 1-2 minutes)")
    print(f"{'-'*60}")

    try:
        PyInstaller.__main__.run(args)
        print(f"{'='*60}")
        print(" <SUCCESS> BUILD COMPLETE.")
        print(f" <OUTPUT> dist/{APP_NAME}.exe")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\n <CRITICAL FAILURE> Build Process Failed: {str(e)}")

if __name__ == "__main__":
    main()
    print("Press Enter to exit.")
    input()