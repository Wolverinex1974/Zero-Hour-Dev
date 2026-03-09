# ==============================================================================
# ZERO HOUR SERVER MANAGER: BOOTSTRAPPER - v24.1 (BLACK BOX EDITION)
# ==============================================================================
# ROLE: Entry point, UI Initializer, Router Coordinator, and Global Logger.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================

import sys
import os
import platform
import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer

# region [CORE_IMPORTS]
from core.app_state import state
from core.logger import flight_recorder
from ui.admin_layouts import AdminLayoutBuilder
from ui.nexus_styler import NexusStyler
# endregion

# region[ROUTER_IMPORTS]
from routers.dashboard_router import DashboardRouter
from routers.config_router import ConfigRouter
from routers.forge_router import ForgeRouter
from routers.economy_router import EconomyRouter
from routers.automation_router import AutomationRouter
# endregion

class ZeroHourManager(QMainWindow):
    """
    The main application window. It builds the UI shell and initializes all 5 
    sub-controllers (Routers) to handle specific business logic.
    """
    def __init__(self):
        super().__init__()
        
        # 1. Initialize the Black Box Flight Recorder immediately.
        flight_recorder.hook_system_streams()
        flight_recorder.write_to_file("========================================", "BOOT")
        flight_recorder.write_to_file("ZERO HOUR MANAGER INITIALIZATION STARTED", "BOOT")
        flight_recorder.write_to_file("========================================", "BOOT")

        # 2. Setup the Main Window properties
        self.setWindowTitle("Zero Hour Ecosystem | Paradoxal Suite v24.1")
        self.setMinimumSize(1200, 800)
        
        # 3. Build the UI using the Builder Pattern
        self.ui = AdminLayoutBuilder.build(self)
        self.setCentralWidget(self.ui.central_widget)
        
        # 4. Apply the Global CSS Theme
        try:
            styler_engine = NexusStyler()
            self.setStyleSheet(styler_engine.get_stylesheet())
            flight_recorder.write_to_file("NexusStyler Theme applied successfully.", "INFO")
        except Exception as theme_error:
            flight_recorder.write_to_file(f"Failed to apply NexusStyler: {str(theme_error)}", "ERROR")
            
        # 5. Initialize the 5 Intelligence Routers
        self._initialize_routers()
        
        # 6. Final UI Setup
        self._connect_global_signals()
        self.log_event("SYSTEM", "Phase 24 Refactor Active. Flight Recorder Engaged.")

    def _initialize_routers(self):
        """
        Instantiates the logic controllers and binds them to the UI components.
        """
        try:
            self.dashboard_router = DashboardRouter(self)
            flight_recorder.write_to_file("DashboardRouter initialized.", "INFO")
            
            self.config_router = ConfigRouter(self, self.ui)
            flight_recorder.write_to_file("ConfigRouter initialized.", "INFO")
            
            self.forge_router = ForgeRouter(self.ui)
            flight_recorder.write_to_file("ForgeRouter initialized.", "INFO")
            
            self.economy_router = EconomyRouter(self.ui)
            flight_recorder.write_to_file("EconomyRouter initialized.", "INFO")
            
            self.automation_router = AutomationRouter(self.ui)
            flight_recorder.write_to_file("AutomationRouter initialized.", "INFO")
            
            # Wire cross-router communication
            self.dashboard_router.server_status_changed.connect(self.automation_router.handle_server_status_change)
            
        except Exception as router_error:
            flight_recorder.write_to_file(f"Critical error during router initialization: {str(router_error)}", "CRITICAL")
            QMessageBox.critical(self, "Boot Failure", f"A router failed to initialize.\n\n{str(router_error)}")

    def _connect_global_signals(self):
        """
        Wires top-level window controls and global state changes.
        """
        # Global Header Buttons
        if hasattr(self.ui, 'btn_global_start'):
            self.ui.btn_global_start.clicked.connect(self.dashboard_router.start_server_sequence)
        
        if hasattr(self.ui, 'btn_global_stop'):
            self.ui.btn_global_stop.clicked.connect(self.dashboard_router.initiate_kill_sequence)

    def log_event(self, category_string, message_text):
        """
        The Master Logging Function. 
        It writes to the physical log file AND updates the visual Dashboard UI.
        """
        if not message_text:
            return
            
        # 1. Write to the physical Black Box
        flight_recorder.write_to_file(message_text, category_string.upper())
        
        # 2. Write to the Left Window (System Log) in the UI
        timestamp_string = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_ui_string = f"[{category_string}] {timestamp_string}: {message_text}"
        
        if hasattr(self, 'dashboard_router'):
            self.dashboard_router.append_system_log(formatted_ui_string)

    def closeEvent(self, event_object):
        """
        Intercepts the application 'X' button to ensure safe shutdowns.
        """
        if hasattr(self, 'dashboard_router') and getattr(self.dashboard_router, 'is_running', False):
            warning_dialog = QMessageBox.question(
                self, 
                "Active Server Detected", 
                "The 7D2D Server is still running.\nClosing the manager will forcefully terminate the server without saving.\n\nAre you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if warning_dialog == QMessageBox.No:
                event_object.ignore()
                return
            else:
                flight_recorder.write_to_file("User forced application close while server was running. Killing process.", "WARNING")
                self.dashboard_router.initiate_kill_sequence()
                
        flight_recorder.write_to_file("========================================", "SHUTDOWN")
        flight_recorder.write_to_file("ZERO HOUR MANAGER TERMINATED NORMALLY", "SHUTDOWN")
        flight_recorder.write_to_file("========================================", "SHUTDOWN")
        event_object.accept()

# region[APPLICATION_ENTRY]
def main():
    """
    The main execution block for the compiled .exe.
    """
    application_instance = QApplication(sys.argv)
    
    if platform.system() == "Windows":
        import ctypes
        application_id = "paradoxal.zerohour.manager.v24"
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(application_id)
        except Exception:
            pass 

    main_window_instance = ZeroHourManager()
    main_window_instance.show()
    
    sys.exit(application_instance.exec())

if __name__ == "__main__":
    main()
# endregion