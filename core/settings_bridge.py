# ==============================================================================
# ZERO HOUR CORE: SETTINGS BRIDGE - v23.0
# ==============================================================================
# ROLE: The Translator. Bridges the GUI Widgets to the serverconfig.xml file.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 23 UPDATE (INTELLIGENCE RESTORATION):
# FIX: Added 'Comment Scraper' logic to read <!-- Help Text --> from XML.
# FIX: Injects scraped descriptions into the UI Help Labels (3rd Column).
# FIX: Maintains robust ElementTree parsing for data values.
# ==============================================================================

import os
import sys
import shutil
import re
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QLineEdit, 
    QComboBox, 
    QCheckBox, 
    QSpinBox, 
    QMessageBox,
    QLabel
)

class SettingsBridge:
    def __init__(self, main_window):
        """
        Initialize the Settings Bridge.
        :param main_window: Reference to the Main Window (to access UI widgets).
        """
        self.main_window = main_window
        self.ui = main_window.ui
        self.target_file = "serverconfig.xml" 
        
        # XML Namespace mapping (Property Name -> UI Widget Name)
        # Used to map Values AND Help Text (via lbl_help_{Property})
        self.property_map = {
            # Page 1: Identity & Web
            "ServerName": "txt_ServerName",
            "ServerDescription": "txt_ServerDescription",
            "ServerWebsiteURL": "txt_ServerWebsiteURL",
            "ServerPassword": "txt_ServerPassword",
            "WebDashboardEnabled": "combo_WebDashboardEnabled",
            
            # Page 2: Networking
            "ServerPort": "txt_ServerPort",
            "ServerVisibility": "combo_ServerVisibility",
            "ServerMaxPlayerCount": "txt_ServerMaxPlayerCount",
            "ServerReservedSlots": "txt_ServerReservedSlots",
            
            # Page 3: Admin
            "TelnetEnabled": "combo_TelnetEnabled",
            "TelnetPort": "txt_TelnetPort",
            "TelnetPassword": "txt_TelnetPassword",
            "AdminFileName": "txt_AdminFileName",
            "UserDataFolder": "txt_UserDataFolder",
            
            # Page 4: World
            "GameWorld": "txt_GameWorld",
            "WorldGenSize": "txt_WorldGenSize",
            "WorldGenSeed": "txt_WorldGenSeed",
            "GameName": "txt_GameName",
            "GameMode": "txt_GameMode",
            
            # Page 5: Difficulty
            "GameDifficulty": "txt_GameDifficulty",
            "DayNightLength": "txt_DayNightLength",
            "DayLightLength": "txt_DayLightLength",
            "XPMultiplier": "txt_XPMultiplier",
            "BlockDamagePlayer": "txt_BlockDamagePlayer",
            
            # Page 6: Rules
            "DropOnDeath": "combo_DropOnDeath",
            "DropOnQuit": "combo_DropOnQuit",
            "PlayerKillingMode": "combo_PlayerKillingMode",
            "BloodMoonFrequency": "txt_BloodMoonFrequency",
            
            # Page 7: Zombies
            "EnemySpawnMode": "combo_EnemySpawnMode",
            "BloodMoonEnemyCount": "txt_BloodMoonEnemyCount",
            "ZombieMove": "combo_ZombieMove",
            "ZombieMoveNight": "combo_ZombieMoveNight",
            "ZombieFeralMove": "combo_ZombieFeralMove",
            
            # Page 8: Loot
            "LootAbundance": "txt_LootAbundance",
            "LootRespawnDays": "txt_LootRespawnDays",
            "AirDropFrequency": "txt_AirDropFrequency",
            "PartySharedKillRange": "txt_PartySharedKillRange",
            
            # Page 9: Land Claim
            "LandClaimSize": "txt_LandClaimSize",
            "LandClaimDeadZone": "txt_LandClaimDeadZone",
            "LandClaimExpiryTime": "txt_LandClaimExpiryTime",
            "EACEnabled": "combo_EACEnabled"
        }

    # region [READ_LOGIC]
    def load_from_xml(self):
        """
        Reads serverconfig.xml.
        1. Parses Values using ElementTree.
        2. Parses Comments/Help using Raw Text Regex.
        3. Populates UI Widgets and Help Labels.
        """
        # Resolve path
        if not os.path.exists(self.target_file):
            cwd_path = os.path.join(os.getcwd(), "serverconfig.xml")
            if os.path.exists(cwd_path):
                self.target_file = cwd_path
            else:
                print(f"[BRIDGE] Warning: {self.target_file} not found. Skipping load.")
                return False

        # Phase 1: Value Parsing (ElementTree)
        try:
            tree = ET.parse(self.target_file)
            root = tree.getroot()
            
            for prop in root.findall('property'):
                name = prop.get('name')
                value = prop.get('value')
                
                if name in self.property_map:
                    widget_name = self.property_map[name]
                    self._set_widget_value(widget_name, value)
                    
        except Exception as e:
            print(f"[BRIDGE] XML Value Parse Error: {e}")
            return False

        # Phase 2: Comment/Help Parsing (Raw Text)
        try:
            self._scrape_help_text()
        except Exception as e:
            print(f"[BRIDGE] Help Text Scrape Error: {e}")

        print(f"[BRIDGE] XML Data & Intelligence Loaded: {self.target_file}")
        return True

    def _scrape_help_text(self):
        """
        Reads the raw file to extract <!-- comments --> associated with properties.
        """
        with open(self.target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Dictionary to store found descriptions: { "GameDifficulty": "0-5..." }
        descriptions = {}
        
        # Regex to find property name: name="SomeProp"
        name_pattern = re.compile(r'name="(\w+)"')
        # Regex to find comment: <!-- text -->
        comment_pattern = re.compile(r'<!--(.*?)-->')

        for i, line in enumerate(lines):
            # Check if this line defines a property
            name_match = name_pattern.search(line)
            if name_match:
                prop_name = name_match.group(1)
                
                # Strategy: Look for comment on SAME line, or NEXT line
                comment_text = ""
                
                # Check Same Line
                comment_match = comment_pattern.search(line)
                if comment_match:
                    comment_text = comment_match.group(1).strip()
                
                # If not found, check Next Line (commonly used in 7D2D config)
                elif i + 1 < len(lines):
                    next_line = lines[i+1]
                    next_comment_match = comment_pattern.search(next_line)
                    if next_comment_match:
                        comment_text = next_comment_match.group(1).strip()

                if comment_text:
                    descriptions[prop_name] = comment_text

        # Inject into UI
        self._inject_descriptions(descriptions)

    def _inject_descriptions(self, descriptions):
        """
        Updates the 'lbl_help_X' widgets in the UI.
        """
        for xml_key, widget_name in self.property_map.items():
            if xml_key in descriptions:
                # Construct help label name: lbl_help_ServerName
                help_widget_name = f"lbl_help_{xml_key}"
                
                if hasattr(self.ui, help_widget_name):
                    help_label = getattr(self.ui, help_widget_name)
                    if isinstance(help_label, QLabel):
                        help_label.setText(descriptions[xml_key])
                        # Optional: Style update to indicate success
                        # help_label.setStyleSheet("color: #00FFCC; font-size: 10px;")

    def _set_widget_value(self, widget_name, value):
        """
        Helper: Finds the widget by name and sets its value/text.
        """
        if hasattr(self.ui, widget_name):
            widget = getattr(self.ui, widget_name)
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
                widget.setCursorPosition(0) # Reset cursor to start
            elif isinstance(widget, QComboBox):
                # Try to match the text (case-insensitive search is harder, assuming exact match)
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    # Handle boolean conversion for combos (true/false)
                    lower_val = str(value).lower()
                    if lower_val == "true":
                        idx_t = widget.findText("true")
                        if idx_t >= 0: widget.setCurrentIndex(idx_t)
                    elif lower_val == "false":
                        idx_f = widget.findText("false")
                        if idx_f >= 0: widget.setCurrentIndex(idx_f)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(str(value).lower() == "true")
    # endregion

    # region [WRITE_LOGIC]
    def save_to_xml(self):
        """
        Reads the UI widgets and updates serverconfig.xml.
        """
        if not os.path.exists(self.target_file):
            return False

        try:
            # Create a backup
            shutil.copy2(self.target_file, self.target_file + ".bak")
            
            tree = ET.parse(self.target_file)
            root = tree.getroot()
            
            changes_count = 0
            
            for xml_key, widget_name in self.property_map.items():
                new_value = self._get_widget_value(widget_name)
                
                if new_value is not None:
                    # Search for property
                    for prop in root.findall('property'):
                        if prop.get('name') == xml_key:
                            # Only update if changed
                            if prop.get('value') != str(new_value):
                                prop.set('value', str(new_value))
                                changes_count += 1
                            break
            
            # Write back
            tree.write(self.target_file, encoding="UTF-8", xml_declaration=True)
            print(f"[BRIDGE] Saved {changes_count} settings to {self.target_file}")
            return True

        except Exception as e:
            print(f"[BRIDGE] Save Error: {e}")
            return False

    def _get_widget_value(self, widget_name):
        """
        Helper: Finds the widget and extracts its current value.
        """
        if hasattr(self.ui, widget_name):
            widget = getattr(self.ui, widget_name)
            
            if isinstance(widget, QLineEdit):
                return widget.text()
            elif isinstance(widget, QComboBox):
                return widget.currentText()
            elif isinstance(widget, QCheckBox):
                return "true" if widget.isChecked() else "false"
        
        return None
    # endregion