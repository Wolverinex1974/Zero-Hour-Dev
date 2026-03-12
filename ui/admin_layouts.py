# ==============================================================================
# ZERO HOUR UI: ADMIN LAYOUTS - v23.2
# ==============================================================================
# ROLE: The "Skeleton" of the Application. Builds the Global Header, 
#       Navigation Bar, Tactical Toolbar, and the Central Content Stack.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE (v16 RESTORATION):
# FIX: Rebuilt Top Header to include Profile Dropdown and Keep Alive toggles.
# FIX: Updated Tactical Navigation with Folder Unicode and v16 CSS Hooks.
# ==============================================================================

import sys
import os
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPushButton, 
    QLabel, 
    QStackedWidget, 
    QFrame, 
    QSpacerItem, 
    QSizePolicy,
    QGridLayout,
    QComboBox,
    QCheckBox
)

# region[IMPORTS_THEME]
from ui.nexus_styler import NexusStyler
# endregion

# region[IMPORTS_TABS]
from ui.tabs.dashboard_tab import DashboardTabBuilder
from ui.tabs.configuration_tab import ConfigurationTabBuilder
from ui.tabs.forge_tab import ForgeTabBuilder
from ui.tabs.economy_tab import EconomyTabBuilder
from ui.tabs.automation_tab import AutomationTabBuilder
from ui.tabs.faq_tab import FaqTabBuilder
# endregion

