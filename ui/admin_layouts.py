# ==============================================================================
# ZERO HOUR UI: ADMIN LAYOUTS - v23.2
# ==============================================================================
# ROLE: The "Skeleton" of the Application. Builds the Global Header, 
#       Navigation Bar, Tactical Toolbar, and the Central Content Stack.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 22 UPDATE (VISUAL RESTORATION):
# FIX: Integrated 'NexusStyler' to restore the "Zero Hour Dark" industrial theme.
# FIX: Wired 'Tactical Navigation' buttons with correct ObjectNames for CSS styling.
# FIX: Switched Tab instantiation to use 'TabBuilder.build(main_window)' pattern
#      to match the Phase 20 architecture.
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
    QGridLayout
)

# region [IMPORTS_THEME]
from ui.nexus_styler import NexusStyler
# endregion

# region [IMPORTS_TABS]
# CORRECTED: Importing the 'Builder' classes, not the raw widgets
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
        # We inject the Industrial CSS immediately
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
        self._build_content_stack(main_window) # Pass main_window for Builders
        self._build_footer()

        # 4. FINALIZE
        main_window.setCentralWidget(self.central_widget)
        
        # Connect navigation buttons to the stack (Logic wiring)
        self._connect_nav_buttons()

        # Set default page
        self.content_stack.setCurrentIndex(0)

    # region [SECTION_1_HEADER]
    def _build_header_frame(self):
        """
        Constructs the top branding bar and Server Status indicator.
        """
        self.header_frame = QFrame(self.central_widget)
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setMinimumHeight(60)
        self.header_frame.setMaximumHeight(60)
        self.header_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.header_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(15, 0, 15, 0)
        self.header_layout.setSpacing(10)

        # Logo / Title
        self.lbl_app_title = QLabel(self.header_frame)
        self.lbl_app_title.setObjectName("lbl_app_title")
        self.lbl_app_title.setText("ZERO HOUR | NEXUS COMMAND v21.2")
        self.lbl_app_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_app_title.setStyleSheet("color: #FFFFFF; letter-spacing: 1px;")

        # Active Profile Display
        self.lbl_active_profile = QLabel(self.header_frame)
        self.lbl_active_profile.setObjectName("lbl_active_profile")
        self.lbl_active_profile.setText("ACTIVE PROFILE: NOT SELECTED")
        self.lbl_active_profile.setStyleSheet("color: #00A8E8; font-weight: bold;")

        # Spacer
        self.header_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Add to Layout
        self.header_layout.addWidget(self.lbl_app_title)
        self.header_layout.addSpacerItem(self.header_spacer)
        self.header_layout.addWidget(self.lbl_active_profile)
        
        # Add Header to Main Layout
        self.main_layout.addWidget(self.header_frame)
    # endregion

    # region [SECTION_2_TACTICAL_TOOLBAR]
    def _build_tactical_toolbar(self):
        """
        Constructs the row of 'Quick Action' buttons and Server Controls (Start/Stop).
        """
        self.tactical_frame = QFrame(self.central_widget)
        self.tactical_frame.setObjectName("tactical_frame")
        self.tactical_frame.setMinimumHeight(50)
        self.tactical_frame.setMaximumHeight(50)
        self.tactical_frame.setStyleSheet("background-color: #1A1A1A; border-bottom: 1px solid #333;")

        self.tactical_layout = QHBoxLayout(self.tactical_frame)
        self.tactical_layout.setContentsMargins(10, 5, 10, 5)
        self.tactical_layout.setSpacing(10)

        # -- LEFT SIDE: File Operations --
        self.btn_open_root = QPushButton("ROOT DIR")
        self.btn_open_root.setObjectName("tactical_btn") # CSS Hook
        self.btn_open_root.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_root.setToolTip("Open Server Root Folder")

        self.btn_open_logs = QPushButton("LOGS")
        self.btn_open_logs.setObjectName("tactical_btn")
        self.btn_open_logs.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_save_data = QPushButton("SAVES")
        self.btn_save_data.setObjectName("tactical_btn")
        self.btn_save_data.setCursor(Qt.CursorShape.PointingHandCursor)

        # Spacer between File Ops and Server Controls
        self.tactical_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # -- RIGHT SIDE: Reactor Controls (Start/Stop) --
        self.btn_start_server = QPushButton("START SERVER")
        self.btn_start_server.setObjectName("btn_start_server") 
        # Note: NexusStyler handles #btn_start_server with Green styling
        self.btn_start_server.setMinimumWidth(120)
        self.btn_start_server.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_stop_server = QPushButton("STOP (KILL)")
        self.btn_stop_server.setObjectName("btn_stop_server")
        # Note: NexusStyler handles #btn_stop_server with Red styling
        self.btn_stop_server.setMinimumWidth(120)
        self.btn_stop_server.setEnabled(False) # Disabled by default
        self.btn_stop_server.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_shutdown_dialog = QPushButton("OPTIONS")
        self.btn_shutdown_dialog.setObjectName("tactical_btn")
        self.btn_shutdown_dialog.setToolTip("Graceful Shutdown / Restart Options")

        # Assemble
        self.tactical_layout.addWidget(self.btn_open_root)
        self.tactical_layout.addWidget(self.btn_open_logs)
        self.tactical_layout.addWidget(self.btn_save_data)
        self.tactical_layout.addSpacerItem(self.tactical_spacer)
        self.tactical_layout.addWidget(self.btn_start_server)
        self.tactical_layout.addWidget(self.btn_shutdown_dialog)
        self.tactical_layout.addWidget(self.btn_stop_server)

        # Add to Main Layout
        self.main_layout.addWidget(self.tactical_frame)
    # endregion

    # region [SECTION_3_NAVIGATION_BAR]
    def _build_navigation_bar(self):
        """
        Constructs the main horizontal tab navigation.
        """
        self.nav_frame = QFrame(self.central_widget)
        self.nav_frame.setObjectName("nav_frame")
        self.nav_frame.setMinimumHeight(45)
        self.nav_frame.setMaximumHeight(45)

        self.nav_layout = QHBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(2)

        # Create Buttons
        # We give them objectName "nav_btn" for generic styling, 
        # and specific IDs for the router map.
        
        self.btn_nav_dashboard = QPushButton("DASHBOARD")
        self.btn_nav_dashboard.setObjectName("nav_btn")
        self.btn_nav_dashboard.setCheckable(True)
        self.btn_nav_dashboard.setChecked(True) # Default active

        self.btn_nav_config = QPushButton("CONFIGURATION")
        self.btn_nav_config.setObjectName("nav_btn")
        self.btn_nav_config.setCheckable(True)

        self.btn_nav_forge = QPushButton("THE FORGE")
        self.btn_nav_forge.setObjectName("nav_btn")
        self.btn_nav_forge.setCheckable(True)

        self.btn_nav_economy = QPushButton("ECONOMY")
        self.btn_nav_economy.setObjectName("nav_btn")
        self.btn_nav_economy.setCheckable(True)

        self.btn_nav_automation = QPushButton("AUTOMATION")
        self.btn_nav_automation.setObjectName("nav_btn")
        self.btn_nav_automation.setCheckable(True)

        self.btn_nav_faq = QPushButton("KNOWLEDGE BASE")
        self.btn_nav_faq.setObjectName("nav_btn")
        self.btn_nav_faq.setCheckable(True)

        # Add to Layout
        self.nav_layout.addWidget(self.btn_nav_dashboard)
        self.nav_layout.addWidget(self.btn_nav_config)
        self.nav_layout.addWidget(self.btn_nav_forge)
        self.nav_layout.addWidget(self.btn_nav_economy)
        self.nav_layout.addWidget(self.btn_nav_automation)
        self.nav_layout.addWidget(self.btn_nav_faq)

        # Add to Main Layout
        self.main_layout.addWidget(self.nav_frame)
    # endregion

    # region [SECTION_4_CONTENT_STACK]
    def _build_content_stack(self, main_window):
        """
        Constructs the QStackedWidget and instantiates the individual Tab Classes.
        Uses the BUILDER PATTERN (TabBuilder.build(main_window)).
        """
        self.content_stack = QStackedWidget(self.central_widget)
        self.content_stack.setObjectName("content_stack")

        # Instantiate Tabs via Builders
        
        # Index 0: Dashboard
        self.tab_dashboard = DashboardTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_dashboard)

        # Index 1: Configuration
        self.tab_config = ConfigurationTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_config)

        # Index 2: The Forge (Mod Manager)
        self.tab_forge = ForgeTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_forge)

        # Index 3: Economy
        self.tab_economy = EconomyTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_economy)

        # Index 4: Automation
        self.tab_automation = AutomationTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_automation)

        # Index 5: FAQ / Help
        self.tab_faq = FaqTabBuilder.build(main_window)
        self.content_stack.addWidget(self.tab_faq)

        # Add Stack to Main Layout
        self.main_layout.addWidget(self.content_stack)
    # endregion

    # region [SECTION_5_FOOTER]
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

        self.lbl_system_status = QLabel("SYSTEM READY")
        self.lbl_system_status.setStyleSheet("color: #666; font-size: 10px;")

        self.footer_layout.addWidget(self.lbl_system_status)
        self.main_layout.addWidget(self.footer_frame)
    # endregion

    # region [LOGIC_WIRING]
    def _connect_nav_buttons(self):
        """
        Internal logic to handle visual tab switching state (Exclusive checks).
        """
        self.nav_group = [
            self.btn_nav_dashboard,
            self.btn_nav_config,
            self.btn_nav_forge,
            self.btn_nav_economy,
            self.btn_nav_automation,
            self.btn_nav_faq
        ]

        # Note: Actual page switching is handled by 'main.py' Routers.
        # This function just ensures only one button looks "Pressed" at a time.
        for btn in self.nav_group:
            btn.clicked.connect(self._update_nav_state)

    def _update_nav_state(self):
        sender = self.central_widget.sender()
        if not sender: return

        for btn in self.nav_group:
            if btn == sender:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
    # endregion