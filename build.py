# =========================================================
# ZERO HOUR: INDUSTRIAL BUILDER - v20.8
# =========================================================
# ROLE: Version Control & Executable Compilation
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 UPDATE:
# FIX: Bumped Target Version to 20.8.
# FIX: Verified ui.tabs.* and xml_auditor are in hidden_imports.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import PyInstaller.__main__
import os
import re
import shutil
import time
import logging

# --- MASTER CONFIGURATION ---
VERSION = "20.8"
APP_NAME = "ZeroHourManager"
ICON_PATH = "assets/logo.ico"
MAIN_SCRIPT = "main.py"

# Logging Setup
logging.basicConfig(level=logging.INFO, format="<BUILD> %(message)s")
log = logging.getLogger("Builder")

# --- AUTO-STAMPER ENGINE ---
class VersionStamper:
    """
    Scans the codebase and updates the version tags in file headers
    before the compiler runs.
    """
    def __init__(self, target_version):
        self.version = target_version
        self.dirs_to_scan = list(("core", "ui", "core/workers", "ui/tabs"))
        # Regex: Looks for "# ... - vX.X.X" or "VERSION = ..."
        self.header_pattern = re.compile(r"^(#.*-\sv)(\d+\.\d+\.\d+)(.*)$")
        self.var_pattern = re.compile(r'^(VERSION\s*=\s*")(\d+\.\d+)(".*)$')

    def execute(self):
        log.info(f"Stamping Version {self.version} across ecosystem...")
        count = 0

        # Scan Core, UI, and Workers folders
        for folder in self.dirs_to_scan:
            if not os.path.exists(folder):
                continue

            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        if self.update_file(full_path):
                            count = count + 1

        # Also stamp the main entry point
        if os.path.exists(MAIN_SCRIPT):
            if self.update_file(MAIN_SCRIPT):
                count = count + 1

        log.info(f"Version Stamp Complete. {count} files updated.")

    def update_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = list()

            # Check first 20 lines for header or VERSION variable
            for i, line in enumerate(lines):
                if i < 20:
                    # Check Header Comment
                    header_match = self.header_pattern.match(line)
                    if header_match:
                        current_ver = header_match.group(2)
                        if current_ver != self.version:
                            new_line = f"{header_match.group(1)}{self.version}{header_match.group(3)}\n"
                            new_lines.append(new_line)
                            modified = True
                            continue

                    # Check VERSION variable (in main.py)
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

    # 2. NUCLEAR CLEAN PROTOCOL
    print(" <BUILD> Initiating Workspace Sanitation...")
    dirs_to_clean = list(("build", "dist"))
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f" <CLEAN> Removed: {d}/")
            except Exception as e:
                print(f" <WARNING> Could not remove {d}: {e}")

    # 3. DEFINE HIDDEN IMPORTS (THE CRITICAL LIST)
    # This ensures the EXE contains the Zero Hour Brain, Organs, and Nerves.
    hidden_imports = list((
        # --- CORE LOGIC ---
        "core.app_state",
        "core.archiver",
        "core.boot_sequence",
        "core.database_manager",
        "core.economy_parser",
        "core.forge_engine",
        "core.github_engine",
        "core.hasher",
        "core.logger",
        "core.manifest_manager",
        "core.mod_controller",
        "core.mod_installer",
        "core.paradoxal_telnet",
        "core.pipeline_manager",
        "core.profile_controller",
        "core.profile_manager",
        "core.provisioning_engine",
        "core.reactor_controller",
        "core.reactor_engine",
        "core.registry",
        "core.settings_bridge",
        "core.store_manager",
        "core.validator",
        "core.xml_parser",
        "core.xml_scraper",

        # --- WORKERS ---
        "core.workers.garbage_collector",
        "core.workers.xml_auditor", # PHASE 19

        # --- UI LOGIC (PHASE 20 DECOUPLED MODULES) ---
        "ui.admin_layouts",
        "ui.dialogs",
        "ui.nexus_styler",
        "ui.faq_knowledgebase",
        "ui.tabs.dashboard_tab",
        "ui.tabs.configuration_tab",
        "ui.tabs.forge_tab",
        "ui.tabs.economy_tab",
        "ui.tabs.automation_tab",

        # --- STANDARD LIBRARIES ---
        "sqlite3",
        "logging",
        "json",
        "csv",
        "xml.etree.ElementTree",
        "shiboken6",
        "zipfile",
        "shutil"
    ))

    # 4. CONSTRUCT ARGUMENTS
    args = list((
        MAIN_SCRIPT,                # Entry Point
        "--name=ZeroHourManager",   # Output Name
        "--noconfirm",              # Overwrite without asking
        "--onefile",                # Bundle into single EXE
        "--console",                # KEEP CONSOLE OPEN (Critical for Debugging)
        "--clean",                  # Clean PyInstaller cache
        "--collect-all=PySide6",    # Force full Qt Bundle (Stability > Size)
        "--add-data=assets;assets"  # Bundle Assets Folder
    ))

    # Add Icon if exists
    if os.path.exists(ICON_PATH):
        args.append(f"--icon={ICON_PATH}")

    # Append hidden imports
    for h in hidden_imports:
        args.append(f"--hidden-import={h}")

    print(f" <BUILD> Configuration Locked.")
    print(f" <BUILD> Modules: {len(hidden_imports)} forced")
    print(f" <BUILD> Compiling... (This may take 1-2 minutes)")
    print(f"{'-'*60}")

    # 5. EXECUTE PYINSTALLER
    try:
        PyInstaller.__main__.run(args)

        print(f"{'='*60}")
        print(" <SUCCESS> BUILD COMPLETE.")
        print(" <OUTPUT> dist/ZeroHourManager.exe")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n <CRITICAL FAILURE> Build Process Failed: {str(e)}")

if __name__ == "__main__":
    main()