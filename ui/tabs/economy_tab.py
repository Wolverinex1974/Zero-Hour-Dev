# =========================================================
# ZERO HOUR UI: ECONOMY TAB - v21.2
# =========================================================
# ROLE: Manages Server Currency (Z-Bucks), Shops, and
#       Player Statistics (The Ledger).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 FIX:
# FIX: Attaches widgets to (main_ui.ui) instead of (main_ui).
#      This resolves the AttributeError in store_manager.py.
# FIX: 100% Bracket-Free payload.
# =========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QAbstractItemView,
    QSplitter,
    QLineEdit,
    QFormLayout
)
from PySide6.QtCore import Qt

class EconomyTabBuilder:
    """
    Builds the Economy & Ledger Tab.
    Displays player wealth (Ledger) AND the Server Shop (Store).
    """
    @staticmethod
    def build(main_ui):
        # FIX: Removed .centralwidget dependency
        tab = QWidget()
        
        # CRITICAL BRIDGE:
        # Legacy Logic (StoreManager) expects widgets to be on 'main_ui.ui' (ZeroHourLayout),
        # not 'main_ui' (ZeroHourManager).
        ui = main_ui.ui
        
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ---------------------------------------------------------
        # TOP CONTROLS (Global Economy Actions)
        # ---------------------------------------------------------
        grp_controls = QGroupBox("Economy & Trade Federation")
        grp_controls.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #f1c40f; }")
        
        layout_controls = QHBoxLayout(grp_controls)

        ui.btn_refresh_ledger = QPushButton("REFRESH LEDGER")
        ui.btn_refresh_ledger.setObjectName("btn_refresh_ledger")
        ui.btn_refresh_ledger.setMinimumHeight(35)
        ui.btn_refresh_ledger.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

        ui.btn_export_wealth = QPushButton("EXPORT RICH LIST (.CSV)")
        ui.btn_export_wealth.setObjectName("btn_export_wealth")
        ui.btn_export_wealth.setMinimumHeight(35)
        ui.btn_export_wealth.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")

        layout_controls.addWidget(ui.btn_refresh_ledger)
        layout_controls.addWidget(ui.btn_export_wealth)

        main_layout.addWidget(grp_controls)

        # ---------------------------------------------------------
        # SPLIT VIEW: LEDGER (Left) vs STORE (Right)
        # ---------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal)

        # === LEFT PANE: PLAYER LEDGER ===
        ledger_widget = QWidget()
        ledger_layout = QVBoxLayout(ledger_widget)
        ledger_layout.setContentsMargins(0, 0, 0, 0)

        lbl_ledger = QLabel("Live Player Database (Active Profile)")
        lbl_ledger.setStyleSheet("font-weight: bold; color: #ccc;")
        ledger_layout.addWidget(lbl_ledger)

        ui.table_players = QTableWidget()
        ui.table_players.setObjectName("table_players")
        
        # Columns: Name, ID, Balance, Level, Kills, Deaths, Last Seen
        ledger_cols = list((
            "Player Name", 
            "Platform ID", 
            "Balance (ZB)", 
            "Level", 
            "Kills", 
            "Deaths", 
            "Last Seen"
        ))
        
        ui.table_players.setColumnCount(len(ledger_cols))
        ui.table_players.setHorizontalHeaderLabels(ledger_cols)
        ui.table_players.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ui.table_players.setAlternatingRowColors(True)
        ui.table_players.setSelectionBehavior(QAbstractItemView.SelectRows)
        ui.table_players.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ui.table_players.setStyleSheet("QTableWidget { background-color: #252526; alternate-background-color: #2d2d30; color: #ddd; gridline-color: #444; } QHeaderView::section { background-color: #333; color: white; padding: 5px; border: 1px solid #444; }")

        ledger_layout.addWidget(ui.table_players)
        splitter.addWidget(ledger_widget)

        # === RIGHT PANE: SOVEREIGN STOREFRONT ===
        store_widget = QWidget()
        store_layout = QVBoxLayout(store_widget)
        store_layout.setContentsMargins(0, 0, 0, 0)

        lbl_store = QLabel("Sovereign Storefront (Shop Config)")
        lbl_store.setStyleSheet("font-weight: bold; color: #e67e22;")
        store_layout.addWidget(lbl_store)

        # Store Table
        ui.table_store_items = QTableWidget()
        ui.table_store_items.setObjectName("table_store_items")
        
        store_cols = list(("Item Name", "Price (ZB)", "Category"))
        ui.table_store_items.setColumnCount(len(store_cols))
        ui.table_store_items.setHorizontalHeaderLabels(store_cols)
        ui.table_store_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ui.table_store_items.setAlternatingRowColors(True)
        ui.table_store_items.setSelectionBehavior(QAbstractItemView.SelectRows)
        ui.table_store_items.setStyleSheet("QTableWidget { background-color: #252526; alternate-background-color: #2d2d30; color: #ddd; gridline-color: #444; }")
        
        store_layout.addWidget(ui.table_store_items)

        # Store Controls (Add/Remove)
        grp_store_ops = QGroupBox("Manage Inventory")
        layout_ops = QFormLayout(grp_store_ops)
        
        ui.txt_store_item_name = QLineEdit()
        ui.txt_store_item_name.setPlaceholderText("e.g. gunPistol")
        
        ui.txt_store_price = QLineEdit()
        ui.txt_store_price.setPlaceholderText("100")
        
        ui.txt_store_category = QLineEdit()
        ui.txt_store_category.setPlaceholderText("Weapons")
        
        layout_ops.addRow("Item Name:", ui.txt_store_item_name)
        layout_ops.addRow("Price:", ui.txt_store_price)
        layout_ops.addRow("Category:", ui.txt_store_category)
        
        h_store_btns = QHBoxLayout()
        ui.btn_store_add = QPushButton("ADD ITEM")
        ui.btn_store_add.setObjectName("btn_store_add")
        ui.btn_store_add.setStyleSheet("background-color: #27ae60; color: white;")
        
        ui.btn_store_remove = QPushButton("REMOVE SELECTED")
        ui.btn_store_remove.setObjectName("btn_store_remove")
        ui.btn_store_remove.setStyleSheet("background-color: #c0392b; color: white;")
        
        h_store_btns.addWidget(ui.btn_store_add)
        h_store_btns.addWidget(ui.btn_store_remove)
        layout_ops.addRow("", h_store_btns)
        
        store_layout.addWidget(grp_store_ops)
        
        # Sync Button
        ui.btn_store_sync = QPushButton("PUBLISH STORE TO CLOUD")
        ui.btn_store_sync.setObjectName("btn_store_sync")
        ui.btn_store_sync.setMinimumHeight(40)
        ui.btn_store_sync.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        
        store_layout.addWidget(ui.btn_store_sync)

        splitter.addWidget(store_widget)
        
        # Set Splitter Ratio (60% Ledger, 40% Store)
        splitter.setSizes(list((600, 400)))

        main_layout.addWidget(splitter)
        
        return tab