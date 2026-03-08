import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

# region [IMPORTS_UI]
# Using the corrected Layout Engine
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

# ==============================================================================
# ZERO HOUR: MAIN BOOTSTRAPPER - v21.4
# ==============================================================================
# ROLE: Application Entry Point & Central Nervous System.
# RESPONSIBILITY: Initializes UI, loads Routers, and wires the "Watchdog" logic.
# ENGINE: PySide6 (Native)
# ==============================================================================

class ZeroHourManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Setup Logging & State
        self._init_system_state()
        
        # 2. Load UI (Using ZeroHourLayout Engine)
        self.ui = ZeroHourLayout()
        self.ui.setup_ui(self)
        
        # 3. Apply Compatibility Aliases
        # (Bridges the gap between Layout names and Router expectations)
        self.ui.dashboard_tab = getattr(self.ui, 'tab_dashboard', None)
        self.ui.configuration_tab = getattr(self.ui, 'tab_config', None)
        self.ui.forge_tab = getattr(self.ui, 'tab_forge', None)
        self.ui.economy_tab = getattr(self.ui, 'tab_economy', None)
        self.ui.automation_tab = getattr(self.ui, 'tab_automation', None)
        
        # 4. Window Configuration
        self.setWindowTitle("Zero Hour Ecosystem | Paradoxal Suite v21.4")
        if os.path.exists("assets/logo.ico"):
            self.setWindowIcon(QIcon("assets/logo.ico"))
        
        # 5. Initialize Routers (The Logic Injection)
        self._init_routers()
        
        # 6. Wire Subsystems (Watchdog & Nav)
        self._setup_navigation()
        self._wire_watchdog_system()
        
        # 7. Final Boot
        self.log_system_event("SYSTEM: Phase 21 Refactor Complete. Watchdog Active.")

    # region [SYSTEM_INIT]
    def _init_system_state(self):
        """
        Initialize the global application state and paths.
        """
        state.base_directory = os.getcwd()
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
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
        # Pass to Dashboard Router if it exists
        if hasattr(self, 'dashboard_router') and self.dashboard_router:
            self.dashboard_router.append_log(message)
        else:
            print(f"[BOOT] {message}")
    # endregion

    # region [ROUTER_INJECTION]
    def _init_routers(self):
        """
        Instantiate all Logic Controllers.
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
            
        except Exception as e:
            logging.critical(f"ROUTER INIT FAILED: {e}")
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
    # endregion

    # region [WATCHDOG_LOGIC]
    def _wire_watchdog_system(self):
        """
        Connects the Dashboard (Server Process) to the Automation Router.
        """
        if self.dashboard_router and self.dashboard_router.server_process:
            # Listen for when the server stops/crashes
            self.dashboard_router.server_process.finished.connect(self.on_server_process_finished)

    def on_server_process_finished(self, exit_code, exit_status):
        """
        Triggered whenever the dedicated server closes.
        Decides if we should Auto-Restart (Watchdog).
        """
        self.log_system_event(f"WATCHDOG: Process ended (Code {exit_code}). Analyzing...")

        # 1. Check if Watchdog is Enabled in Automation Tab
        # We access the checkbox directly via the UI namespace
        chk_watchdog = getattr(self.ui, 'chk_enable_watchdog', None)
        
        if chk_watchdog and chk_watchdog.isChecked():
            # 2. Check if it was a manual stop (Optional: logic to distinguish stop vs crash)
            # For now, if "Keep Alive" is checked, we ALWAYS restart unless we explicitly implement a "Maintenance Mode".
            
            self.log_system_event("WATCHDOG: Auto-Restart Sequence Initiated (T-Minus 5s)")
            
            # 3. Schedule Restart
            QTimer.singleShot(5000, self.execute_auto_restart)
        else:
            self.log_system_event("WATCHDOG: Auto-Restart Disabled. Standing by.")

    def execute_auto_restart(self):
        """
        Callback to restart the server.
        """
        self.log_system_event("WATCHDOG: REBOOTING SERVER...")
        if self.dashboard_router:
            self.dashboard_router.start_server_sequence()
    # endregion

    # region [NAVIGATION_LOGIC]
    def _setup_navigation(self):
        """
        Wires the Top-Nav buttons to the StackedWidget pages.
        """
        nav_map = {
            "btn_nav_dashboard": 0,
            "btn_nav_config": 1,
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
        """
        Changes the central stacked widget view.
        """
        if hasattr(self.ui, 'content_stack'):
            self.ui.content_stack.setCurrentIndex(index)
    # endregion

    # region [UI_UTILITIES]
    def set_button_busy(self, button, temp_text):
        """
        Helper for routers to disable a button temporarily.
        """
        if button:
            button.setEnabled(False)
            button.setText(temp_text)
    # endregion

# region [ENTRY_POINT]
def main():
    """
    Application Launch Sequence.
    """
    app = QApplication(sys.argv)
    
    # Optional: Load external stylesheet if exists
    # if os.path.exists("assets/style.qss"):
    #     with open("assets/style.qss", "r") as f:
    #         app.setStyleSheet(f.read())
        
    window = ZeroHourManager()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# endregion