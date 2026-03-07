# =========================================================
# ZERO HOUR CORE: STORE MANAGER - v20.8
# =========================================================
# ROLE: Sovereign Storefront Controller & Item Scanner
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16.5 UPDATE (POLISH):
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# FEATURE: Added Industrial Dark Theme to ItemScannerDialog.
# FEATURE: Added "Top 100" UX warning label for smooth scrolling.
# =========================================================

import os
import logging
import xml.etree.ElementTree as ET
import datetime
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, 
    QProgressBar
)
from PySide6.QtCore import (Qt, QThread, Signal, QObject, QCoreApplication)
from PySide6.QtGui import (QColor)

from core.app_state import state

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class ItemScannerWorker(QThread):
    """
    Background Thread that scans items.xml files without freezing the UI.
    Scans:
    1. Vanilla: /Data/Config/items.xml
    2. Mods: /Mods/*/Config/items.xml
    """
    item_found_signal = Signal(str, str, int) 
    progress_signal = Signal(str)
    finished_signal = Signal(int) 

    def __init__(self, server_path):
        super().__init__()
        self.server_path = server_path
        self.is_running = False

    def run(self):
        self.is_running = True
        total_found = 0
        
        # 1. SCAN VANILLA
        vanilla_path = os.path.join(self.server_path, "Data", "Config", "items.xml")
        
        if os.path.exists(vanilla_path):
            self.progress_signal.emit("Scanning Vanilla Items...")
            total_found = total_found + self._parse_xml_file(vanilla_path)

        # 2. SCAN MODS
        mods_dir = os.path.join(self.server_path, "Mods")
        
        if os.path.exists(mods_dir):
            for mod_name in os.listdir(mods_dir):
                if not self.is_running: 
                    break
                
                mod_config_path = os.path.join(mods_dir, mod_name, "Config", "items.xml")
                
                # Check alternative casing
                if not os.path.exists(mod_config_path):
                    mod_config_path = os.path.join(mods_dir, mod_name, "config", "items.xml")
                
                if os.path.exists(mod_config_path):
                    self.progress_signal.emit(f"Scanning Mod: {mod_name}...")
                    total_found = total_found + self._parse_xml_file(mod_config_path)

        self.finished_signal.emit(total_found)

    def _parse_xml_file(self, file_path):
        """
        Parses a single XML file.
        Uses incremental parsing to keep memory usage low.
        Extracts: Name, ID (Name attribute), and EconomicValue.
        """
        count = 0
        try:
            # We use iterparse to handle large files efficiently
            context = ET.iterparse(file_path, events=tuple(("start", "end")))
            context = iter(context)
            event, root = next(context)

            for event, elem in context:
                if event == "end" and elem.tag == "item":
                    item_id = elem.get("name")
                    
                    # Extract EconomicValue if present
                    econ_value = 10 
                    
                    # Search children properties
                    for prop in elem.findall("property"):
                        p_name = prop.get("name")
                        if p_name == "EconomicValue":
                            try:
                                econ_value = int(prop.get("value"))
                            except Exception:
                                pass
                            break
                    
                    # We emit the item immediately
                    if item_id:
                        # Skip technical/hidden items to keep the shop clean
                        if "hand" not in item_id.lower(): 
                            self.item_found_signal.emit(item_id, item_id, econ_value)
                            count = count + 1
                    
                    root.clear() 
                    
        except Exception as e:
            log.warning(f" Failed to parse {file_path}: {e}")
            
        return count

    def stop(self):
        self.is_running = False

