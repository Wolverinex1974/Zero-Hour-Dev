# =========================================================
# ZERO HOUR: LAYOUT ENGINE (TOP-NAV RESTORATION) - v21.2
# =========================================================
# ROLE: UI Construction & Crash Reporting
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 UI RESTORATION:
# FEATURE: Switched from Sidebar to Top-Horizontal Layout.
# FEATURE: Added Global Reactor Controls (Redundant Start/Stop).
# FEATURE: Restored Profile & Keep Alive Headers.
# FIX: 100% Bracket-Free payload.
# =========================================================

import sys
import os
import datetime
import traceback
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QStackedWidget, QFrame, QListWidget, QListWidgetItem, 
    QSizePolicy, QScrollArea, QAbstractItemView, QComboBox,
    QCheckBox, QButtonGroup
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor

# TAB BUILDERS
from ui.tabs.dashboard_tab import DashboardTabBuilder
from ui.tabs.configuration_tab import ConfigurationTabBuilder
from ui.tabs.forge_tab import ForgeTabBuilder
from ui.tabs.economy_tab import EconomyTabBuilder
from ui.tabs.automation_tab import AutomationTabBuilder

class ZeroHourLayout:
    def __init__(self):
        # --- CONTAINER SKELETON ---
        self.main_window = None
        self.central_widget = None
        self.main_layout = None
        self.content_stack = None
        self.nav_group = None # Button Group for Tabs
        
        # --- SHARED WIDGET REGISTRY ---
        
        # Header: Profile & Identity
        self.combo_profile_selector = None
        self.btn_add_profile = None
        self.btn_delete_profile = None
        self.chk_keep_alive = None # Restored
        
        # Header: Tactical & Global Reactor
        self.btn_open_root = None
        self.btn_open_logs = None
        self.btn_open_saves = None
        self.btn_open_mods = None
        
        # GLOBAL CONTROLS (Always Visible)
        self.btn_start_server_global = None
        self.btn_shutdown_dialog_global = None
        self.btn_stop_server_global = None
        
        # Nav Buttons
        self.btn_nav_dashboard = None
        self.btn_nav_config = None
        self.btn_nav_forge = None
        self.btn_nav_economy = None
        self.btn_nav_automation = None
        self.btn_nav_faq = None
        
        # Dashboard (Local Widgets)
        self.lbl_instance_info = None
        self.txt_system_log = None
        self.btn_start_server = None # Local Redundancy
        self.btn_stop_server = None  # Local Redundancy
        self.lbl_watchdog_status = None
        self.txt_reactor_stream = None
        self.lbl_status = None # Footer Status
        
        # Config
        self.txt_prof_name = None
        self.txt_server_port = None
        self.txt_target_repo = None
        self.btn_save_identity = None
        self.btn_save_srv_settings = None
        
        # Forge
        self.table_mods = None
        self.progressBar_forge = None
        self.btn_commit_deploy = None
        self.btn_install_mod = None
        self.btn_scan_duplicates = None
        self.btn_rebalance_mods = None
        self.btn_run_audit = None
        self.btn_export_audit = None
        self.tree_conflicts = None
        self.txt_atlas_desc = None
        self.combo_atlas_status = None
        
        # Economy
        self.table_players = None
        self.table_store_items = None
        self.btn_refresh_ledger = None
        self.btn_store_add = None
        self.btn_store_remove = None
        self.btn_store_sync = None
        
        # Automation
        self.btn_backup_now = None
        self.chk_enable_watchdog = None
        self.chk_announce_restart = None
        self.txt_webhook_url = None

        # Tab References
        self.tab_dashboard = None
        self.tab_config = None
        self.tab_forge = None
        self.tab_economy = None
        self.tab_automation = None

    def setup_ui(self, main_window):
        """Constructs the Top-Nav Layout matching the Screenshots."""
        self._log_to_file("--- STARTING UI CONSTRUCTION (TOP-NAV) ---")
        self.main_window = main_window
        
        if hasattr(main_window, "resize"):
            main_window.resize(1300, 900)
            
        main_window.setWindowTitle("Zero Hour Nexus Command v20.8 (TEST ENV)")
        
        self.central_widget = QWidget()
        main_window.setCentralWidget(self.central_widget)
        
        # Main Vertical Layout (Header -> Nav -> Content -> Footer)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Build Header Rows
        self._build_top_header()
        self._build_tactical_row()
        self._build_nav_bar()
        
        # 2. Build Content Stack
        self._build_content_stack()
        
        # 3. Populate Tabs
        self._populate_tabs(main_window)
        
        # 4. Build Footer
        self._build_footer()
        
        # 5. Apply Styles
        self._apply_global_styles(main_window)
        self._log_to_file("--- UI CONSTRUCTION COMPLETE ---")

    def _build_top_header(self):
        """Row 1: Profile Selector, Keep Alive, Delete"""
        header_frame = QFrame()
        header_frame.setObjectName("TopHeader")
        header_frame.setFixedHeight(60)
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Profile Section
        layout.addWidget(QLabel("ACTIVE SERVER PROFILE:"))
        
        self.combo_profile_selector = QComboBox()
        self.combo_profile_selector.setObjectName("combo_profile_selector")
        self.combo_profile_selector.setMinimumWidth(250)
        layout.addWidget(self.combo_profile_selector)
        
        self.btn_add_profile = QPushButton("+ ADD NEW SERVER")
        self.btn_add_profile.setObjectName("btn_add_profile")
        layout.addWidget(self.btn_add_profile)
        
        layout.addStretch()
        
        # Keep Alive
        self.chk_keep_alive = QCheckBox("KEEP ALIVE (AUTO-RESTART)")
        self.chk_keep_alive.setObjectName("chk_keep_alive")
        self.chk_keep_alive.setChecked(True)
        # Note: Logic usually binds this to the Watchdog
        layout.addWidget(self.chk_keep_alive)
        
        layout.addStretch()
        
        # Delete
        self.btn_delete_profile = QPushButton("DELETE PROFILE")
        self.btn_delete_profile.setObjectName("btn_delete_profile")
        self.btn_delete_profile.setStyleSheet("background-color: #c0392b; color: white;")
        layout.addWidget(self.btn_delete_profile)
        
        self.main_layout.addWidget(header_frame)

    def _build_tactical_row(self):
        """Row 2: Tactical Nav Buttons + GLOBAL Reactor Controls"""
        tactical_frame = QFrame()
        tactical_frame.setObjectName("TacticalRow")
        tactical_frame.setFixedHeight(60)
        layout = QHBoxLayout(tactical_frame)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)
        
        # Label
        lbl_tac = QLabel("TACTICAL NAV:")
        lbl_tac.setStyleSheet("color: #8e44ad; font-weight: bold;")
        layout.addWidget(lbl_tac)
        
        # Nav Buttons
        self.btn_open_root = QPushButton("ROOT DIR")
        self.btn_open_root.setObjectName("btn_open_root")
        self.btn_open_root.setStyleSheet("background-color: #444; border: 1px solid #555;")
        
        self.btn_open_logs = QPushButton("SERVER LOGS")
        self.btn_open_logs.setObjectName("btn_open_logs")
        self.btn_open_logs.setStyleSheet("background-color: #444; border: 1px solid #555;")
        
        self.btn_open_saves = QPushButton("SAVE DATA")
        self.btn_open_saves.setObjectName("btn_open_saves")
        self.btn_open_saves.setStyleSheet("background-color: #444; border: 1px solid #555;")
        
        self.btn_open_mods = QPushButton("MODS FOLDER")
        self.btn_open_mods.setObjectName("btn_open_mods")
        self.btn_open_mods.setStyleSheet("background-color: #444; border: 1px solid #555;")
        
        layout.addWidget(self.btn_open_root)
        layout.addWidget(self.btn_open_logs)
        layout.addWidget(self.btn_open_saves)
        layout.addWidget(self.btn_open_mods)
        
        layout.addStretch()
        
        # GLOBAL REACTOR CONTROLS (Redundant)
        self.btn_start_server_global = QPushButton("START SERVER")
        self.btn_start_server_global.setObjectName("btn_start_server_global")
        self.btn_start_server_global.setStyleSheet("background-color: #2ecc71; color: black; font-weight: bold; padding: 5px 15px;")
        
        self.btn_shutdown_dialog_global = QPushButton("SHUTDOWN / RESTART")
        self.btn_shutdown_dialog_global.setObjectName("btn_shutdown_dialog_global")
        self.btn_shutdown_dialog_global.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; padding: 5px 15px;")
        
        self.btn_stop_server_global = QPushButton("STOP (IMMEDIATE)")
        self.btn_stop_server_global.setObjectName("btn_stop_server_global")
        self.btn_stop_server_global.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 5px 15px;")
        
        layout.addWidget(self.btn_start_server_global)
        layout.addWidget(self.btn_shutdown_dialog_global)
        layout.addWidget(self.btn_stop_server_global)
        
        self.main_layout.addWidget(tactical_frame)

    def _build_nav_bar(self):
        """Row 3: The Tab Buttons"""
        nav_frame = QFrame()
        nav_frame.setObjectName("NavBar")
        nav_frame.setFixedHeight(50)
        layout = QHBoxLayout(nav_frame)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(1) # Tight spacing like tabs
        
        self.nav_group = QButtonGroup(self.main_window)
        self.nav_group.setExclusive(True)
        
        # Helper to create styled tab buttons
        def create_nav_btn(text, id_num):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            btn.setStyleSheet("""
                QPushButton { background-color: #2d2d30; border: none; color: #aaa; font-weight: bold; border-bottom: 2px solid transparent; }
                QPushButton:checked { background-color: #3e3e42; color: #fff; border-bottom: 2px solid #007acc; }
                QPushButton:hover { background-color: #3e3e42; }
            """)
            self.nav_group.addButton(btn, id_num)
            layout.addWidget(btn)
            return btn
            
        self.btn_nav_dashboard = create_nav_btn("DASHBOARD", 0)
        self.btn_nav_dashboard.setChecked(True)
        
        self.btn_nav_config = create_nav_btn("CONFIGURATION", 1)
        self.btn_nav_forge = create_nav_btn("THE FORGE", 2)
        self.btn_nav_economy = create_nav_btn("ECONOMY LEDGER", 3)
        self.btn_nav_automation = create_nav_btn("AUTOMATION EVENTS", 4)
        self.btn_nav_faq = create_nav_btn("KNOWLEDGE BASE", 5)
        
        layout.addStretch()
        
        # Connect Group to Stack
        self.nav_group.idClicked.connect(self._switch_tab)
        
        self.main_layout.addWidget(nav_frame)

    def _switch_tab(self, id_num):
        if self.content_stack:
            self.content_stack.setCurrentIndex(id_num)

    def _build_content_stack(self):
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

    def _populate_tabs(self, main_window):
        # DASHBOARD
        try:
            self.tab_dashboard = DashboardTabBuilder.build(main_window)
            self.content_stack.addWidget(self.tab_dashboard)
        except Exception as e:
            self._log_crash_to_file("DASHBOARD", e)
            self._add_fallback_tab("Dashboard Error")
            
        # CONFIGURATION
        try:
            self.tab_config = ConfigurationTabBuilder.build(main_window)
            self.content_stack.addWidget(self.tab_config)
        except Exception as e:
            self._log_crash_to_file("CONFIGURATION", e)
            self._add_fallback_tab("Configuration Error")
            
        # FORGE
        try:
            self.tab_forge = ForgeTabBuilder.build(main_window)
            self.content_stack.addWidget(self.tab_forge)
        except Exception as e:
            self._log_crash_to_file("FORGE", e)
            self._add_fallback_tab("Forge Error")
            
        # ECONOMY
        try:
            self.tab_economy = EconomyTabBuilder.build(main_window)
            self.content_stack.addWidget(self.tab_economy)
        except Exception as e:
            self._log_crash_to_file("ECONOMY", e)
            self._add_fallback_tab("Economy Error")
            
        # AUTOMATION
        try:
            self.tab_automation = AutomationTabBuilder.build(main_window)
            self.content_stack.addWidget(self.tab_automation)
        except Exception as e:
            self._log_crash_to_file("AUTOMATION", e)
            self._add_fallback_tab("Automation Error")
            
        # FAQ (Placeholder for now)
        try:
            tab_faq = QWidget()
            layout_faq = QVBoxLayout(tab_faq)
            lbl_faq = QLabel("Knowledgebase Under Construction")
            lbl_faq.setAlignment(Qt.AlignCenter)
            layout_faq.addWidget(lbl_faq)
            self.content_stack.addWidget(tab_faq)
        except Exception as e:
            self._log_crash_to_file("FAQ", e)
            self._add_fallback_tab("FAQ Error")

    def _build_footer(self):
        footer = QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #222; border-top: 1px solid #333;")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_status = QLabel("Paradoxal Logic Operational")
        self.lbl_status.setObjectName("lbl_status")
        self.lbl_status.setStyleSheet("color: #777; font-size: 11px;")
        
        layout.addWidget(self.lbl_status)
        self.main_layout.addWidget(footer)

    def _add_fallback_tab(self, name):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(f"MODULE FAILED: {name}")
        lbl.setStyleSheet("color: red; font-weight: bold;")
        l.addWidget(lbl)
        self.content_stack.addWidget(w)

    def _log_to_file(self, message):
        try:
            with open("logs/startup_crash_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now()} {message}\n")
        except: pass

    def _log_crash_to_file(self, name, err):
        try:
            with open("logs/startup_crash_log.txt", "a", encoding="utf-8") as f:
                f.write(f"CRASH {name}: {str(err)}\n{traceback.format_exc()}\n")
        except: pass

    def _apply_global_styles(self, main_window):
        main_window.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #ddd; }
            QComboBox { background-color: #333; color: #eee; border: 1px solid #444; padding: 5px; }
            QLineEdit { background-color: #333; color: #eee; border: 1px solid #444; padding: 5px; }
            QPushButton { border-radius: 3px; padding: 5px; }
        """)