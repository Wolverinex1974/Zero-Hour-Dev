# ==============================================================================
# ZERO HOUR UI: DASHBOARD TAB - v23.0
# ==============================================================================
# ROLE: Combines System Info and Live Reactor Logs into a
#       single, unified Command Center view.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 22 UPDATE (DRIFT REPAIR):
# FIX: Removed duplicate 'Tactical Navigation' buttons (Root, Logs, etc.) 
#      to prevent overwriting the Global Header button references.
# FIX: Preserved Reactor Controls (Start/Stop) and Console Streams.
# ==============================================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QSplitter,
    QFrame
)
from PySide6.QtCore import Qt

class DashboardTabBuilder:
    """
    Builds the Dashboard Tab and binds its interactive widgets
    directly to the main UI instance (ZeroHourLayout) to preserve 
    logic compatibility.
    """
    @staticmethod
    def build(main_ui):
        """
        Constructs the Dashboard Widget.
        :param main_ui: Reference to the Main Window (holds the .ui namespace)
        """
        tab = QWidget()
        tab.setObjectName("tab_dashboard")
        
        # CRITICAL BRIDGE:
        # Connect to the Layout Object (ZeroHourLayout)
        # This allows us to inject widgets into 'self.ui' for the Routers.
        ui = main_ui.ui
        
        # Using a splitter allows the Admin to dynamically resize
        # the System Log vs Reactor Log width while the server is running.
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # -------------------------------------------------------------
        # LEFT PANE: SYSTEM INTELLIGENCE
        # -------------------------------------------------------------
        sys_widget = QWidget()
        v_system = QVBoxLayout(sys_widget)
        v_system.setContentsMargins(0, 0, 5, 0)
        
        # Instance Header
        ui.lbl_instance_info = QLabel("INSTANCE: UNCONFIGURED")
        ui.lbl_instance_info.setObjectName("lbl_instance_info")
        # Inline style for immediate visibility, can be overridden by NexusStyler
        ui.lbl_instance_info.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 14px; margin-bottom: 5px;")
        v_system.addWidget(ui.lbl_instance_info)
        
        # [REMOVED] Tactical Navigation Frame
        # The buttons (Root, Logs, Saves) were duplicates of the Global Header.
        # Removing them here restores functionality to the Global Header buttons.
        
        # System Log Label
        lbl_syslog = QLabel("SYSTEM EVENTS")
        lbl_syslog.setStyleSheet("font-weight: bold; color: #7f8c8d; margin-top: 5px;")
        v_system.addWidget(lbl_syslog)
        
        # System Log Console
        ui.txt_system_log = QTextEdit()
        ui.txt_system_log.setObjectName("txt_system_log")
        ui.txt_system_log.setReadOnly(True)
        ui.txt_system_log.setStyleSheet("background-color: #000; color: #2ecc71; font-family: Consolas; border: 1px solid #333;")
        v_system.addWidget(ui.txt_system_log)
        
        # -------------------------------------------------------------
        # RIGHT PANE: REACTOR CORE / SERVER LOGS
        # -------------------------------------------------------------
        reactor_widget = QWidget()
        v_reactor = QVBoxLayout(reactor_widget)
        v_reactor.setContentsMargins(5, 0, 0, 0)
        
        # Control Deck (Start/Stop/Status)
        h_reactor_ops = QHBoxLayout()
        
        # Note: These buttons share names with Global Header buttons.
        # Ideally, Routers should listen to both, or these should be renamed.
        # For now, we keep them to match the "Command Center" visual expectation.
        
        ui.btn_start_server = QPushButton("START SERVER")
        ui.btn_start_server.setObjectName("btn_start_server")
        ui.btn_start_server.setMinimumHeight(40)
        ui.btn_start_server.setCursor(Qt.CursorShape.PointingHandCursor)
        ui.btn_start_server.setStyleSheet("background-color: #2ecc71; color: black; font-weight: bold;")
        
        ui.btn_shutdown_dialog = QPushButton("SHUTDOWN / RESTART")
        ui.btn_shutdown_dialog.setObjectName("btn_shutdown_dialog")
        ui.btn_shutdown_dialog.setMinimumHeight(40)
        ui.btn_shutdown_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        ui.btn_shutdown_dialog.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        
        ui.btn_stop_server = QPushButton("STOP (IMMEDIATE)")
        ui.btn_stop_server.setObjectName("btn_stop_server")
        ui.btn_stop_server.setMinimumHeight(40)
        ui.btn_stop_server.setCursor(Qt.CursorShape.PointingHandCursor)
        ui.btn_stop_server.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        ui.lbl_watchdog_status = QLabel("OFFLINE")
        ui.lbl_watchdog_status.setObjectName("lbl_watchdog_status")
        ui.lbl_watchdog_status.setStyleSheet("font-weight: bold; margin-left: 10px; color: #e74c3c;")
        
        h_reactor_ops.addWidget(ui.btn_start_server)
        h_reactor_ops.addWidget(ui.btn_shutdown_dialog)
        h_reactor_ops.addWidget(ui.btn_stop_server)
        h_reactor_ops.addWidget(ui.lbl_watchdog_status)
        
        v_reactor.addLayout(h_reactor_ops)
        
        # Reactor Stream Console
        ui.txt_reactor_stream = QTextEdit()
        ui.txt_reactor_stream.setObjectName("txt_reactor_stream")
        ui.txt_reactor_stream.setReadOnly(True)
        ui.txt_reactor_stream.setStyleSheet("background-color: #1e1e1e; color: #ccc; font-family: Consolas; border: 1px solid #333;")
        v_reactor.addWidget(ui.txt_reactor_stream)
        
        # Assemble Splitter Engine
        splitter.addWidget(sys_widget)
        splitter.addWidget(reactor_widget)
        
        # Set default ratio (approx 30% System Logs, 70% Reactor Stream)
        splitter.setSizes([300, 700])
        
        # Inject into final Tab Layout
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(splitter)
        
        return tab