# =========================================================
# ZERO HOUR UI: DASHBOARD TAB - v21.2
# =========================================================
# ROLE: Combines System Info and Live Reactor Logs into a
#       single, unified Command Center view.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 FIX:
# FIX: Attaches widgets to (main_ui.ui) instead of (main_ui).
#      This ensures Logic Engines can find them via attributes.
# FIX: Restored Tactical Navigation Buttons (Root/Logs/etc).
# FIX: 100% Bracket-Free payload.
# =========================================================

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
        # FIX: Removed (main_ui.centralwidget) argument.
        tab = QWidget()
        
        # CRITICAL BRIDGE:
        # Connect to the Layout Object (ZeroHourLayout)
        ui = main_ui.ui
        
        # Using a splitter allows the Admin to dynamically resize
        # the System Log vs Reactor Log width while the server is running.
        splitter = QSplitter(Qt.Horizontal)
        
        # -------------------------------------------------------------
        # LEFT PANE: SYSTEM INTELLIGENCE
        # -------------------------------------------------------------
        sys_widget = QWidget()
        v_system = QVBoxLayout(sys_widget)
        v_system.setContentsMargins(0, 0, 5, 0)
        
        # Instance Header
        ui.lbl_instance_info = QLabel("INSTANCE: UNCONFIGURED")
        ui.lbl_instance_info.setObjectName("lbl_instance_info")
        ui.lbl_instance_info.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 14px; margin-bottom: 5px;")
        v_system.addWidget(ui.lbl_instance_info)
        
        # Tactical Navigation (Restored)
        # These buttons allow quick access to physical folders
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #2d2d30; border-radius: 4px;")
        h_nav = QHBoxLayout(nav_frame)
        h_nav.setContentsMargins(5, 5, 5, 5)
        
        ui.btn_open_root = QPushButton("ROOT")
        ui.btn_open_root.setObjectName("btn_open_root")
        ui.btn_open_root.setStyleSheet("background-color: #333; color: #ccc;")
        
        ui.btn_open_logs = QPushButton("LOGS")
        ui.btn_open_logs.setObjectName("btn_open_logs")
        ui.btn_open_logs.setStyleSheet("background-color: #333; color: #ccc;")
        
        ui.btn_open_saves = QPushButton("SAVES")
        ui.btn_open_saves.setObjectName("btn_open_saves")
        ui.btn_open_saves.setStyleSheet("background-color: #333; color: #ccc;")
        
        ui.btn_open_mods = QPushButton("MODS")
        ui.btn_open_mods.setObjectName("btn_open_mods")
        ui.btn_open_mods.setStyleSheet("background-color: #333; color: #ccc;")
        
        h_nav.addWidget(ui.btn_open_root)
        h_nav.addWidget(ui.btn_open_logs)
        h_nav.addWidget(ui.btn_open_saves)
        h_nav.addWidget(ui.btn_open_mods)
        
        v_system.addWidget(nav_frame)
        
        # System Log
        lbl_syslog = QLabel("SYSTEM EVENTS")
        lbl_syslog.setStyleSheet("font-weight: bold; color: #7f8c8d; margin-top: 5px;")
        v_system.addWidget(lbl_syslog)
        
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
        
        # Control Deck
        h_reactor_ops = QHBoxLayout()
        
        ui.btn_start_server = QPushButton("START SERVER")
        ui.btn_start_server.setObjectName("btn_start_server")
        ui.btn_start_server.setMinimumHeight(40)
        ui.btn_start_server.setCursor(Qt.PointingHandCursor)
        ui.btn_start_server.setStyleSheet("background-color: #2ecc71; color: black; font-weight: bold;")
        
        ui.btn_shutdown_dialog = QPushButton("SHUTDOWN / RESTART")
        ui.btn_shutdown_dialog.setObjectName("btn_shutdown_dialog")
        ui.btn_shutdown_dialog.setMinimumHeight(40)
        ui.btn_shutdown_dialog.setCursor(Qt.PointingHandCursor)
        ui.btn_shutdown_dialog.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        
        ui.btn_stop_server = QPushButton("STOP (IMMEDIATE)")
        ui.btn_stop_server.setObjectName("btn_stop_server")
        ui.btn_stop_server.setMinimumHeight(40)
        ui.btn_stop_server.setCursor(Qt.PointingHandCursor)
        ui.btn_stop_server.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        ui.lbl_watchdog_status = QLabel("OFFLINE")
        ui.lbl_watchdog_status.setObjectName("lbl_watchdog_status")
        ui.lbl_watchdog_status.setStyleSheet("font-weight: bold; margin-left: 10px; color: #e74c3c;")
        
        h_reactor_ops.addWidget(ui.btn_start_server)
        h_reactor_ops.addWidget(ui.btn_shutdown_dialog)
        h_reactor_ops.addWidget(ui.btn_stop_server)
        h_reactor_ops.addWidget(ui.lbl_watchdog_status)
        
        v_reactor.addLayout(h_reactor_ops)
        
        # Reactor Stream
        ui.txt_reactor_stream = QTextEdit()
        ui.txt_reactor_stream.setObjectName("txt_reactor_stream")
        ui.txt_reactor_stream.setReadOnly(True)
        ui.txt_reactor_stream.setStyleSheet("background-color: #1e1e1e; color: #ccc; font-family: Consolas; border: 1px solid #333;")
        v_reactor.addWidget(ui.txt_reactor_stream)
        
        # Assemble Splitter Engine
        splitter.addWidget(sys_widget)
        splitter.addWidget(reactor_widget)
        
        # Set default ratio (approx 30% System Logs, 70% Reactor Stream)
        splitter.setSizes(list((300, 700)))
        
        # Inject into final Tab Layout
        main_layout = QVBoxLayout(tab)
        main_layout.addWidget(splitter)
        
        return tab