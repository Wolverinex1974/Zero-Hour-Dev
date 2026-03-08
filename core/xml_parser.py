# =========================================================
# ZERO HOUR CORE: XML CONFIG PARSER - v21.2
# =========================================================
# ROLE: Non-Destructive serverconfig.xml Read/Write Engine
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 15 UPDATE:
# FEATURE: 'extract_help_definitions' scrapes XML comments.
# REASON: Powers the UI Tooltips with official documentation.
# =========================================================

import os
import re
import logging
import shutil
from datetime import datetime

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class XMLConfigParser:
    """
    The Data Surgeon for 7 Days to Die configuration files.
    Uses an industrial-grade regex engine to modify values while 
    strictly preserving file comments and modder formatting.
    """
    def __init__(self, server_path):
        self.server_path = server_path
        self.config_path = os.path.join(self.server_path, "serverconfig.xml")
        self.backup_dir = os.path.join(self.server_path, "Paradoxal_Backups")

    def read_config(self):
        """
        Reads serverconfig.xml and extracts property values.
        Returns a simple dictionary: {'ServerName': 'My Server'}
        """
        settings_map = {}
        
        if not os.path.exists(self.config_path):
            log.error(f"[XML-PARSER] Target missing: {self.config_path}")
            return settings_map

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # INDUSTRIAL REGEX: 
            # Captures 'name' and 'value' regardless of quote type (single/double) 
            pattern = re.compile(r'<property\s+name=["\']([^"\']+)["\']\s+value=["\']([^"\']*)["\']')

            for line in lines:
                match = pattern.search(line)
                if match:
                    prop_name = match.group(1)
                    prop_val = match.group(2)
                    settings_map[prop_name] = prop_val
            
            log.info(f"[XML-PARSER] Ingested {len(settings_map)} properties from XML.")
            return settings_map

        except Exception as e:
            log.error(f"[XML-PARSER] Ingestion failed: {str(e)}")
            return settings_map

    def extract_help_definitions(self):
        """
        PHASE 15 NEW FEATURE:
        Scrapes the XML comments preceding properties to create a 
        Knowledge Base for UI Tooltips.
        Returns: {'ServerName': 'Name shown in server browser'}
        """
        definitions_map = {}
        
        if not os.path.exists(self.config_path):
            return definitions_map

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Regex for comments: <!-- Text -->
            comment_pattern = re.compile(r'<!--\s*(.*?)\s*-->')
            # Regex for properties
            prop_pattern = re.compile(r'<property\s+name=["\']([^"\']+)["\']')

            last_comment = ""

            for line in lines:
                line = line.strip()
                
                # Check for Comment
                comment_match = comment_pattern.search(line)
                if comment_match:
                    # Capture the text, strip whitespace
                    last_comment = comment_match.group(1).strip()
                    continue

                # Check for Property
                prop_match = prop_pattern.search(line)
                if prop_match:
                    prop_name = prop_match.group(1)
                    
                    # Associate last comment with this property
                    if last_comment:
                        definitions_map[prop_name] = last_comment
                        last_comment = "" # Reset consumption
                    else:
                        definitions_map[prop_name] = "No description available."

            log.info(f"[XML-PARSER] Extracted {len(definitions_map)} help definitions.")
            return definitions_map

        except Exception as e:
            log.warning(f"[XML-PARSER] Help extraction failed: {e}")
            return {}

    def write_config(self, registry_updates):
        """
        Surgically updates values in serverconfig.xml.
        Preserves indentation, comments, and file structure.
        """
        if not os.path.exists(self.config_path):
            log.error("[XML-PARSER] Write aborted: Target file not found.")
            return False

        # Create backup before any file-write operations
        self._create_backup()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            updated_count = 0

            for line in lines:
                # Capture indentation and property name
                # regex looks for the start of the tag: <property name="...
                match = re.search(r'^(\s*)<property\s+name=["\']([^"\']+)["\']', line)
                
                if match:
                    indent = match.group(1)
                    prop_name = match.group(2)
                    
                    if prop_name in registry_updates:
                        new_val = str(registry_updates[prop_name])
                        # Reconstruct the line using the standard 7D2D double-quote format
                        # Preserves the original indentation
                        line = f'{indent}<property name="{prop_name}" value="{new_val}"/>\n'
                        updated_count = updated_count + 1
                
                new_lines.append(line)

            # Commit the updated lines to hardware
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            log.info(f"[XML-PARSER] Surgery successful. {updated_count} lines updated.")
            return True

        except Exception as e:
            log.error(f"[XML-PARSER] Surgery critical failure: {str(e)}")
            return False

    def _create_backup(self):
        """
        Creates a time-stamped backup to prevent data loss during surgery.
        """
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)

            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"serverconfig_bak_{stamp}.xml"
            path = os.path.join(self.backup_dir, fname)

            shutil.copy2(self.config_path, path)
            self._prune_backups()
            
        except Exception as e:
            log.warning(f"[XML-PARSER] Backup skipped: {str(e)}")

    def _prune_backups(self):
        """ Maintains a 10-file rolling backup limit to save disk space. """
        try:
            backups = sorted([
                os.path.join(self.backup_dir, f) 
                for f in os.listdir(self.backup_dir) 
                if f.endswith(".xml")
            ], key=os.path.getmtime)

            while len(backups) > 10:
                os.remove(backups.pop(0))
        except Exception:
            pass