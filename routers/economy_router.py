import os
import json
import datetime
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

# region [METADATA]
# FILE: routers/economy_router.py
# DESC: Controller for Server Economy
# AUTH: Phase 21 Refactor - v23.0
# endregion

class EconomyRouter(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui
        self.economy_data = {}
        self.data_path = "server_bank.json"
        
        self._setup_connections()

    def _setup_connections(self):
        if hasattr(self.ui, 'btn_refresh_ledger'):
            self.ui.btn_refresh_ledger.clicked.connect(self.load_database)
            
        if hasattr(self.ui, 'btn_credit_player'):
            self.ui.btn_credit_player.clicked.connect(self.transaction_credit)

    def load_database(self):
        if not os.path.exists(self.data_path):
            self.main_window.log_system_event("ECONOMY: No database found.")
            return

        try:
            with open(self.data_path, 'r') as f:
                self.economy_data = json.load(f)
            self.update_ui_table()
            self.main_window.log_system_event("ECONOMY: Ledger Loaded.")
        except Exception as e:
            self.main_window.log_system_event(f"ECONOMY ERROR: {e}")

    def update_ui_table(self):
        table = getattr(self.ui, 'tbl_economy_ledger', None)
        if not table: return
        
        table.setRowCount(0)
        row = 0
        for steam_id, data in self.economy_data.items():
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(data.get("name", "Unknown")))
            table.setItem(row, 1, QTableWidgetItem(str(data.get("balance", 0))))
            table.setItem(row, 2, QTableWidgetItem(steam_id))
            row += 1

    def transaction_credit(self):
        # Placeholder for credit logic
        self.main_window.log_system_event("ECONOMY: Credit Transaction Initiated.")