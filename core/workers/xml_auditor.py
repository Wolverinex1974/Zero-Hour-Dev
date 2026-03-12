# =========================================================
# ZERO HOUR: XML COLLISION AUDITOR - v23.2
# =========================================================
# ROLE: Phase 19 Deep Scan Engine
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 FIX:
# FIX: Renamed class to XMLCollisionAuditor to match main.py
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import os
import xml.etree.ElementTree as ET
from PySide6.QtCore import QThread, Signal

class XMLCollisionAuditor(QThread):
    # Signal definitions
    # progress_signal: Status Message, Percent Complete
    progress_signal = Signal(str, int)
    
    # log_signal: Text to append to system log
    log_signal = Signal(str)
    
    # finished_signal: Success(bool), ConflictData(dict), TotalCount(int)
    finished_signal = Signal(bool, dict, int)

    def __init__(self, mods_path):
        super().__init__()
        self.mods_path = mods_path
        self.is_running = True

    def run(self):
        self.log_signal.emit("Initializing XML Deep Scan...")
        
        if not os.path.exists(self.mods_path):
            self.log_signal.emit("ERROR: Mods path does not exist.")
            self.finished_signal.emit(False, dict(), 0)
            return

        # Data Structure:
        # seen_declarations = {
        #    "items.xml": { "gunPistol": "ModA", "gunRifle": "ModB" }
        # }
        seen_declarations = dict()

        # conflicts = {
        #    "items.xml": { 
        #        "gunPistol": ["ModA", "ModC"] 
        #    }
        # }
        conflicts = dict()
        total_conflicts = 0

        # Get list of mod folders
        try:
            mod_folders = list()
            items = os.listdir(self.mods_path)
            for item in items:
                full_path = os.path.join(self.mods_path, item)
                if os.path.isdir(full_path):
                    mod_folders.append(item)
        except Exception as e:
            self.log_signal.emit(f"ERROR: Could not list directories: {str(e)}")
            self.finished_signal.emit(False, dict(), 0)
            return

        total_mods = len(mod_folders)
        if total_mods == 0:
            self.log_signal.emit("No mods found to scan.")
            self.finished_signal.emit(True, dict(), 0)
            return

        processed_count = 0

        # SCAN LOOP
        for mod_name in mod_folders:
            if not self.is_running:
                break

            processed_count = processed_count + 1
            percent = int((processed_count / total_mods) * 100)
            self.progress_signal.emit(f"Scanning: {mod_name}", percent)

            # Look for Config folder
            config_path = os.path.join(self.mods_path, mod_name, "Config")
            if not os.path.exists(config_path):
                # Some mods rely only on Resources/Prefabs, skip if no Config
                continue

            # Scan XML files in Config
            for xml_file in os.listdir(config_path):
                if not xml_file.endswith(".xml"):
                    continue

                full_xml_path = os.path.join(config_path, xml_file)
                self._parse_xml_file(mod_name, xml_file, full_xml_path, seen_declarations, conflicts)

        # Calculate total unique conflicts
        for file_key in conflicts:
            file_data = conflicts.get(file_key)
            if file_data:
                total_conflicts = total_conflicts + len(file_data)

        self.log_signal.emit(f"Scan Complete. Found {total_conflicts} collisions.")
        self.finished_signal.emit(True, conflicts, total_conflicts)

    def _parse_xml_file(self, mod_name, xml_filename, full_path, seen_db, conflict_db):
        """
        Parses a single XML file and checks for 'name' attribute collisions.
        """
        try:
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Iterate over all elements that might have a 'name' attribute
            # We look for <item name="...">, <block name="...">, etc.
            # Using xpath "//*[@name]" finds any element with a name attribute
            for element in root.findall(".//*[@name]"):
                decl_name = element.get("name")
                
                if not decl_name:
                    continue

                # Prepare the Seen DB structure for this filename
                if not seen_db.get(xml_filename):
                    seen_db.update({xml_filename: dict()})

                file_seen_db = seen_db.get(xml_filename)

                # Check for Collision
                existing_owner = file_seen_db.get(decl_name)
                
                if existing_owner:
                    # COLLISION DETECTED
                    # We found a duplicate name in the same XML type
                    
                    # 1. Add to Conflict DB
                    if not conflict_db.get(xml_filename):
                        conflict_db.update({xml_filename: dict()})
                    
                    file_conflicts = conflict_db.get(xml_filename)

                    if not file_conflicts.get(decl_name):
                        # Initialize list with the original owner
                        # We have to use list() constructor
                        new_list = list()
                        new_list.append(existing_owner)
                        file_conflicts.update({decl_name: new_list})

                    # Add the current offender
                    conflict_list = file_conflicts.get(decl_name)
                    if mod_name not in conflict_list:
                        conflict_list.append(mod_name)

                else:
                    # No collision, register it
                    file_seen_db.update({decl_name: mod_name})

        except ET.ParseError:
            # Malformed XML is common in modding, we just log and skip
            self.log_signal.emit(f"WARN: Could not parse {xml_filename} in {mod_name}")
        except Exception as e:
            self.log_signal.emit(f"ERR: Error scanning {xml_filename}: {str(e)}")

    def stop(self):
        self.is_running = False