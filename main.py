import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

# region [IMPORTS_UI]
# FIX: Importing the correct class from admin_layouts
from ui.admin_layouts import ZeroHourLayout
# endregion

# region [IMPORTS_CORE]
from core.app_state import state
# endregion

# region [IMPORTS_ROUTERS]
from routers.dashboard_router import DashboardRouter
from routers.config_router import ConfigRouter
from routers.forge_router import ForgeRouter
from routers.economy_router import EconomyRouter
from routers.automation_router import AutomationRouter
# endregion

# ======================================================
# ZERO HOUR: MAIN BOOTSTRAPPER - v21.2
# ======================================================
# ROLE: Application Entry Point & Router Orchestrator
# ENGINE: PySide6 (Native)
# ======================================================

class ZeroHourManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Setup Logging & State
        self._init_system_state()
        
        # 2. Load UI (Using ZeroHourLayout Engine)
        self.ui = ZeroHourLayout()
        self.ui.setup_ui(self) # FIX: Changed from setupUi to setup_ui
        
        # 3. Apply Compatibility Aliases
        # The routers expect specific names (e.g. dashboard_tab), but the layout
        # uses 'tab_dashboard'. We bridge them here.
        self.ui.dashboard_tab = self.ui.tab_dashboard
        self.ui.configuration_tab = self.ui.tab_config
        self.ui.forge_tab = self.ui.tab_forge
        self.ui.economy_tab = self.ui.tab_economy
        self.ui.automation_tab = self.ui.tab_automation
        
        # 4. Window Configuration
        self.setWindowTitle("Zero Hour Ecosystem | Paradoxal Suite v21.2")
        if os.path.exists("assets/logo.ico"):
            self.setWindowIcon(QIcon("assets/logo.ico"))
        
        # 5. Initialize Routers
        self._init_routers()
        
        # 6. Wire Navigation
        self._setup_navigation()
        
        self.log_system_event("SYSTEM: Phase 21 Refactor Initialized (PySide6).")

    # region [SYSTEM_INIT]
    def _init_system_state(self):
        state.base_directory = os.getcwd()
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
        logging.basicConfig(
            filename='logs/manager.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_system_event(self, message):
        logging.info(message)
        # Check if dashboard router is ready before trying to log to UI
        if hasattr(self, 'dashboard_router'):
            self.dashboard_router.append_log(message)
        else:
            print(f"[BOOT] {message}")
    # endregion

    # region [ROUTER_INJECTION]
    def _init_routers(self):
        try:
            self.dashboard_router = DashboardRouter(self)
            self.config_router = ConfigRouter(self)
            self.forge_router = ForgeRouter(self)
            self.economy_router = EconomyRouter(self)
            self.automation_router = AutomationRouter(self)
        except Exception as e:
            logging.critical(f"ROUTER INIT FAILED: {e}")
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
    # endregion

    # region [NAVIGATION_LOGIC]
    def _setup_navigation(self):
        # FIX: Updated keys to match 'admin_layouts.py' variable names
        nav_map = {
            "btn_nav_dashboard": 0,
            "btn_nav_config": 1,      # Was btn_nav_configuration
            "btn_nav_forge": 2,
            "btn_nav_economy": 3,
            "btn_nav_automation": 4,
            "btn_nav_faq": 5
        }

        for btn_name, page_index in nav_map.items():
            # Check if button exists in the layout class
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                if btn:
                    btn.clicked.connect(lambda checked=False, idx=page_index: self.switch_page(idx))
            else:
                print(f"WARNING: Nav Button '{btn_name}' not found in Layout.")

    def switch_page(self, index):
        # FIX: AdminLayouts uses 'content_stack', not 'stackedWidget'
        if hasattr(self.ui, 'content_stack'):
            self.ui.content_stack.setCurrentIndex(index)
    # endregion

    # region [UI_UTILITIES]
    def set_button_busy(self, button, temp_text):
        if button:
            button.setEnabled(False)
            button.setText(temp_text)
    # endregion

def main():
    app = QApplication(sys.argv)
    window = ZeroHourManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()