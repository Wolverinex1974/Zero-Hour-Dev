# =========================================================
# ZERO HOUR CORE: SETTINGS BRIDGE - v21.2
# =========================================================
# ROLE: Translator between UI Widgets, Registry, and XML
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16.5 UPDATE:
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# SURGERY: Added RAT Parity mappings for WorldGenName, 
#          TwitchServerPermission, and DynamicMeshEnabled.
# FEATURE: ARKASM UI Redesign integration. Purged HTML Tooltips.
#          XML comments are now injected as static text into 
#          the new 3rd-column UI labels for instant readability.
# =========================================================

import os
import logging
from PySide6.QtWidgets import QLineEdit, QComboBox, QCheckBox, QSpinBox, QTimeEdit
from PySide6.QtCore import QTime

from core.app_state import state
from core.registry import RegistryEngine
from core.xml_parser import XMLConfigParser

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class SettingsBridge:
    """
    The Diplomat.
    It reads the UI state, updates the Registry, and commits to XML.
    It also pulls data from XML to hydrate the UI.
    """
    def __init__(self, ui_reference):
        self.ui = ui_reference
        self.xml_parser = None
        
        # MAPPING: UI Widget Name -> ServerConfig Property Name
        # This dictionary links the visual input to the actual data key.
        self.ui_map = dict()
        self.ui_map.update({"txt_ServerName": "ServerName"})
        self.ui_map.update({"txt_ServerDescription": "ServerDescription"})
        self.ui_map.update({"txt_ServerWebsiteURL": "ServerWebsiteURL"})
        self.ui_map.update({"txt_ServerPassword": "ServerPassword"})
        self.ui_map.update({"combo_WebDashboardEnabled": "WebDashboardEnabled"})
        
        self.ui_map.update({"txt_ServerPort": "ServerPort"})
        self.ui_map.update({"txt_ServerMaxPlayerCount": "ServerMaxPlayerCount"})
        self.ui_map.update({"txt_ServerVisibility": "ServerVisibility"})
        
        self.ui_map.update({"combo_TelnetEnabled": "TelnetEnabled"})
        self.ui_map.update({"txt_TelnetPort": "TelnetPort"})
        self.ui_map.update({"txt_TelnetPassword": "TelnetPassword"})
        self.ui_map.update({"txt_AdminID": "AdminFileName"}) 
        
        self.ui_map.update({"combo_GameWorld": "GameWorld"})
        self.ui_map.update({"combo_WorldGenName": "WorldGenName"})
        self.ui_map.update({"txt_WorldGenSeed": "WorldGenSeed"})
        self.ui_map.update({"txt_WorldGenSize": "WorldGenSize"})
        
        self.ui_map.update({"combo_GameDifficulty": "GameDifficulty"})
        self.ui_map.update({"txt_XPMultiplier": "XPMultiplier"})
        self.ui_map.update({"txt_BlockDamagePlayer": "BlockDamagePlayer"})
        
        self.ui_map.update({"txt_DayNightLength": "DayNightLength"})
        self.ui_map.update({"txt_DayLightLength": "DayLightLength"})
        self.ui_map.update({"combo_DropOnDeath": "DropOnDeath"})
        
        self.ui_map.update({"txt_MaxSpawnedZombies": "MaxSpawnedZombies"})
        self.ui_map.update({"txt_BloodMoonFrequency": "BloodMoonFrequency"})
        self.ui_map.update({"txt_BloodMoonEnemyCount": "BloodMoonEnemyCount"})
        
        self.ui_map.update({"txt_LootAbundance": "LootAbundance"})
        self.ui_map.update({"txt_LootRespawnDays": "LootRespawnDays"})
        self.ui_map.update({"txt_AirDropFrequency": "AirDropFrequency"})
        
        self.ui_map.update({"txt_LandClaimCount": "LandClaimCount"})
        self.ui_map.update({"txt_LandClaimSize": "LandClaimSize"})
        self.ui_map.update({"combo_EACEnabled": "EACEnabled"})
        self.ui_map.update({"combo_TwitchServerPermission": "TwitchServerPermission"})
        self.ui_map.update({"combo_DynamicMeshEnabled": "DynamicMeshEnabled"})

    def load_settings_into_ui(self):
        """
        1. Reads serverconfig.xml via XMLParser.
        2. Scrapes Comments for Static Help Labels (ARKASM-style).
        3. Updates the Registry.
        4. Populates UI Widgets.
        """
        if not state.server_path:
            return

        self.xml_parser = XMLConfigParser(state.server_path)
        
        # 1. Read Data & Comments
        xml_data = self.xml_parser.read_config()
        help_definitions = self.xml_parser.extract_help_definitions()
        
        if not xml_data:
            log.warning(" XML Read returned empty.")
            return

        # Normalize the help dictionary to be completely case-insensitive
        normalized_help = dict()
        for original_key, help_text in help_definitions.items():
            normalized_key = str(original_key).lower().strip()
            normalized_help.update({normalized_key: help_text})

        # 2. Update Registry
        if state.registry:
            for key, val in xml_data.items():
                # We prefix with 'srv_' to distinguish server props from app props
                state.registry.set(f"srv_{key}", val)
            
            state.registry.save_local()

        # 3. Populate UI & Inject Static Help Text
        log.info(" Hydrating UI from XML data...")
        
        for widget_name, property_key in self.ui_map.items():
            
            # Fetch the Main Input Widget (Text Box / Combo Box)
            widget = getattr(self.ui, widget_name, None)
            if not widget:
                continue
                
            # A. Set Main Value
            value = xml_data.get(property_key)
            if value is not None:
                self._set_widget_value(widget, value)
                
            # B. Target the Static Help Label (Created dynamically in admin_layouts.py)
            help_label_name = f"lbl_help_{property_key}"
            help_label = getattr(self.ui, help_label_name, None)
            
            if help_label is not None:
                search_key = str(property_key).lower().strip()
                raw_help = normalized_help.get(search_key)
                
                if raw_help is not None:
                    # Clean up the raw XML comment text for a clean UI read
                    clean_help = raw_help.replace("<!--", "").replace("-->", "").strip()
                    help_label.setText(clean_help)
                else:
                    help_label.setText("No official description available.")

    def save_settings_from_ui(self):
        """
        1. Reads values from UI Widgets.
        2. Updates Registry.
        3. Writes to serverconfig.xml via XMLParser.
        """
        if not state.server_path:
            log.error(" Save failed: No server path.")
            return False

        self.xml_parser = XMLConfigParser(state.server_path)
        registry_updates = dict()
        
        log.info(" Harvesting UI data...")
        
        for widget_name, property_key in self.ui_map.items():
            widget = getattr(self.ui, widget_name, None)
            if not widget:
                continue
                
            value = self._get_widget_value(widget)
            
            # Store for XML writer using safe .update()
            registry_updates.update({property_key: value})
            
            # Store in Registry
            if state.registry:
                state.registry.set(f"srv_{property_key}", value)

        # Commit to Disk
        success = self.xml_parser.write_config(registry_updates)
        
        if success and state.registry:
            state.registry.save_local()
            
        return success

    def _set_widget_value(self, widget, value):
        """ Internal helper to handle different widget types safely. """
        try:
            val_str = str(value)
            
            if isinstance(widget, QLineEdit):
                widget.setText(val_str)
                widget.setCursorPosition(0)
                
            elif isinstance(widget, QComboBox):
                # Try to find the item, if not found, add it temporarily or ignore
                index = widget.findText(val_str)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    # For things like 'GameWorld', we might need to add it dynamically from XML
                    widget.addItem(val_str)
                    widget.setCurrentText(val_str)
                    
            elif isinstance(widget, QCheckBox):
                widget.setChecked(val_str.lower() == "true")
                
            elif isinstance(widget, QSpinBox):
                if val_str.isdigit():
                    widget.setValue(int(val_str))
                    
        except Exception as e:
            log.warning(f" Widget Set Error: {e}")

    def _get_widget_value(self, widget):
        """ Internal helper to extract values based on widget type safely. """
        try:
            if isinstance(widget, QLineEdit):
                return widget.text().strip()
                
            elif isinstance(widget, QComboBox):
                return widget.currentText()
                
            elif isinstance(widget, QCheckBox):
                return "true" if widget.isChecked() else "false"
                
            elif isinstance(widget, QSpinBox):
                return str(widget.value())
                
            return ""
            
        except Exception as e:
            log.warning(f" Widget Get Error: {e}")
            return ""