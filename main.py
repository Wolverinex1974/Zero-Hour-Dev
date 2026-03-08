import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

# region [IMPORTS_UI]
# Import the generated UI class
# Ensure your UI file is compiled to 'ui/main_ui.py' or update this import
from ui.main_ui import Ui_MainWindow
# endregion

# region [IMPORTS_CORE]
from core.app_state import state
# endregion

# region [IMPORTS_ROUTERS]
# The new controllers that hold the logic
from routers.dashboard_router import DashboardRouter
from routers.config_router import ConfigRouter
from routers.forge_router import ForgeRouter
from routers.economy_router import EconomyRouter
from routers.automation_router import AutomationRouter
# endregion

# ======================================================
# ZERO HOUR: MAIN BOOTSTRAPPER - v21.0
# ======================================================
# ROLE: Application Entry Point & Router Orchestrator
# STRATEGY: Controller/Router Pattern
# ======================================================

class ZeroHourManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Setup Logging & State
        self._init_system_state()
        
        # 2. Load UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 3. Window Configuration
        self.setWindowTitle("Zero Hour Ecosystem | Paradoxal Suite v21.0")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        
        # 4. Initialize Routers (The Logic Injection)
        self._init_routers()
        
        # 5. Wire Navigation (Global Header)
        self._setup_navigation()
        
        # 6. Final Boot Tasks
        self.log_system_event("SYSTEM: Phase 21 Refactor Initialized.")
        self.log_system_event("SYSTEM: All Routers Online.")

    # region [SYSTEM_INIT]
    def _init_system_state(self):
        """
        Initialize the global application state and paths.
        """
        # Set base directory for other routers to use
        state.base_directory = os.getcwd()
        
        # Ensure critical folders exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
        # Setup basic logging config
        logging.basicConfig(
            filename='logs/manager.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_system_event(self, message):
        """
        Central logging hub. Routers call this to log to the UI console.
        """
        logging.info(message)
        
        # Pass to Dashboard Router if it exists, else queue it?
        # Since routers are initialized AFTER this class, we check existence.
        if hasattr(self, 'dashboard_router'):
            self.dashboard_router.append_log(message)
        else:
            print(f"[BOOT] {message}")
    # endregion

    # region [ROUTER_INJECTION]
    def _init_routers(self):
        """
        Instantiate all Logic Controllers.
        Each router gets a reference to 'self' (MainWindow) to access UI elements.
        """
        try:
            # A. Dashboard (Server Control & Logs)
            self.dashboard_router = DashboardRouter(self)
            
            # B. Configuration (Identity & Provisioning)
            self.config_router = ConfigRouter(self)
            
            # C. Forge (Mod Management)
            self.forge_router = ForgeRouter(self)
            
            # D. Economy (Ledger & Currency)
            self.economy_router = EconomyRouter(self)
            
            # E. Automation (Backups & Watchdog)
            self.automation_router = AutomationRouter(self)
            
            # F. Dependency Injection (Cross-Router Communication)
            # Example: Config router needs to tell Dashboard about path changes
            # self.config_router.settings_changed.connect(self.dashboard_router.reload_paths)
            
        except Exception as e:
            logging.critical(f"ROUTER INIT FAILED: {e}")
            print(f"CRITICAL ERROR: {e}")
    # endregion

    # region [NAVIGATION_LOGIC]
    def _setup_navigation(self):
        """
        Wires the Top-Nav buttons to the StackedWidget pages.
        """
        # Define the buttons and their corresponding Page Index in the Stack
        # Ensure these object names match your .ui file exactly
        nav_map = {
            "btn_nav_dashboard": 0,
            "btn_nav_configuration": 1,
            "btn_nav_forge": 2,
            "btn_nav_economy": 3,
            "btn_nav_automation": 4,
            "btn_nav_faq": 5  # If exists
        }

        for btn_name, page_index in nav_map.items():
            btn = self.ui.findChild(object, btn_name)
            if btn:
                # Use lambda to capture the specific page index
                btn.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))
            else:
                print(f"WARNING: Nav Button '{btn_name}' not found in UI.")

    def switch_page(self, index):
        """
        Changes the central stacked widget view.
        """
        if hasattr(self.ui, 'stackedWidget'):
            self.ui.stackedWidget.setCurrentIndex(index)
    # endregion

    # region [UI_UTILITIES]
    def set_button_busy(self, button, temp_text):
        """
        Helper for routers to disable a button temporarily.
        """
        original_text = button.text()
        button.setEnabled(False)
        button.setText(temp_text)
        # Store original text in property if needed, or rely on Router to reset it.
    # endregion

# region [ENTRY_POINT]
def main():
    """
    Application Launch Sequence.
    """
    app = QApplication(sys.argv)
    
    # Optional: Load Stylesheet
    # with open("assets/styles.qss", "r") as f:
    #     app.setStyleSheet(f.read())
        
    window = ZeroHourManager()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# endregion