class ItemScannerDialog(QDialog):
    """
    The Pop-up Window that runs the scan and lets admins 
    add items directly to their shop manifest.
    """
    def __init__(self, parent_manager):
        super().__init__()
        self.manager = parent_manager
        self.setWindowTitle("Sovereign Store: Item Scanner")
        self.resize(800, 600)
        
        self.scanned_items = list()
        self.scanner_worker = None
        
        self.setup_ui()
        self.start_scan()

    def setup_ui(self):
        # Apply Industrial Dark Theme specifically to the pop-up dialog
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #ecf0f1; }
            QLabel { color: #ecf0f1; font-weight: bold; }
            QLineEdit { background-color: #2d2d2d; color: #2ecc71; border: 1px solid #555; padding: 6px; }
            QPushButton { background-color: #3d3d3d; color: white; border: 1px solid #555; padding: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #4d4d4d; border: 1px solid #9b59b6; }
            QTableWidget { background-color: #252525; color: #ecf0f1; gridline-color: #333; border: 1px solid #555; }
            QHeaderView::section { background-color: #1a1a1a; color: #9b59b6; font-weight: bold; border: 1px solid #333; padding: 4px; }
        """)

        main_layout = QVBoxLayout(self)
        
        # --- Top Bar ---
        top_layout = QHBoxLayout()
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search items (e.g., '762', 'steel')...")
        self.txt_search.textChanged.connect(self.filter_scanned_list)
        
        self.btn_refresh = QPushButton("RE-SCAN")
        self.btn_refresh.clicked.connect(self.start_scan)
        
        top_layout.addWidget(QLabel("Search:"))
        top_layout.addWidget(self.txt_search)
        top_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(top_layout)
        
        # --- UX Warning Label ---
        self.lbl_warning = QLabel("Displaying top 100 results to guarantee zero UI lag. Please use the search filter to locate specific items.")
        self.lbl_warning.setStyleSheet("color: #f1c40f; font-style: italic; font-weight: normal; font-size: 11px;")
        main_layout.addWidget(self.lbl_warning)
        
        # --- Table ---
        self.table_scanner = QTableWidget()
        self.table_scanner.setColumnCount(3)
        
        # Bracket-proof Header Injection
        scanner_headers = list(("Item ID (Game Name)", "Base Value", "Action"))
        self.table_scanner.setHorizontalHeaderLabels(scanner_headers)
        
        header = self.table_scanner.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        main_layout.addWidget(self.table_scanner)
        
        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #555; border-radius: 2px; text-align: center; color: white; font-weight: bold; background-color: #2d2d2d; }
            QProgressBar::chunk { background-color: #9b59b6; }
        """)
        main_layout.addWidget(self.progress_bar)

    def start_scan(self):
        if not state.server_path:
            QMessageBox.warning(self, "Error", "No Server Path Configured.")
            return

        self.table_scanner.setRowCount(0)
        self.scanned_items = list()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) 
        
        self.scanner_worker = ItemScannerWorker(state.server_path)
        self.scanner_worker.item_found_signal.connect(self.on_item_found)
        self.scanner_worker.progress_signal.connect(lambda msg: self.progress_bar.setFormat(msg))
        self.scanner_worker.finished_signal.connect(self.on_scan_finished)
        self.scanner_worker.start()

    def on_item_found(self, name, item_id, value):
        new_tuple = tuple((item_id, value))
        self.scanned_items.append(new_tuple)

    def on_scan_finished(self, total):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        log.info(f" Scan complete. Found {total} items.")
        self.filter_scanned_list("") 

    def filter_scanned_list(self, query):
        query = query.lower()
        
        filtered = list()
        for x in self.scanned_items:
            item_name = x.__getitem__(0)
            if query in item_name.lower():
                filtered.append(x)
        
        # Limit rendering to 100 items to prevent UI lag while typing
        display_limit = 100
        render_count = min(len(filtered), display_limit)
        self.table_scanner.setRowCount(render_count)
        
        for i in range(render_count):
            item_data = filtered.__getitem__(i)
            item_id = item_data.__getitem__(0)
            value = item_data.__getitem__(1)
            
            self.table_scanner.setItem(i, 0, QTableWidgetItem(item_id))
            self.table_scanner.setItem(i, 1, QTableWidgetItem(str(value)))
            
            btn_add = QPushButton("ADD TO STORE")
            btn_add.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            
            # Using default argument binding to prevent lambda loop bugs
            def make_add_callback(i_id=item_id, val=value):
                def callback():
                    self.manager.add_item_to_shop(i_id, val)
                return callback
                
            btn_add.clicked.connect(make_add_callback())
            self.table_scanner.setCellWidget(i, 2, btn_add)

    def closeEvent(self, event):
        if self.scanner_worker:
            self.scanner_worker.stop()
        event.accept()

class StoreManager(QObject):
    """
    The Controller for Tab 9: Store Manager.
    Wires the UI buttons to the Database and handles the 
    GitHub direct-JSON cloud syncing.
    """
    def __init__(self, ui_reference, database_instance, github_engine=None):
        super().__init__()
        self.ui = ui_reference
        self.db = database_instance
        self.github = github_engine
        
        # Setup Table Headers (Bracket-Proofed)
        headers = list(("Command Alias (/buy...)", "Game Item ID", "Price (ZB)", "Category", "Stock"))
        self.ui.table_store_items.setColumnCount(len(headers))
        self.ui.table_store_items.setHorizontalHeaderLabels(headers)
        
        h2 = self.ui.table_store_items.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.Interactive)
        self.ui.table_store_items.setColumnWidth(0, 150)
        h2.setSectionResizeMode(1, QHeaderView.Stretch)
        h2.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h2.setSectionResizeMode(3, QHeaderView.Interactive)
        self.ui.table_store_items.setColumnWidth(3, 150)
        h2.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # Wire UI Buttons
        self.ui.btn_store_add.clicked.connect(self.open_scanner_dialog)
        self.ui.btn_store_remove.clicked.connect(self.remove_selected_item)
        self.ui.btn_store_sync.clicked.connect(self.publish_store_to_cloud)
        
        # Auto-Save Hook: Trigger database update when user types in the table
        self.ui.table_store_items.itemChanged.connect(self.save_manifest_to_db)
        
        self.load_manifest_into_ui()

    def open_scanner_dialog(self):
        self.dialog = ItemScannerDialog(self)
        self.dialog.exec()

    def add_item_to_shop(self, item_id, base_value):
        """ Invoked by the Dialog when an Admin clicks 'Add to Store'. """
        
        # Try to make a smart alias (e.g. 'ammo762mmBulletBall' -> '762')
        smart_alias = item_id.lower()
        if "ammo" in smart_alias:
            smart_alias = smart_alias.replace("ammo", "").replace("bulletball", "").replace("bullet", "")
            
        # Add to SQLite
        self.db.add_shop_item(item_id, smart_alias, base_value, "General")
        log.info(f" Added item to Store: {item_id}")
        
        # Refresh the Tab 9 UI
        self.load_manifest_into_ui()

    def remove_selected_item(self):
        row = self.ui.table_store_items.currentRow()
        if row < 0:
            return
            
        # Get the immutable Game ID from column 1
        item_id = self.ui.table_store_items.item(row, 1).text()
        
        # Execute safe raw SQL to remove it since DB wrapper might lack remove_shop_item
        try:
            self.db.cursor.execute("DELETE FROM shop_manifest WHERE item_id=?", tuple((item_id,)))
            self.db.conn.commit()
            log.info(f" Removed item from Store: {item_id}")
            self.load_manifest_into_ui()
        except Exception as e:
            log.error(f" Failed to delete item {item_id}: {e}")

    def load_manifest_into_ui(self):
        """ Hydrates Tab 9 from SQLite. """
        # Disable auto-save hook while loading to prevent infinite loops
        self.ui.table_store_items.blockSignals(True)
        
        manifest = self.db.get_shop_manifest()
        self.ui.table_store_items.setRowCount(len(manifest))
        
        for i, entry in enumerate(manifest):
            # Tuple extraction without brackets
            item_id = entry.__getitem__(0)
            alias = entry.__getitem__(1)
            cost = entry.__getitem__(2)
            category = entry.__getitem__(3) if len(entry) > 3 else "General"
            stock = entry.__getitem__(4) if len(entry) > 4 else -1
            
            # 0. Alias
            self.ui.table_store_items.setItem(i, 0, QTableWidgetItem(str(alias)))
            
            # 1. Game ID (Read Only)
            id_item = QTableWidgetItem(str(item_id))
            id_item.setFlags(id_item.flags() ^ Qt.ItemIsEditable)
            id_item.setForeground(QColor("#7f8c8d"))
            self.ui.table_store_items.setItem(i, 1, id_item)
            
            # 2. Cost
            self.ui.table_store_items.setItem(i, 2, QTableWidgetItem(str(cost)))
            
            # 3. Category
            self.ui.table_store_items.setItem(i, 3, QTableWidgetItem(str(category)))
            
            # 4. Stock (-1 = Infinite)
            self.ui.table_store_items.setItem(i, 4, QTableWidgetItem(str(stock)))

        self.ui.table_store_items.blockSignals(False)

    def save_manifest_to_db(self, changed_item):
        """ AUTO-SAVE LOGIC: Triggered when user edits a cell in the table. """
        row = changed_item.row()
        
        try:
            # Re-read the whole row
            alias = self.ui.table_store_items.item(row, 0).text()
            item_id = self.ui.table_store_items.item(row, 1).text()
            cost_str = self.ui.table_store_items.item(row, 2).text()
            category = self.ui.table_store_items.item(row, 3).text()
            stock_str = self.ui.table_store_items.item(row, 4).text()
            
            cost = int(cost_str) if cost_str.isdigit() else 9999
            
            # Stock parsing (Allow negatives for infinite)
            stock = -1
            try:
                stock = int(stock_str)
            except Exception:
                pass
                
            # Upsert into DB
            self.db.add_shop_item(item_id, alias, cost, category, stock)
            
        except Exception as e:
            log.warning(f" Auto-save failed on row {row}: {e}")

    def publish_store_to_cloud(self):
        """
        The Iron Bridge Direct-Sync.
        Pulls data from DB, builds JSON, beams to GitHub.
        """
        if not self.github:
            QMessageBox.warning(None, "Cloud Error", "GitHub Engine is offline. Check Setup Tab.")
            return
            
        if not state.current_profile_name:
            QMessageBox.warning(None, "Profile Error", "No active profile loaded.")
            return

        self.ui.btn_store_sync.setText("PUBLISHING TO CLOUD...")
        self.ui.btn_store_sync.setEnabled(False)
        QCoreApplication.processEvents()
        
        try:
            manifest = self.db.get_shop_manifest()
            
            # Build the Sovereign Payload without brackets
            shop_data = dict()
            shop_data.update({"server_profile": state.current_profile_name})
            shop_data.update({"currency": "ZombieBucks"})
            shop_data.update({"last_updated": datetime.datetime.now().isoformat()})
            
            items_list = list()
            
            for entry in manifest:
                item_data = dict()
                item_data.update({"game_id": entry.__getitem__(0)})
                item_data.update({"alias": entry.__getitem__(1)})
                item_data.update({"price": entry.__getitem__(2)})
                
                cat = entry.__getitem__(3) if len(entry) > 3 else "General"
                item_data.update({"category": cat})
                
                stk = entry.__getitem__(4) if len(entry) > 4 else -1
                item_data.update({"stock": stk})
                
                items_list.append(item_data)
                
            shop_data.update({"items": items_list})
                
            # Construct Remote Path
            safe_name = state.current_profile_name.lower().replace(' ', '_')
            remote_filename = f"shop_{safe_name}.json"
            
            # Engage Binary Beam
            success = self.github.commit_json(
                remote_filename, 
                shop_data, 
                f"Automated Storefront Sync: {len(manifest)} items"
            )
            
            if success:
                QMessageBox.information(None, "Success", f"Storefront published!\nThe Client can now fetch {len(manifest)} items.")
            else:
                QMessageBox.warning(None, "Failure", "Failed to beam JSON to GitHub API.")
                
        except Exception as e:
            log.error(f" Cloud Publish Error: {e}")
            QMessageBox.critical(None, "Critical Error", f"Sync failed: {str(e)}")
            
        finally:
            self.ui.btn_store_sync.setText("PUBLISH STORE TO CLOUD")
            self.ui.btn_store_sync.setEnabled(True)