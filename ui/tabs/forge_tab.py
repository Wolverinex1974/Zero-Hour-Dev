# =========================================================
# ZERO HOUR UI: FORGE TAB - v23.2
# =========================================================
# ROLE: Mod Management, Cloud Sync, and XML Auditing Center
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# =========================================================
# PHASE 24 UPDATE (v16 RESTORATION):
# FIX: Forced dark mode on QTableWidget and QTreeWidget.
# FIX: Applied "Green Matrix" theme to the XML Auditor Tree.
# FIX: Tied Action Buttons to NexusStyler flat color ObjectNames.
# =========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QGroupBox,
    QSplitter,
    QLineEdit,
    QComboBox,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QTextEdit,
    QAbstractItemView
)
from PySide6.QtCore import Qt

class ForgeTabBuilder:
    """
    Builds the Forge (Mod Manager) Tab.
    Handles Mod Installation, GitHub Sync, and XML Conflict Auditing.
    """
    @staticmethod
    def build(main_ui):
        tab = QWidget()
        
        # CRITICAL BRIDGE:
        # Logic Engines (BootSequence, ModController) expect widgets 
        # to be on 'main_ui.ui' (ZeroHourLayout / QMainWindow).
        ui = main_ui.ui
        
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ---------------------------------------------------------
        # TOP BAR: PIPELINE STATUS & SYNC
        # ---------------------------------------------------------
        top_bar = QGroupBox("Cloud Pipeline & Synchronization")
        top_bar.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; color: #888888; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        top_layout = QHBoxLayout(top_bar)

        ui.progressBar_forge = QProgressBar()
        ui.progressBar_forge.setRange(0, 100)
        ui.progressBar_forge.setValue(0)
        ui.progressBar_forge.setTextVisible(True)
        ui.progressBar_forge.setFormat("%p% - Pipeline Idle")
        ui.progressBar_forge.setStyleSheet("""
            QProgressBar { 
                background-color: #000000; 
                color: #ffffff; 
                border: 1px solid #444; 
                border-radius: 5px; 
                text-align: center; 
            } 
            QProgressBar::chunk { 
                background-color: #9b59b6; 
                width: 20px; 
            }
        """)

        ui.btn_commit_deploy = QPushButton("SYNC SERVER TO CLOUD")
        # Tied directly to the v16 Purple CSS class
        ui.btn_commit_deploy.setObjectName("btn_publish_purple")
        ui.btn_commit_deploy.setMinimumHeight(40)
        ui.btn_commit_deploy.setMinimumWidth(250)

        top_layout.addWidget(ui.progressBar_forge)
        top_layout.addWidget(ui.btn_commit_deploy)

        main_layout.addWidget(top_bar)

        # ---------------------------------------------------------
        # MAIN CONTENT: SPLITTER (MOD LIST | ACTIONS & AUDIT)
        # ---------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #333333; }")

        # --- LEFT PANE: MOD LIST (TABLE) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl_mods = QLabel("Active Mod Library")
        lbl_mods.setStyleSheet("font-weight: bold; color: #e0e0e0;")
        left_layout.addWidget(lbl_mods)

        ui.table_mods = QTableWidget()
        ui.table_mods.setObjectName("table_mods")
        
        # CONTROLLER REQUIRES 5 COLUMNS:
        # 0: Name, 1: Folder, 2: Tier (Widget), 3: Version, 4: Actions (Widget)
        mod_columns = list(("Name", "Folder", "Tier", "Version", "Actions"))
        ui.table_mods.setColumnCount(len(mod_columns))
        ui.table_mods.setHorizontalHeaderLabels(mod_columns)
        
        # Resize Modes
        header = ui.table_mods.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)       
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) 
        
        ui.table_mods.setSelectionBehavior(QAbstractItemView.SelectRows)
        ui.table_mods.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ui.table_mods.setDragDropMode(QAbstractItemView.InternalMove)
        
        # Forced Dark Theme to override Windows White
        ui.table_mods.setStyleSheet("""
            QTableWidget { 
                background-color: #000000; 
                color: #e0e0e0; 
                border: 1px solid #333333; 
                gridline-color: #2a2a2a; 
            }
            QHeaderView::section { 
                background-color: #1e1e1e; 
                color: #888888; 
                padding: 5px; 
                border: 1px solid #333333; 
                font-weight: bold;
            }
        """)
        
        left_layout.addWidget(ui.table_mods)

        # Mod Movement Controls
        h_move = QHBoxLayout()
        ui.btn_mod_up = QPushButton("▲ MOVE UP")
        ui.btn_mod_down = QPushButton("▼ MOVE DOWN")
        h_move.addWidget(ui.btn_mod_up)
        h_move.addWidget(ui.btn_mod_down)
        left_layout.addLayout(h_move)

        splitter.addWidget(left_widget)

        # --- RIGHT PANE: TOOLS & AUDIT ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Tool: Installation & Sanitation
        grp_tools = QGroupBox("Mod Operations")
        grp_tools.setStyleSheet("QGroupBox { border: 1px solid #444444; color: #e0e0e0; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_tools = QVBoxLayout(grp_tools)
        
        ui.btn_install_mod = QPushButton("INSTALL MOD FROM .ZIP")
        ui.btn_install_mod.setObjectName("btn_install_blue")
        
        ui.btn_scan_duplicates = QPushButton("SCAN FOR ORPHANED CLOUD ZIPS")
        ui.btn_scan_duplicates.setObjectName("btn_scan_orange")
        
        ui.btn_rebalance_mods = QPushButton("SANITIZE & REBALANCE (10-Step Gap)")
        ui.btn_rebalance_mods.setStyleSheet("color: #f1c40f; border: 1px solid #f1c40f;")
        
        layout_tools.addWidget(ui.btn_install_mod)
        layout_tools.addWidget(ui.btn_scan_duplicates)
        layout_tools.addWidget(ui.btn_rebalance_mods)
        
        right_layout.addWidget(grp_tools)

        # Tool: XML Auditor (Phase 19)
        grp_audit = QGroupBox("XML Collision Auditor (Phase 19)")
        grp_audit.setStyleSheet("QGroupBox { border: 1px solid #d35400; font-weight: bold; margin-top: 10px; } QGroupBox::title { color: #e67e22; subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_audit = QVBoxLayout(grp_audit)

        h_audit_btns = QHBoxLayout()
        ui.btn_run_audit = QPushButton("RUN DEEP SCAN")
        ui.btn_run_audit.setObjectName("btn_scan_orange")
        
        ui.btn_export_audit = QPushButton("EXPORT REPORT")
        ui.btn_export_audit.setEnabled(False) 
        
        h_audit_btns.addWidget(ui.btn_run_audit)
        h_audit_btns.addWidget(ui.btn_export_audit)
        layout_audit.addLayout(h_audit_btns)

        ui.progressBar_audit = QProgressBar()
        ui.progressBar_audit.setValue(0)
        ui.progressBar_audit.setFixedHeight(10)
        ui.progressBar_audit.setTextVisible(False)
        ui.progressBar_audit.setStyleSheet("QProgressBar { border: 1px solid #444; background-color: #000000; } QProgressBar::chunk { background-color: #d35400; }")
        layout_audit.addWidget(ui.progressBar_audit)

        ui.lbl_audit_status = QLabel("Status: Idle")
        ui.lbl_audit_status.setStyleSheet("color: #e0e0e0;")
        ui.lbl_audit_status.setAlignment(Qt.AlignCenter)
        layout_audit.addWidget(ui.lbl_audit_status)

        # Tree Widget for Conflicts (Green Matrix Theme)
        ui.tree_conflicts = QTreeWidget()
        ui.tree_conflicts.setObjectName("tree_conflicts")
        ui.tree_conflicts.setHeaderLabels(list(("File / Conflict Name", "Involved Mods")))
        ui.tree_conflicts.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        ui.tree_conflicts.setStyleSheet("""
            QTreeWidget { 
                background-color: #000000; 
                color: #00ff00; 
                font-family: Consolas, monospace; 
                border: 1px solid #d35400; 
            }
            QHeaderView::section { 
                background-color: #1e1e1e; 
                color: #e67e22; 
                padding: 5px; 
                border: 1px solid #333333; 
            }
        """)
        
        layout_audit.addWidget(ui.tree_conflicts)

        right_layout.addWidget(grp_audit)
        
        # Tool: Atlas Registration
        grp_atlas = QGroupBox("Atlas Public Listing")
        grp_atlas.setStyleSheet("QGroupBox { border: 1px solid #2980b9; color: #2980b9; font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_atlas = QVBoxLayout(grp_atlas)
        
        ui.txt_atlas_desc = QLineEdit()
        ui.txt_atlas_desc.setPlaceholderText("Server Description for Public Listing...")
        ui.txt_atlas_desc.setStyleSheet("background-color: #000000; color: #00ff00; border: 1px solid #2980b9; padding: 5px;")
        
        ui.combo_atlas_status = QComboBox()
        ui.combo_atlas_status.addItems(list(("ONLINE", "MAINTENANCE", "PRIVATE")))
        ui.combo_atlas_status.setStyleSheet("background-color: #2980b9; color: white; border: none; padding: 5px;")
        
        layout_atlas.addWidget(ui.txt_atlas_desc)
        layout_atlas.addWidget(ui.combo_atlas_status)
        
        right_layout.addWidget(grp_atlas)

        splitter.addWidget(right_widget)
        
        # Set Splitter Ratio (40% List, 60% Tools)
        splitter.setSizes(list((400, 600)))
        
        main_layout.addWidget(splitter)
        
        return tab