class ZeroHourLayout(object):
    """
    The main layout engine. This class constructs the visual hierarchy
    of the main window.
    """

    def setup_ui(self, main_window):
        """
        Builds the entire UI structure and attaches it to the main_window.
        """
        if not main_window.objectName():
            main_window.setObjectName("MainWindow")
        
        main_window.resize(1280, 850)
        
        # 1. APPLY THEME (The Paint)
        industrial_style = NexusStyler.get_industrial_style()
        main_window.setStyleSheet(industrial_style)

        # 2. CENTRAL WIDGET
        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        
        # Main Vertical Layout (Top to Bottom)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 3. BUILD SECTIONS
        self._build_header_frame()
        self._build_tactical_toolbar()
        self._build_navigation_bar()
        self._build_content_stack(main_window) 
        self._build_footer()

        # 4. FINALIZE
        main_window.setCentralWidget(self.central_widget)
        
        # Connect navigation buttons to the stack
        self._connect_nav_buttons()

        # Set default page
        self.content_stack.setCurrentIndex(0)

    # region[SECTION_1_HEADER]
    def _build_header_frame(self):
        """
        Constructs the top branding bar and Server Status indicator (v16 Restored).
        """
        self.header_frame = QFrame(self.central_widget)
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setMinimumHeight(70)
        self.header_frame.setMaximumHeight(70)
        self.header_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.header_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(15, 5, 15, 5)
        self.header_layout.setSpacing(15)

        # Profile Label & Dropdown
        self.lbl_profile_tag = QLabel("ACTIVE SERVER PROFILE:")
        self.lbl_profile_tag.setStyleSheet("color: #E0E0E0; font-weight: bold; font-size: 11px;")
        
        self.combo_active_profile = QComboBox()
        self.combo_active_profile.setMinimumWidth(300)
        self.combo_active_profile.addItem("Paradoxal Gaming 7D2D Server TEST")
        
        self.btn_add_server = QPushButton("+ ADD NEW SERVER")
        
        # Keep Alive Checkbox Area
        self.keep_alive_layout = QVBoxLayout()
        self.keep_alive_layout.setSpacing(0)
        
        self.chk_keep_alive = QCheckBox("KEEP ALIVE (AUTO-RESTART)")
        self.chk_keep_alive.setStyleSheet("""
            QCheckBox { color: #2ecc71; font-weight: bold; font-size: 11px; }
            QCheckBox::indicator { width: 15px; height: 15px; }
        """)
        self.chk_keep_alive.setChecked(True)
        
        self.lbl_keep_alive_sub = QLabel("Auto-restarts server on crash. Disable for maintenance.")
        self.lbl_keep_alive_sub.setStyleSheet("color: #888888; font-size: 9px;")
        
        self.keep_alive_layout.addWidget(self.chk_keep_alive)
        self.keep_alive_layout.addWidget(self.lbl_keep_alive_sub)

        # Spacer
        self.header_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Delete Profile Button
        self.btn_delete_profile = QPushButton("DELETE PROFILE")
        self.btn_delete_profile.setObjectName("btn_action_delete")

        # Add to Layout
        self.header_layout.addWidget(self.lbl_profile_tag)
        self.header_layout.addWidget(self.combo_active_profile)
        self.header_layout.addWidget(self.btn_add_server)
        self.header_layout.addSpacing(30)
        self.header_layout.addLayout(self.keep_alive_layout)
        self.header_layout.addSpacerItem(self.header_spacer)
        self.header_layout.addWidget(self.btn_delete_profile)
        
        # Add Header to Main Layout
        self.main_layout.addWidget(self.header_frame)
    # endregion

    # region[SECTION_2_TACTICAL_TOOLBAR]
    def _build_tactical_toolbar(self):
        """
        Constructs the row of 'Quick Action' buttons and Server Controls (v16 Restored).
        """
        self.tactical_frame = QFrame(self.central_widget)
        self.tactical_frame.setObjectName("tactical_frame")
        self.tactical_frame.setMinimumHeight(50)
        self.tactical_frame.setMaximumHeight(50)
        self.tactical_frame.setStyleSheet("background-color: #252526; border-top: 1px solid #333333; border-bottom: 1px solid #111111;")

        self.tactical_layout = QHBoxLayout(self.tactical_frame)
        self.tactical_layout.setContentsMargins(15, 5, 15, 5)
        self.tactical_layout.setSpacing(10)
        
        self.lbl_tactical = QLabel("TACTICAL NAV:")
        self.lbl_tactical.setStyleSheet("color: #9b59b6; font-weight: bold; font-size: 11px;")

        # -- LEFT SIDE: File Operations (Folders) --
        self.btn_open_root = QPushButton("📁 ROOT DIR")
        self.btn_open_root.setObjectName("tactical_btn")
        self.btn_open_root.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_open_logs = QPushButton("📁 SERVER LOGS")
        self.btn_open_logs.setObjectName("tactical_btn")
        self.btn_open_logs.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_save_data = QPushButton("📁 SAVE DATA")
        self.btn_save_data.setObjectName("tactical_btn")
        self.btn_save_data.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_open_mods = QPushButton("📁 MODS FOLDER")
        self.btn_open_mods.setObjectName("tactical_btn")
        self.btn_open_mods.setCursor(Qt.CursorShape.PointingHandCursor)

        # Spacer
        self.tactical_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # -- RIGHT SIDE: Reactor Controls (Start/Stop) --
        self.btn_start_server = QPushButton("START SERVER")
        self.btn_start_server.setObjectName("btn_action_start") 
        self.btn_start_server.setMinimumWidth(120)
        self.btn_start_server.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_shutdown_dialog = QPushButton("SHUTDOWN / RESTART")
        self.btn_shutdown_dialog.setMinimumWidth(140)
        self.btn_shutdown_dialog.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_stop_server = QPushButton("STOP (IMMEDIATE)")
        self.btn_stop_server.setObjectName("btn_action_stop")
        self.btn_stop_server.setMinimumWidth(140)
        self.btn_stop_server.setEnabled(False) 
        self.btn_stop_server.setCursor(Qt.CursorShape.PointingHandCursor)

        # Assemble
        self.tactical_layout.addWidget(self.lbl_tactical)
        self.tactical_layout.addWidget(self.btn_open_root)
        self.tactical_layout.addWidget(self.btn_open_logs)
        self.tactical_layout.addWidget(self.btn_save_data)
        self.tactical_layout.addWidget(self.btn_open_mods)
        self.tactical_layout.addSpacerItem(self.tactical_spacer)
        self.tactical_layout.addWidget(self.btn_start_server)
        self.tactical_layout.addWidget(self.btn_shutdown_dialog)
        self.tactical_layout.addWidget(self.btn_stop_server)

        # Add to Main Layout
        self.main_layout.addWidget(self.tactical_frame)
    # endregion

    # region[SECTION_3_NAVIGATION_BAR]
    def _build_navigation_bar(self):
        """
        Constructs the main horizontal tab navigation.
        """
        self.nav_frame = QFrame(self.central_widget)
        self.nav_frame.setObjectName("nav_frame")
        self.nav_frame.setMinimumHeight(45)
        self.nav_frame.setMaximumHeight(45)
        self.nav_frame.setStyleSheet("background-color: #161616;")

        self.nav_layout = QHBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(15, 0, 15, 0)
        self.nav_layout.setSpacing(0)
        
        self.btn_nav_dashboard = QPushButton("DASHBOARD")
        self.btn_nav_dashboard.setObjectName("main_nav_button")
        self.btn_nav_dashboard.setCheckable(True)
        self.btn_nav_dashboard.setChecked(True) 

        self.btn_nav_config = QPushButton("CONFIGURATION")
        self.btn_nav_config.setObjectName("main_nav_button")
        self.btn_nav_config.setCheckable(True)

        self.btn_nav_forge = QPushButton("THE FORGE")
        self.btn_nav_forge.setObjectName("main_nav_button")
        self.btn_nav_forge.setCheckable(True)

        self.btn_nav_economy = QPushButton("ECONOMY LEDGER")
        self.btn_nav_economy.setObjectName("main_nav_button")
        self.btn_nav_economy.setCheckable(True)

        self.btn_nav_automation = QPushButton("AUTOMATION EVENTS")
        self.btn_nav_automation.setObjectName("main_nav_button")
        self.btn_nav_automation.setCheckable(True)

        self.btn_nav_faq = QPushButton("KNOWLEDGE BASE")
        self.btn_nav_faq.setObjectName("main_nav_button")
        self.btn_nav_faq.setCheckable(True)
        
        self.nav_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Add to Layout
        self.nav_layout.addWidget(self.btn_nav_dashboard)
        self.nav_layout.addWidget(self.btn_nav_config)
        self.nav_layout.addWidget(self.btn_nav_forge)
        self.nav_layout.addWidget(self.btn_nav_economy)
        self.nav_layout.addWidget(self.btn_nav_automation)
        self.nav_layout.addWidget(self.btn_nav_faq)
        self.nav_layout.addSpacerItem(self.nav_spacer)

        # Add to Main Layout
        self.main_layout.addWidget(self.nav_frame)
    # endregion

    # region[SECTION_4_CONTENT_STACK]
    def _build_content_stack(self, main_window):
        """
        Constructs the QStackedWidget and instantiates the individual Tab Classes.
        """
        self.content_stack = QStackedWidget(self.central_widget)
        self.content_stack.setObjectName("content_stack")

        # Instantiate Tabs via Builders
        self.tab_dashboard = DashboardTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_dashboard)

        self.tab_config = ConfigurationTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_config)

        self.tab_forge = ForgeTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_forge)

        self.tab_economy = EconomyTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_economy)

        self.tab_automation = AutomationTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_automation)

        self.tab_faq = FaqTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_faq)

        # Add Stack to Main Layout
        self.main_layout.addWidget(self.content_stack)
    # endregion

    # region[SECTION_5_FOOTER]
    def _build_footer(self):
        """
        Constructs the bottom status bar.
        """
        self.footer_frame = QFrame(self.central_widget)
        self.footer_frame.setObjectName("footer_frame")
        self.footer_frame.setMinimumHeight(30)
        self.footer_frame.setMaximumHeight(30)
        self.footer_frame.setStyleSheet("background-color: #0F0F0F; border-top: 1px solid #333;")

        self.footer_layout = QHBoxLayout(self.footer_frame)
        self.footer_layout.setContentsMargins(10, 0, 10, 0)

        self.lbl_system_status = QLabel("Paradoxal Logic Operational")
        self.lbl_system_status.setStyleSheet("color: #666; font-size: 10px; font-weight: bold;")

        self.footer_layout.addWidget(self.lbl_system_status)
        self.main_layout.addWidget(self.footer_frame)
    # endregion

    # region[LOGIC_WIRING]
    def _connect_nav_buttons(self):
        """
        Internal logic to handle visual tab switching AND content stack indexing.
        """
        self.nav_group = list((
            self.btn_nav_dashboard,
            self.btn_nav_config,
            self.btn_nav_forge,
            self.btn_nav_economy,
            self.btn_nav_automation,
            self.btn_nav_faq
        ))

        for index_number in range(len(self.nav_group)):
            button_reference = self.nav_group[index_number]
            button_reference.clicked.connect(
                lambda checked_state=False, idx=index_number: self._update_nav_state(idx)
            )

    def _update_nav_state(self, clicked_index):
        """
        Switches the QStackedWidget page AND ensures only the clicked button
        receives the Blue :checked CSS styling.
        """
        # 1. Switch the physical page
        self.content_stack.setCurrentIndex(clicked_index)
        
        # 2. Enforce the exclusive visual state
        for index_number in range(len(self.nav_group)):
            button_reference = self.nav_group[index_number]
            if index_number == clicked_index:
                button_reference.setChecked(True)
            else:
                button_reference.setChecked(False)
    # endregion