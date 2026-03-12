# =========================================================
# ZERO HOUR CORE: MOD CONTROLLER - v23.2
# =========================================================
# ROLE: Physical File and Manifest Orchestration
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 19.2: THE WEB-SAFE UNIFORMITY GAUNTLET
# FEATURE: Implemented strict alphanumeric, dot, and underscore
#          formatting. Instantly strips () and prevents GitHub's 
#          Garbage Collector from destroying mismatched zip names.
# FEATURE: Squeezes double underscores and converts hyphens.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import os
import shutil
import re
import logging
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QComboBox, QWidget, QHBoxLayout, QPushButton
from PySide6.QtGui import QColor

from core.app_state import state
from core.manifest_manager import get_manifest, save_manifest, update_mod_metadata, remove_mod_from_manifest

log = logging.getLogger("Paradoxal")

class ModController:
    """
    Handles all physical folder operations and manifest synchronization 
    for the Mod Architect tab.
    """
    def __init__(self, main_window_ref):
        self.hub = main_window_ref

    def _get_prefix(self, folder_name):
        if not folder_name:
            return 0
            
        pattern = re.compile(r"^(\d+)_(.*)$")
        match = pattern.match(folder_name)
        
        if match:
            return int(match.group(1))
            
        return 0

    def _strip_all_prefixes_and_spaces(self, folder_name):
        if not folder_name:
            return "Unknown"
            
        clean_name = folder_name
        pattern = re.compile(r"^\d+_(.*)$")
        match = pattern.match(clean_name)
        
        while match:
            clean_name = match.group(1)
            match = pattern.match(clean_name)
            
        # STAGE 1: Convert spaces and hyphens to underscores for readability
        clean_name = clean_name.replace(" ", "_")
        clean_name = clean_name.replace("-", "_")
        
        # STAGE 2: The Purge. Strictly allow ONLY alphanumeric, dots, and underscores.
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_."
        sanitized_name = ""
        
        for char in clean_name:
            if char in allowed_chars:
                sanitized_name = sanitized_name + char
                
        clean_name = sanitized_name
        
        # STAGE 3: The Squeeze. Compress multiple underscores into a single one.
        while "__" in clean_name:
            clean_name = clean_name.replace("__", "_")
            
        # STAGE 4: Clean up hanging edges
        clean_name = clean_name.strip("_")
        
        if not clean_name:
            clean_name = "UnknownMod"
            
        return clean_name

    def _rename_mod_physically(self, mod_dict, new_folder_name):
        old_folder = mod_dict.get("folder_name")
        if old_folder == new_folder_name:
            return False
            
        base_path = state.mods_path
        old_path = os.path.join(base_path, old_folder)
        new_path = os.path.join(base_path, new_folder_name)
        
        try:
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                mod_dict.update({"folder_name": new_folder_name})
                
                # PHASE 18 AMNESIA FIX: Force Forge to re-upload renamed mod
                mod_dict.update({"hash": "PENDING"})
                mod_dict.update({"folder_hash": ""})
                mod_dict.update({"download_urls": list()})
                
                self.hub.add_system_log(f"RENAMED (Amnesia): {old_folder} -> {new_folder_name}")
                return True
        except Exception as e:
            self.hub.add_system_log(f"RENAME FAILED: {old_folder} ({e})")
            
        return False

    def mass_rebalance_prefixes(self, mod_list):
        """
        Only runs when the gaps run out (e.g. 001, 002, 003).
        Spreads all mods out to 010, 020, 030 to create infinite gaps.
        """
        self.hub.add_system_log("MASS REBALANCE: Converting ecosystem to 10-Step Gap Architecture...")
        
        for index, mod in enumerate(mod_list):
            clean_name = self._strip_all_prefixes_and_spaces(mod.get("folder_name"))
            new_prefix_val = (index + 1) * 10
            new_folder_name = f"{new_prefix_val:03d}_{clean_name}"
            self._rename_mod_physically(mod, new_folder_name)

    def enforce_soft_formatting(self, mod_list):
        """
        Quietly gives new, unformatted mods a prefix at the very end 
        of the list without disturbing the existing load order gaps.
        """
        max_prefix = 0
        for mod in mod_list:
            p = self._get_prefix(mod.get("folder_name"))
            if p > max_prefix:
                max_prefix = p
                
        changed = False
        for mod in mod_list:
            p = self._get_prefix(mod.get("folder_name"))
            if p == 0:
                max_prefix = max_prefix + 10
                clean_name = self._strip_all_prefixes_and_spaces(mod.get("folder_name"))
                new_folder_name = f"{max_prefix:03d}_{clean_name}"
                
                if self._rename_mod_physically(mod, new_folder_name):
                    changed = True
                    
        return changed

    def action_mod_move(self, direction):
        if state.server_process_active:
            QMessageBox.warning(self.hub, "Safety Lock", "Cannot rename mod folders while server is running.")
            return

        row = self.hub.ui.table_mods.currentRow()
        if row < 0: 
            return
        
        manifest = get_manifest(state.manifest_path)
        mods = manifest.get("mods", list())
        
        if not mods or row >= len(mods): 
            return
        
        target_idx = row - 1 if direction == "UP" else row + 1
        
        if 0 <= target_idx < len(mods):
            item_a = mods.pop(row)
            mods.insert(target_idx, item_a)
            
            # --- PHASE 19.1: 10-STEP GAP LOGIC ---
            prev_prefix = 0
            if target_idx > 0:
                prev_mod = mods.__getitem__(target_idx - 1)
                prev_prefix = self._get_prefix(prev_mod.get("folder_name"))

            next_prefix = prev_prefix + 20
            if target_idx < (len(mods) - 1):
                next_mod = mods.__getitem__(target_idx + 1)
                next_prefix = self._get_prefix(next_mod.get("folder_name"))
                
            if next_prefix <= prev_prefix:
                next_prefix = prev_prefix + 20

            gap = next_prefix - prev_prefix
            if gap > 1:
                # Room to slide in! 0 Cascades.
                new_prefix_val = prev_prefix + int(gap / 2)
                clean_name = self._strip_all_prefixes_and_spaces(item_a.get("folder_name"))
                new_folder_name = f"{new_prefix_val:03d}_{clean_name}"
                self._rename_mod_physically(item_a, new_folder_name)
            else:
                # Gap depleted. Trigger 1-time mass rebalance.
                self.hub.add_system_log("GAP DEPLETED: Triggering Mass Rebalance (This will cause a cascade upload)...")
                self.mass_rebalance_prefixes(mods)
            
            manifest.update({"mods": mods})
            save_manifest(manifest, state.manifest_path)
            
            self.refresh_mod_list()
            self.hub.ui.table_mods.selectRow(target_idx)

    def toggle_mod_state(self, folder_name, to_disabled):
        try:
            if to_disabled:
                src = os.path.join(state.mods_path, folder_name)
                dst = os.path.join(state.disabled_mods_path, folder_name)
            else:
                src = os.path.join(state.disabled_mods_path, folder_name)
                dst = os.path.join(state.mods_path, folder_name)
                
            if os.path.exists(src):
                shutil.move(src, dst)
                self.refresh_mod_list()
                status_text = "DISABLED" if to_disabled else "ENABLED"
                self.hub.add_system_log(f"MOD {status_text}: {folder_name}")
            else: 
                QMessageBox.warning(self.hub, "Error", "Source folder not found.")
        except Exception as e: 
            QMessageBox.critical(self.hub, "Error", f"Failed to move mod: {str(e)}")

    def delete_mod_completely(self, mod_name, folder_name):
        confirm = QMessageBox.question(
            self.hub, 
            "Confirm Delete", 
            f"Are you sure you want to PERMANENTLY DELETE '{mod_name}'?\nThis cannot be undone.", 
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes: 
            return
            
        path_active = os.path.join(state.mods_path, folder_name)
        if os.path.exists(path_active): 
            shutil.rmtree(path_active)
            
        path_disabled = os.path.join(state.disabled_mods_path, folder_name)
        if os.path.exists(path_disabled): 
            shutil.rmtree(path_disabled)
            
        remove_mod_from_manifest(state.manifest_path, folder_name)
        self.refresh_mod_list()
        self.hub.add_system_log(f"MOD DELETED: {mod_name}")

    def refresh_mod_list(self):
        if not os.path.exists(state.mods_path): 
            os.makedirs(state.mods_path, exist_ok=True)
            
        if not os.path.exists(state.disabled_mods_path): 
            os.makedirs(state.disabled_mods_path, exist_ok=True)
            
        vault = get_manifest(state.manifest_path)
        m_list = vault.get("mods")
        
        if not m_list:
            m_list = list()
        
        live_mods = list()
        for f in os.listdir(state.mods_path):
            if os.path.isdir(os.path.join(state.mods_path, f)):
                live_mods.append(f)
                
        disabled_mods = list()
        for f in os.listdir(state.disabled_mods_path):
            if os.path.isdir(os.path.join(state.disabled_mods_path, f)):
                disabled_mods.append(f)
                
        valid_mods = list()
        manifest_changed = False
        
        for m in m_list:
            folder = m.get("folder_name")
            is_active = False
            is_disabled = False
            
            for lm in live_mods:
                if folder == lm:
                    is_active = True
            for dm in disabled_mods:
                if folder == dm:
                    is_disabled = True
                    
            if is_active or is_disabled:
                valid_mods.append(m)
            else:
                self.hub.add_system_log(f"GHOST PURGE: Removed orphaned mod '{folder}' from manifest.")
                manifest_changed = True
                
        m_list = valid_mods
        
        known_names = list()
        for m in m_list:
            known_names.append(m.get("folder_name"))
            
        for f in live_mods:
            found = False
            for kn in known_names:
                if f == kn:
                    found = True
            if not found: 
                m_list.append(self._create_mod_entry(f, f))
                manifest_changed = True
                
        for f in disabled_mods:
            found = False
            for kn in known_names:
                if f == kn:
                    found = True
            if not found: 
                m_list.append(self._create_mod_entry(f, f))
                manifest_changed = True
                
        # PHASE 19: Catch newly added mods and give them a valid 10-step gap prefix
        if self.enforce_soft_formatting(m_list):
            manifest_changed = True
                
        if manifest_changed: 
            vault.update({"mods": m_list})
            save_manifest(vault, state.manifest_path)
            self.hub.apply_dirty_ui_state(True)
            
        self.hub.ui.table_mods.setRowCount(len(m_list))
        
        if len(m_list) == 0: 
            self.hub.add_system_log(" Scan complete. 0 mods found.")
            
        for i, m in enumerate(m_list):
            folder = m.get("folder_name")
            is_active = False
            is_disabled = False
            
            for lm in live_mods:
                if folder == lm:
                    is_active = True
            for dm in disabled_mods:
                if folder == dm:
                    is_disabled = True
                    
            is_ghost = not is_active and not is_disabled
            
            name_item = QTableWidgetItem(m.get("name"))
            if is_ghost: 
                name_item.setForeground(QColor("red"))
            elif is_disabled: 
                name_item.setForeground(QColor("gray"))
                
            self.hub.ui.table_mods.setItem(i, 0, name_item)
            self.hub.ui.table_mods.setItem(i, 1, QTableWidgetItem(folder))
            
            tier_combo = QComboBox()
            tier_combo.addItems(list(("1. Mandatory", "2. Optional", "3. Server Only")))
            tier_combo.setCurrentIndex(m.get("tier", 1) - 1)
            
            def make_tier_callback(f_name):
                def callback(idx):
                    update_mod_metadata(state.manifest_path, f_name, f_name, idx + 1)
                    self.hub.apply_dirty_ui_state(True)
                return callback
                
            tier_combo.currentIndexChanged.connect(make_tier_callback(folder))
            self.hub.ui.table_mods.setCellWidget(i, 2, tier_combo)
            self.hub.ui.table_mods.setItem(i, 3, QTableWidgetItem(m.get("version", "1.0.0")))
            
            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(4)
            
            btn_toggle = QPushButton()
            
            if is_active:
                btn_toggle.setText("DISABLE")
                btn_toggle.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
                btn_toggle.clicked.connect(lambda chk=False, f=folder: self.toggle_mod_state(f, to_disabled=True))
            elif is_disabled:
                btn_toggle.setText("ENABLE")
                btn_toggle.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
                btn_toggle.clicked.connect(lambda chk=False, f=folder: self.toggle_mod_state(f, to_disabled=False))
            else: 
                btn_toggle.setText("MISSING")
                btn_toggle.setEnabled(False)
                btn_toggle.setStyleSheet("background-color: #333; color: #555;")
                
            btn_del = QPushButton("DELETE")
            btn_del.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
            
            if is_ghost: 
                btn_del.setText("PURGE")
                
            btn_del.clicked.connect(lambda chk=False, f=folder, n=m.get("name"): self.delete_mod_completely(n, f))
            
            layout.addWidget(btn_toggle)
            layout.addWidget(btn_del)
            self.hub.ui.table_mods.setCellWidget(i, 4, action_widget)

    def _create_mod_entry(self, name, folder):
        empty_dict = dict()
        empty_dict.update({"name": name})
        empty_dict.update({"folder_name": folder})
        empty_dict.update({"version": "1.0.0"})
        empty_dict.update({"hash": "PENDING"})
        empty_dict.update({"download_urls": list()})
        empty_dict.update({"tier": 1})
        empty_dict.update({"author": "Unknown"})
        empty_dict.update({"description": "Auto-detected"})
        return empty_dict