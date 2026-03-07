# =========================================================
# ZERO HOUR: MASTER NEXUS COMMAND - v20.8
# =========================================================
# ROLE: Multi-Instance Orchestration (Sovereign Hub)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 UI RESTORATION:
# FIX: Wired up new GLOBAL HEADER buttons (Start/Stop/Tactical)
#      to match the new "Top-Nav" Layout.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

VERSION = "20.8"

import sys
import os
import time
import traceback
import logging
import ctypes
import csv
import datetime
import socket
import requests
import webbrowser

# --- IMMEDIATE TERMINAL FEEDBACK ---
print(f" ZERO HOUR NEXUS COMMAND v{VERSION}", flush=True)

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(f" ROOT DIRECTORY: {BASE_DIR}", flush=True)

# --- CRASH HANDLER ---
def global_crash_handler(etype, value, tb):
    error_msg = "".join(traceback.format_exception(etype, value, tb))
    print(f"\n CRITICAL FAILURE \n{error_msg}", flush=True)

    try:
        with open(os.path.join(BASE_DIR, "CRASH_LOG_FULL.txt"), "a", encoding="utf-8") as f:
            f.write(f"\nTIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n{error_msg}\n")
    except Exception:
        pass

    try:
        ctypes.windll.user32.MessageBoxW(0, f"Critical Error:\n{value}\n\nSee CRASH_LOG_FULL.txt", "Zero Hour Crash", 0x10)
    except Exception:
        pass
    
    # KEEP CONSOLE OPEN
    input(" PRESS ENTER TO EXIT...")
    sys.exit(1)

sys.excepthook = global_crash_handler

# --- IMPORTS & ERROR CATCHER ---
try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QFileDialog, QTreeWidgetItem)
    from PySide6.QtCore import (Qt, QTimer, QCoreApplication, Slot)
    from PySide6.QtGui import (QTextCursor, QColor)

    # GLOBAL UI IMPORTS
    from ui.admin_layouts import ZeroHourLayout
    from ui.dialogs import AdvancedRestartDialog
    from ui.nexus_styler import NexusStyler

    # CORE IMPORTS
    from core.app_state import state
    from core.logger import ParadoxalLogger
    from core.profile_manager import ProfileManager
    from core.manifest_manager import update_news_feed, get_manifest
    from core.database_manager import DatabaseManager
    from core.settings_bridge import SettingsBridge
    from core.pipeline_manager import PipelineManager
    from core.reactor_controller import ReactorController
    from core.provisioning_engine import SteamCMDInitializer, SteamCMDDownloader
    from core.validator import validate_server_heartbeat, get_dynamic_log_path, get_dynamic_save_path

    # MODULAR CONTROLLERS
    from core.mod_controller import ModController
    from core.profile_controller import ProfileController
    from core.boot_sequence import BootSequence

    # WORKERS
    from core.archiver import WorldArchiver
    from core.mod_installer import ModInstallerWorker
    from core.forge_engine import DistroWorker
    from core.workers.garbage_collector import CloudGarbageCollector
    from core.workers.xml_auditor import XMLCollisionAuditor

except Exception as e:
    error_details = traceback.format_exc()
    print(f"\n{'='*60}")
    print(f" CRITICAL IMPORT ENGINE FAILURE: ")
    print(f"{'='*60}")
    print(error_details)
    print(f"{'='*60}")
    print(" The application cannot boot because a core module failed to load.")
    print(" This is usually caused by a syntax error in the referenced file.")
    input("\n Press ENTER to close this window...")
    sys.exit(1)

MANIFEST_VAULT = os.path.join(BASE_DIR, "manifests")
if not os.path.exists(MANIFEST_VAULT):
    os.makedirs(MANIFEST_VAULT, exist_ok=True)

try:
    px_handler = ParadoxalLogger(os.path.join(BASE_DIR, "logs"))
    log = px_handler.get_logger()
except Exception:
    pass

class ZeroHourManager(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- SAFE BOOT SEQUENCE ---
        try:
            print(" 1. Init State...", end="", flush=True)
            state.update_status("version", VERSION)
            state.update_status("base_directory", BASE_DIR)
            state.disabled_mods_path = ""
            state.initialize_registry(BASE_DIR)
            print(" OK", flush=True)
        except Exception as e:
            print(f" FAIL ({e})", flush=True)
            log.error(f" Registry Init Failed: {e}")

        try:
            print(" 2. Init Database...", end="", flush=True)
            self.database = DatabaseManager(BASE_DIR)
            print(" OK", flush=True)
        except Exception as e:
            print(f" FAIL ({e})", flush=True)

        print(" 3. Constructing UI...", flush=True)
        self.ui = ZeroHourLayout()
        self.ui.setup_ui(self)

        env_tag = " (TEST ENV)" if state.is_test_env else ""
        self.setWindowTitle(f"Zero Hour Nexus Command v{state.version}{env_tag}")
        self.setStyleSheet(NexusStyler.get_industrial_style())

        # --- INITIALIZE CORE ENGINES ---
        self.profiles_nexus = ProfileManager(BASE_DIR)
        self.settings_bridge = SettingsBridge(self.ui)
        self.github = None
        self.pipeline = PipelineManager(None)
        self.reactor = ReactorController(self.database)
        self.xml_auditor = XMLCollisionAuditor(None)
        
        # --- INITIALIZE MODULAR CONTROLLERS ---
        self.mod_ctrl = ModController(self)
        self.profile_ctrl = ProfileController(self)
        self.boot_seq = BootSequence(self)

        # --- ANTI-FREEZE LOG RENDERER SETTINGS ---
        # Safety Check for Dashboard widget presence
        if hasattr(self.ui, "tab_dashboard"):
            txt_stream = self.ui.tab_dashboard.findChild(object, "txt_reactor_stream")
            if txt_stream:
                txt_stream.document().setMaximumBlockCount(1000)
            
        self.log_buffer = list()

        self.log_render_timer = QTimer()
        self.log_render_timer.setInterval(200)
        self.log_render_timer.timeout.connect(self.flush_log_buffer)
        self.log_render_timer.start()

        # --- WORKER THREADS & STATE ---
        self.backup_worker = None
        self.mod_install_worker = None
        self.distro_worker = None
        self.store_manager = None
        self.garbage_worker = None
        self.init_worker = None
        self.deploy_worker = None
        self.audit_worker = None
        self.last_audit_results = dict()

        self.setup_hub_bindings()
        self.connect_engine_signals()
        px_handler.ui_handler.log_signal.connect(self.add_system_log)

        # PHASE 20.1: Force early UI hydration
        self.on_tab_changed(0)

        # Ignite the modular boot sequence
        QTimer.singleShot(800, self.boot_seq.ignite)
        print(" UI CONSTRUCTION COMPLETE.", flush=True)

    def set_button_busy(self, button, label="PROCESSING..."):
        if button:
            button.setEnabled(False)
            button.setText(label)
            QCoreApplication.processEvents()

    def exec_with_tactile(self, button, func, label="PROCESSING..."):
        self.set_button_busy(button, label)
        func()

    def closeEvent(self, event):
        if state.server_process_active:
            self.reactor.stop_reactor()

        if hasattr(self, "database"):
            self.database.close()

        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def setup_hub_bindings(self):
        """
        Connects UI signals to slots. 
        WIRES UP GLOBAL HEADER BUTTONS + LOCAL TAB BUTTONS.
        """
        
        # --- GLOBAL HEADER CONNECTIONS (Phase 20 Restoration) ---
        
        # 1. Tactical Navigation (Global)
        if hasattr(self.ui, "btn_open_root") and self.ui.btn_open_root:
            self.ui.btn_open_root.clicked.connect(lambda: self.open_tactical_folder("ROOT"))
            
        if hasattr(self.ui, "btn_open_logs") and self.ui.btn_open_logs:
            self.ui.btn_open_logs.clicked.connect(lambda: self.open_tactical_folder("LOGS"))
            
        if hasattr(self.ui, "btn_open_saves") and self.ui.btn_open_saves:
            self.ui.btn_open_saves.clicked.connect(lambda: self.open_tactical_folder("SAVES"))
            
        if hasattr(self.ui, "btn_open_mods") and self.ui.btn_open_mods:
            self.ui.btn_open_mods.clicked.connect(lambda: self.open_tactical_folder("MODS"))

        # 2. Global Reactor Controls
        if hasattr(self.ui, "btn_start_server_global") and self.ui.btn_start_server_global:
            self.ui.btn_start_server_global.clicked.connect(lambda: self.exec_with_tactile(self.ui.btn_start_server_global, self.reactor.start_reactor, "STARTING..."))
            
        if hasattr(self.ui, "btn_stop_server_global") and self.ui.btn_stop_server_global:
            self.ui.btn_stop_server_global.clicked.connect(lambda: self.exec_with_tactile(self.ui.btn_stop_server_global, self.reactor.stop_reactor, "STOPPING..."))
            
        if hasattr(self.ui, "btn_shutdown_dialog_global") and self.ui.btn_shutdown_dialog_global:
            self.ui.btn_shutdown_dialog_global.clicked.connect(self.initiate_shutdown_sequence)

        # 3. Profile Management (Global)
        if hasattr(self.ui, "combo_profile_selector") and self.ui.combo_profile_selector:
            # We delay signal connection or handle logic in ProfileController
            pass 
            
        # --- LOCAL TAB CONNECTIONS (Redundancy) ---

        # A. DASHBOARD (Safety Check: ensure tab exists)
        if hasattr(self.ui, "tab_dashboard"):
            # Local Start Button
            btn_start = self.ui.tab_dashboard.findChild(object, "btn_start_server")
            if btn_start: 
                btn_start.clicked.connect(lambda: self.exec_with_tactile(btn_start, self.reactor.start_reactor, "STARTING..."))
            
            # Local Stop Button
            btn_stop = self.ui.tab_dashboard.findChild(object, "btn_stop_server")
            if btn_stop: 
                btn_stop.clicked.connect(lambda: self.exec_with_tactile(btn_stop, self.reactor.stop_reactor, "STOPPING..."))
            
            # Local Shutdown Button
            btn_restart = self.ui.tab_dashboard.findChild(object, "btn_shutdown_dialog")
            if btn_restart: 
                btn_restart.clicked.connect(self.initiate_shutdown_sequence)

        # B. CONFIGURATION TAB
        if hasattr(self.ui, "tab_config"):
            btn_save_id = self.ui.tab_config.findChild(object, "btn_save_identity")
            if btn_save_id: btn_save_id.clicked.connect(self.save_identity_data)
            
            btn_save_xml = self.ui.tab_config.findChild(object, "btn_save_srv_settings")
            if btn_save_xml: btn_save_xml.clicked.connect(lambda: self.exec_with_tactile(btn_save_xml, self.on_save_xml_settings, "COMMITTING..."))
            
            btn_adopt = self.ui.tab_config.findChild(object, "btn_browse_adopt")
            if btn_adopt: btn_adopt.clicked.connect(self.path_adopt_existing)
            
            btn_init = self.ui.tab_config.findChild(object, "btn_init_tool")
            if btn_init: btn_init.clicked.connect(self.path_initialize_tool)
            
            btn_deploy = self.ui.tab_config.findChild(object, "btn_deploy_fresh")
            if btn_deploy: btn_deploy.clicked.connect(self.path_provision_new)

        # C. FORGE TAB
        if hasattr(self.ui, "tab_forge"):
            btn_install = self.ui.tab_forge.findChild(object, "btn_install_mod")
            if btn_install: btn_install.clicked.connect(self.initiate_mod_install)
            
            btn_rebal = self.ui.tab_forge.findChild(object, "btn_rebalance_mods")
            if btn_rebal: btn_rebal.clicked.connect(self.trigger_mass_rebalance)
            
            btn_commit = self.ui.tab_forge.findChild(object, "btn_commit_deploy")
            if btn_commit: btn_commit.clicked.connect(lambda: self.exec_with_tactile(btn_commit, self.start_pipeline_sequence, "SYNCHRONIZING..."))
            
            btn_scan = self.ui.tab_forge.findChild(object, "btn_scan_duplicates")
            if btn_scan: btn_scan.clicked.connect(self.execute_duplicate_scan)
            
            btn_audit = self.ui.tab_forge.findChild(object, "btn_run_audit")
            if btn_audit: btn_audit.clicked.connect(self.execute_xml_audit)
            
            btn_export_audit = self.ui.tab_forge.findChild(object, "btn_export_audit")
            if btn_export_audit: btn_export_audit.clicked.connect(self.export_audit_report)
            
            btn_up = self.ui.tab_forge.findChild(object, "btn_mod_up")
            if btn_up: btn_up.clicked.connect(lambda: self.mod_ctrl.action_mod_move("UP"))
            
            btn_down = self.ui.tab_forge.findChild(object, "btn_mod_down")
            if btn_down: btn_down.clicked.connect(lambda: self.mod_ctrl.action_mod_move("DOWN"))

        # D. ECONOMY TAB
        if hasattr(self.ui, "tab_economy"):
            btn_refresh = self.ui.tab_economy.findChild(object, "btn_refresh_ledger")
            if btn_refresh: btn_refresh.clicked.connect(self.refresh_player_ledger)
            
            btn_export = self.ui.tab_economy.findChild(object, "btn_export_wealth")
            if btn_export: btn_export.clicked.connect(self.export_wealth_data)

        # E. AUTOMATION TAB
        if hasattr(self.ui, "tab_automation"):
            btn_backup = self.ui.tab_automation.findChild(object, "btn_backup_now")
            if btn_backup: btn_backup.clicked.connect(self.start_backup_sequence)

    def connect_engine_signals(self):
        self.reactor.status_update_signal.connect(self.update_status_ui)
        self.reactor.log_line_signal.connect(self.add_reactor_line)
        self.reactor.system_log_signal.connect(self.add_system_log)
        self.pipeline.pipeline_status_signal.connect(self.handle_pipeline_progress)
        self.pipeline.pipeline_finished_signal.connect(self.handle_pipeline_completion)
        self.reactor.ledger_signal.connect(self.refresh_player_ledger)

    @Slot(int)
    def on_tab_changed(self, idx):
        """Switches the Right-Hand Content Stack"""
        if hasattr(self.ui, "content_stack"):
            self.ui.content_stack.setCurrentIndex(idx)
            self.log_system_event(f"Switched to Tab Index: {idx}")

        if idx == 1 and validate_server_heartbeat(state.server_path):
            QTimer.singleShot(10, self.settings_bridge.load_settings_into_ui)
            QTimer.singleShot(20, self.refresh_generated_worlds)

        if idx == 2 and validate_server_heartbeat(state.server_path):
            QTimer.singleShot(10, self.mod_ctrl.refresh_mod_list)

        if idx == 3:
            QTimer.singleShot(10, self.refresh_player_ledger)

    def toggle_ui_lock(self, enabled):
        """Disables navigation while critical tasks are running."""
        # Top Header Buttons
        if hasattr(self.ui, "btn_start_server_global"):
            self.ui.btn_start_server_global.setEnabled(enabled)
        # We can disable the nav group too if needed
        if hasattr(self.ui, "nav_group"):
            for btn in self.ui.nav_group.buttons():
                btn.setEnabled(enabled)

    def apply_dirty_ui_state(self, dirty):
        state.update_status("is_dirty", dirty)
        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_commit_deploy")
            if btn:
                NexusStyler.apply_dirty_state(btn, dirty)

    def add_system_log(self, message_text):
        formatted_entry = f'<span style="color: #2ecc71;">{message_text}</span>'
        if hasattr(self.ui, "tab_dashboard"):
            txt_log = self.ui.tab_dashboard.findChild(object, "txt_system_log")
            if txt_log:
                txt_log.append(formatted_entry)
                txt_log.moveCursor(QTextCursor.End)

    def add_reactor_line(self, line_string):
        self.log_buffer.append(line_string)

    def flush_log_buffer(self):
        if len(self.log_buffer) == 0:
            return

        lines_to_process = list()
        limit = 0

        while limit < 250 and len(self.log_buffer) > 0:
            lines_to_process.append(self.log_buffer.pop(0))
            limit = limit + 1

        html_chunks = list()
        for raw_line in lines_to_process:
            text_color = "#ffffff"
            if "ERR" in raw_line or "Exception" in raw_line:
                text_color = "#e74c3c"
            elif "WRN" in raw_line:
                text_color = "#f1c40f"
            elif "INF" in raw_line:
                text_color = "#2ecc71"

            safe_line = raw_line.replace("<", "&lt;").replace(">", "&gt;")
            html_chunks.append(f'<span style="color: {text_color};">{safe_line}</span>')

        final_html = "<br>".join(html_chunks)
        
        if hasattr(self.ui, "tab_dashboard"):
            txt_stream = self.ui.tab_dashboard.findChild(object, "txt_reactor_stream")
            if txt_stream:
                txt_stream.append(final_html)

    def update_status_ui(self, status_label, status_color):
        # Update GLOBAL buttons
        if hasattr(self.ui, "btn_start_server_global"):
            if "ONLINE" in status_label:
                self.ui.btn_start_server_global.setEnabled(False)
                self.ui.btn_start_server_global.setText("SERVER LIVE")
            else:
                self.ui.btn_start_server_global.setEnabled(True)
                self.ui.btn_start_server_global.setText("START SERVER")

        # Update LOCAL buttons (if on dashboard)
        if hasattr(self.ui, "tab_dashboard"):
            lbl_status = self.ui.tab_dashboard.findChild(object, "lbl_watchdog_status")
            btn_start = self.ui.tab_dashboard.findChild(object, "btn_start_server")
            
            if lbl_status:
                lbl_status.setText(status_label)
                lbl_status.setStyleSheet(f"color: {status_color}; font-weight: bold;")

            if btn_start:
                if "ONLINE" in status_label:
                    btn_start.setEnabled(False)
                    btn_start.setText("SERVER LIVE")
                else:
                    btn_start.setEnabled(True)
                    btn_start.setText("START SERVER")

    def reset_save_button(self):
        if hasattr(self.ui, "tab_config"):
            btn = self.ui.tab_config.findChild(object, "btn_save_srv_settings")
            if btn:
                btn.setEnabled(True)
                btn.setText("COMMIT SETTINGS TO XML")

    def on_save_xml_settings(self):
        success = self.settings_bridge.save_settings_from_ui()
        if success:
            self.add_system_log("SUCCESS: serverconfig.xml updated.")
            QTimer.singleShot(800, self.reset_save_button)

    def save_identity_data(self):
        if not hasattr(self.ui, "tab_config"): return
        
        txt_repo = self.ui.tab_config.findChild(object, "txt_target_repo")
        txt_port = self.ui.tab_config.findChild(object, "txt_server_port")
        
        if not txt_repo or not txt_port: return
        
        new_repo = txt_repo.text().strip()
        new_port = txt_port.text().strip()

        if not state.current_profile_name:
            QMessageBox.warning(self, "Error", "No active profile selected.")
            return

        self.profiles_nexus.update_profile_key(state.current_profile_name, "target_repo", new_repo)
        self.profiles_nexus.update_profile_key(state.current_profile_name, "server_port", new_port)
        state.target_repo = new_repo
        state.server_port = new_port

        if self.github:
            self.github.set_target_repo(new_repo)

        self.add_system_log(f"IDENTITY SAVED: Repo set to {new_repo}")
        QMessageBox.information(self, "Success", "Server Identity Saved.\n(Repo & Port Updated)")

    def path_adopt_existing(self):
        sel = QFileDialog.getExistingDirectory(self, "Select Root")
        if not sel:
            return

        if not hasattr(self.ui, "tab_config"): return
        txt_name = self.ui.tab_config.findChild(object, "txt_prof_name")
        txt_port = self.ui.tab_config.findChild(object, "txt_server_port")
        txt_repo = self.ui.tab_config.findChild(object, "txt_target_repo")

        p_name = txt_name.text().strip() if txt_name else "Default"
        if not p_name: return

        if validate_server_heartbeat(sel):
            self.profiles_nexus.create_profile(
                p_name,
                sel.replace("/", "\\"),
                txt_port.text() if txt_port else "26900",
                f"manifest_{p_name.lower()}.json",
                txt_repo.text() if txt_repo else ""
            )
            self.profile_ctrl.refresh_profile_list(p_name)
        else:
            QMessageBox.critical(self, "Error", "Binary heartbeat failed.")

    def path_initialize_tool(self):
        if not hasattr(self.ui, "tab_config"): return
        btn_init = self.ui.tab_config.findChild(object, "btn_init_tool")
        
        self.set_button_busy(btn_init, "INITIALIZING...")
        self.init_worker = SteamCMDInitializer(BASE_DIR)
        self.init_worker.log_signal.connect(self.add_setup_log)
        self.init_worker.finished_signal.connect(self.on_tool_init_finished)
        self.init_worker.start()

    def on_tool_init_finished(self, succ, msg):
        if not hasattr(self.ui, "tab_config"): return
        btn_init = self.ui.tab_config.findChild(object, "btn_init_tool")
        if btn_init:
            btn_init.setEnabled(True)
            btn_init.setText("1. INITIALIZE STEAMCMD TOOL")
        if succ:
            self.boot_seq.check_steamcmd_readiness()

    def path_provision_new(self):
        sel = QFileDialog.getExistingDirectory(self, "Select Root")
        if not sel:
            return

        if not hasattr(self.ui, "tab_config"): return
        txt_name = self.ui.tab_config.findChild(object, "txt_prof_name")
        btn_deploy = self.ui.tab_config.findChild(object, "btn_deploy_fresh")
        
        p_name = txt_name.text().strip() if txt_name else "NewServer"
        
        self.set_button_busy(btn_deploy, "DEPLOYING...")
        self.deploy_worker = SteamCMDDownloader(BASE_DIR, sel.replace("/", "\\"))
        self.deploy_worker.log_signal.connect(self.add_setup_log)

        def deploy_callback(s, pr):
            self.on_deploy_complete(s, pr, p_name)

        self.deploy_worker.finished_signal.connect(deploy_callback)
        self.deploy_worker.start()

    def on_deploy_complete(self, succ, path, name):
        if not hasattr(self.ui, "tab_config"): return
        
        btn_deploy = self.ui.tab_config.findChild(object, "btn_deploy_fresh")
        txt_port = self.ui.tab_config.findChild(object, "txt_server_port")
        txt_repo = self.ui.tab_config.findChild(object, "txt_target_repo")
        
        if btn_deploy:
            btn_deploy.setEnabled(True)
            btn_deploy.setText("2. DOWNLOAD 12GB SERVER FILES")
        if succ:
            self.profiles_nexus.create_profile(
                name,
                path,
                txt_port.text() if txt_port else "26900",
                f"manifest_{name.lower()}.json",
                txt_repo.text() if txt_repo else ""
            )
            self.profile_ctrl.refresh_profile_list(name)

    def add_setup_log(self, text):
        if not hasattr(self.ui, "tab_config"): return
        txt_log = self.ui.tab_config.findChild(object, "txt_setup_log")
        if txt_log:
            txt_log.append(text)
            txt_log.moveCursor(QTextCursor.End)
        QCoreApplication.processEvents()

    def open_tactical_folder(self, category):
        if not state.server_path or not os.path.exists(state.server_path):
            self.add_system_log("NAVIGATION ERROR: No active server profile loaded.")
            return

        target_path = state.server_path

        if category == "ROOT":
            target_path = state.server_path

        elif category == "MODS":
            target_path = state.mods_path

        elif category == "LOGS":
            log_file = get_dynamic_log_path(state.server_path)
            if log_file and os.path.exists(os.path.dirname(log_file)):
                target_path = os.path.dirname(log_file)
            else:
                target_path = state.server_path

        elif category == "SAVES":
            sovereign_saves = get_dynamic_save_path(state.server_path)
            local_saves = os.path.join(state.server_path, "Saves")
            user_data_saves = os.path.join(state.server_path, "UserSaveData", "Saves")

            if os.path.exists(sovereign_saves):
                target_path = sovereign_saves
            elif os.path.exists(local_saves):
                target_path = local_saves
            elif os.path.exists(user_data_saves):
                target_path = user_data_saves
            else:
                app_data = os.getenv("APPDATA")
                if app_data:
                    roaming_saves = os.path.join(app_data, "7DaysToDie", "Saves")
                    if os.path.exists(roaming_saves):
                        target_path = roaming_saves

        if os.path.exists(target_path):
            self.add_system_log(f"OPENING TACTICAL FOLDER: {category}")
            try:
                os.startfile(target_path)
            except Exception as e:
                self.add_system_log(f"NAV FAIL: {e}")
        else:
            self.add_system_log(f"NAVIGATION FAILED: Path not found for {category}")

    def initiate_shutdown_sequence(self):
        if not state.server_process_active:
            self.add_system_log("COMMAND REJECTED: Server is not running.")
            return

        dialog = AdvancedRestartDialog(self)
        if dialog.exec():
            reason = dialog.combo_reason.currentText()
            is_restart = dialog.chk_restart.isChecked()
            override_ka = dialog.chk_override.isChecked()
            no_count = dialog.radio_no_count.isChecked()
            m = dialog.spin_min.value()
            s = dialog.spin_sec.value()

            if override_ka:
                # Logic handled in watchdog check
                pass 

            if self.reactor.watchdog:
                self.reactor.watchdog.auto_restart = is_restart

            if no_count:
                self.add_system_log("INITIATING IMMEDIATE SHUTDOWN/RESTART")
                self.reactor.execute_telnet_command('say "SERVER RESTART IMMINENT (IMMEDIATE SHUTDOWN)"')
                self.reactor.execute_telnet_command("saveworld")
                QTimer.singleShot(3000, self.reactor.stop_reactor)
            else:
                self.reactor.schedule_restart(minutes=m, seconds=s, reason=reason)

    def refresh_generated_worlds(self):
        if not hasattr(self.ui, "tab_config"): return
        
        combo_gen = self.ui.tab_config.findChild(object, "combo_WorldGenName")
        if not combo_gen: return
        
        combo_gen.blockSignals(True)
        combo_gen.clear()
        combo_gen.addItem("--- Select World ---")

        if not state.server_path:
            combo_gen.blockSignals(False)
            return

        sovereign_saves = get_dynamic_save_path(state.server_path)
        gen_worlds_path = os.path.join(sovereign_saves, "GeneratedWorlds")

        existing_items = list()
        existing_items.append("--- Select World ---")

        if os.path.exists(gen_worlds_path):
            for folder in os.listdir(gen_worlds_path):
                full_path = os.path.join(gen_worlds_path, folder)
                if os.path.isdir(full_path):
                    combo_gen.addItem(folder)
                    existing_items.append(folder)

        app_data = os.getenv("APPDATA")
        if app_data:
            legacy_gen_worlds = os.path.join(app_data, "7DaysToDie", "GeneratedWorlds")
            if os.path.exists(legacy_gen_worlds):
                for folder in os.listdir(legacy_gen_worlds):
                    full_path = os.path.join(legacy_gen_worlds, folder)
                    if os.path.isdir(full_path):
                        if folder not in existing_items:
                            combo_gen.addItem(folder)
                            existing_items.append(folder)

        combo_gen.blockSignals(False)

    def trigger_mass_rebalance(self):
        if state.server_process_active:
            QMessageBox.warning(self, "Safety Lock", "Cannot rebalance while server is running.")
            return

        confirm = QMessageBox.question(self, "Sanitize & Rebalance",
            "This will convert all mod names to web-safe formatting and space their prefixes by 10 (010, 020).\n\n"
            "WARNING: Because this renames the physical folders, it WILL trigger a mass-upload cascade on your next Sync.\n\nProceed?",
            QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            if hasattr(self.ui, "tab_forge"):
                btn_rebal = self.ui.tab_forge.findChild(object, "btn_rebalance_mods")
                self.set_button_busy(btn_rebal, "REBALANCING...")
                
            manifest = get_manifest(state.manifest_path)
            mods = manifest.get("mods", list())
            self.mod_ctrl.mass_rebalance_prefixes(mods)
            self.mod_ctrl.refresh_mod_list()
            
            if hasattr(self.ui, "tab_forge"):
                btn_rebal = self.ui.tab_forge.findChild(object, "btn_rebalance_mods")
                if btn_rebal:
                    btn_rebal.setEnabled(True)
                    btn_rebal.setText("SANITIZE & REBALANCE")
                    
            self.add_system_log("REBALANCE COMPLETE. Ecosystem is now 100% web-safe.")

    def start_pipeline_sequence(self):
        state.description = "Admin Sync"
        self.pipeline.start_master_deployment()

    def handle_pipeline_progress(self, msg, per):
        if hasattr(self.ui, "tab_forge"):
            bar = self.ui.tab_forge.findChild(object, "progressBar_forge")
            if bar: bar.setValue(per)
            
        if hasattr(self.ui, "lbl_status"):
            self.ui.lbl_status.setText(f"PIPELINE: {msg}")

    def handle_pipeline_completion(self, succ, feed):
        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_commit_deploy")
            bar = self.ui.tab_forge.findChild(object, "progressBar_forge")
            
            if btn:
                btn.setEnabled(True)
                btn.setText("SYNC SERVER TO CLOUD\n(Step 1: Upload Files)")
            if bar:
                bar.setValue(0)

        if succ:
            self.apply_dirty_ui_state(False)

            if feed == "Server Synced Successfully.":
                self.add_system_log("PIPELINE SUCCESS. Auto-publishing to Atlas...")
                self.initiate_atlas_registration()
                QMessageBox.information(self, "Success", "Cloud Operation Complete & Auto-Published to Atlas.\nClients can now see the updates.")
            else:
                self.add_system_log("ATLAS PUBLISH COMPLETE.")
        else:
            QMessageBox.warning(self, "Failure", feed)

    # -------------------------------------------------------------------------
    # PHASE 19.1: XPATH COLLISION AUDITOR
    # -------------------------------------------------------------------------
    def execute_xml_audit(self):
        if not state.mods_path or not os.path.exists(state.mods_path):
            QMessageBox.warning(self, "Auditor Error", "No active Mod folder found.")
            return

        if not hasattr(self.ui, "tab_forge"): return
        
        btn_audit = self.ui.tab_forge.findChild(object, "btn_run_audit")
        btn_export = self.ui.tab_forge.findChild(object, "btn_export_audit")
        tree = self.ui.tab_forge.findChild(object, "tree_conflicts")
        
        self.set_button_busy(btn_audit, "SCANNING XML TREES...")
        if btn_export:
            btn_export.setEnabled(False)
            btn_export.setStyleSheet("background-color: #2c3e50; color: gray; font-weight: bold;")
        
        if tree: tree.clear()
        self.last_audit_results = dict()

        self.audit_worker = XMLCollisionAuditor(state.mods_path)
        self.audit_worker.progress_signal.connect(self.on_audit_progress)
        self.audit_worker.log_signal.connect(self.on_audit_log)
        self.audit_worker.finished_signal.connect(self.on_audit_finished)
        self.audit_worker.start()

    def on_audit_progress(self, message, percent):
        if not hasattr(self.ui, "tab_forge"): return
        
        lbl_status = self.ui.tab_forge.findChild(object, "lbl_audit_status")
        bar = self.ui.tab_forge.findChild(object, "progressBar_audit")
        
        if lbl_status: lbl_status.setText(message)
        if bar: bar.setValue(percent)

    def on_audit_log(self, text):
        self.add_system_log(f"[AUDITOR] {text}")

    def on_audit_finished(self, success, conflict_dict, total_conflicts):
        if not hasattr(self.ui, "tab_forge"): return
        
        btn_audit = self.ui.tab_forge.findChild(object, "btn_run_audit")
        btn_export = self.ui.tab_forge.findChild(object, "btn_export_audit")
        lbl_status = self.ui.tab_forge.findChild(object, "lbl_audit_status")
        bar = self.ui.tab_forge.findChild(object, "progressBar_audit")
        tree = self.ui.tab_forge.findChild(object, "tree_conflicts")

        if btn_audit:
            btn_audit.setEnabled(True)
            btn_audit.setText("RUN DEEP SCAN")
        if bar: bar.setValue(0)

        if not success:
            if lbl_status: lbl_status.setText("Status: Scan Failed.")
            return

        if total_conflicts == 0:
            if lbl_status:
                lbl_status.setText("Status: Perfect Harmony. No Conflicts Found.")
                lbl_status.setStyleSheet("font-weight: bold; color: #2ecc71;")
            QMessageBox.information(self, "Audit Complete", "Your server is mathematically perfect. 0 XML collisions detected.")
            return

        self.last_audit_results = conflict_dict

        if lbl_status:
            lbl_status.setText(f"Status: {total_conflicts} CRITICAL COLLISIONS DETECTED")
            lbl_status.setStyleSheet("font-weight: bold; color: #e74c3c;")

        if btn_export:
            btn_export.setEnabled(True)
            btn_export.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")

        if tree:
            for file_name, declarations in conflict_dict.items():
                file_node = QTreeWidgetItem(tree)
                file_node.setText(0, file_name)
                file_node.setForeground(0, QColor("#f1c40f"))

                font = file_node.font(0)
                font.setBold(True)
                file_node.setFont(0, font)

                for decl_name, mod_list in declarations.items():
                    decl_node = QTreeWidgetItem(file_node)
                    decl_node.setText(0, f"--> name=\"{decl_name}\"")
                    decl_node.setForeground(0, QColor("#e74c3c"))

                    mods_string = ", ".join(mod_list)
                    decl_node.setText(1, mods_string)
                    decl_node.setForeground(1, QColor("#ecf0f1"))
            
            tree.expandAll()

        QMessageBox.warning(self, "Conflicts Detected", f"Found {total_conflicts} duplicated names across your active mods. \n\nClick 'Export Report' to save this data to a text file.")

    def export_audit_report(self):
        if not self.last_audit_results:
            return

        logs_dir = os.path.join(BASE_DIR, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(logs_dir, f"xpath_conflict_report_{timestamp}.txt")

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("ZERO HOUR ECOSYSTEM: XPATH COLLISION REPORT\n")
                f.write(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                total = 0
                for file_name, declarations in self.last_audit_results.items():
                    f.write(f"[{file_name}]\n")
                    for decl_name, mod_list in declarations.items():
                        f.write(f" Collision -> name=\"{decl_name}\"\n")
                        f.write(f" Injected By: {', '.join(mod_list)}\n\n")
                        total = total + 1
                    f.write("\n")
                f.write(f"TOTAL CONFLICTS: {total}\n")

            self.add_system_log(f"AUDITOR EXPORT SUCCESS: Saved to {report_path}")
            try:
                os.startfile(report_path)
            except Exception:
                pass

        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to write report: {str(e)}")

    def execute_duplicate_scan(self):
        if not self.github or not self.github.token:
            QMessageBox.warning(self, "Cloud Error", "GitHub Engine offline. Check token.")
            return

        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_scan_duplicates")
            self.set_button_busy(btn, "SCANNING CLOUD...")

        manifest_data = get_manifest(state.manifest_path)
        required_folders = list()

        for mod in manifest_data.get("mods", list()):
            f_name = mod.get("folder_name")
            if f_name:
                required_folders.append(f_name)

        self.garbage_worker = CloudGarbageCollector(self.github, required_folders)
        self.garbage_worker.log_signal.connect(self.add_system_log)
        self.garbage_worker.scan_finished_signal.connect(self.on_garbage_scan_finished)
        self.garbage_worker.delete_finished_signal.connect(self.on_garbage_delete_finished)
        self.garbage_worker.start()

    def on_garbage_scan_finished(self, success, orphaned_assets, total_mb):
        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_scan_duplicates")
            if not success or len(orphaned_assets) == 0:
                if btn:
                    btn.setEnabled(True)
                    btn.setText("SCAN FOR\nORPHANED CLOUD ZIPS")
            
        if success:
            if len(orphaned_assets) == 0:
                QMessageBox.information(self, "Scan Complete", "Your GitHub repository is perfectly clean. No orphaned files found.")
                return

            orphan_names = list()
            for o in orphaned_assets:
                orphan_names.append(o.get("name", "Unknown"))

            display_names = ""
            count = 0
            for name in orphan_names:
                if count < 15:
                    display_names = display_names + name + "\n"
                    count = count + 1
                else:
                    break

            if len(orphan_names) > 15:
                display_names = display_names + f"...and {len(orphan_names) - 15} more.\n"

            msg = f"Found {len(orphaned_assets)} orphaned files on GitHub ({total_mb:.2f} MB total).\n\n"
            msg = msg + "These files are NOT in your active Mod List:\n"
            msg = msg + f"{display_names}\n"
            msg = msg + "Do you want to PERMANENTLY delete these files from the cloud?"

            confirm = QMessageBox.question(self, "Cloud Garbage Collector", msg, QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                if btn: self.set_button_busy(btn, "PURGING CLOUD...")
                self.garbage_worker.trigger_purge(orphaned_assets)
            else:
                self.add_system_log("GARBAGE COLLECTOR: Operation cancelled by Admin.")
                if btn:
                    btn.setEnabled(True)
                    btn.setText("SCAN FOR\nORPHANED CLOUD ZIPS")

    def on_garbage_delete_finished(self, purged_count):
        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_scan_duplicates")
            if btn:
                btn.setEnabled(True)
                btn.setText("SCAN FOR\nORPHANED CLOUD ZIPS")
        QMessageBox.information(self, "Cleanup Complete", f"Successfully deleted {purged_count} orphaned files from GitHub.")

    def initiate_mod_install(self):
        if not state.mods_path or not os.path.exists(state.mods_path):
            self.add_system_log("INSTALL ERROR: No Mods folder found. Load a profile first.")
            return

        zip_path, _ = QFileDialog.getOpenFileName(self, "Select Mod Archive", "", "Zip Files (*.zip)")
        if not zip_path:
            return

        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_install_mod")
            if btn:
                btn.setEnabled(False)
                btn.setText("INSTALLING...")

        self.mod_install_worker = ModInstallerWorker(zip_path, state.mods_path)
        self.mod_install_worker.progress_signal.connect(self.add_system_log)
        self.mod_install_worker.finished_signal.connect(self.on_mod_install_complete)
        self.mod_install_worker.start()

    def on_mod_install_complete(self, success, message):
        if hasattr(self.ui, "tab_forge"):
            btn = self.ui.tab_forge.findChild(object, "btn_install_mod")
            if btn:
                btn.setEnabled(True)
                btn.setText("INSTALL MOD FROM .ZIP")

        if success:
            self.add_system_log(f"SUCCESS: {message}")
            self.mod_ctrl.refresh_mod_list()
            self.apply_dirty_ui_state(True)
            QMessageBox.information(self, "Mod Installed", f"{message}\n\nDon't forget to Sync Server to Cloud!")
        else:
            self.add_system_log(f"INSTALL FAILED: {message}")
            QMessageBox.critical(self, "Installation Error", message)

    def start_backup_sequence(self):
        if not state.server_path:
            return

        if hasattr(self.ui, "tab_automation"):
            btn = self.ui.tab_automation.findChild(object, "btn_backup_now")
            lbl = self.ui.tab_automation.findChild(object, "lbl_backup_status")
            if btn:
                btn.setEnabled(False)
                btn.setText("BACKUP IN PROGRESS...")

        self.backup_worker = WorldArchiver(state.server_path)
        
        def update_lbl(msg):
             if hasattr(self.ui, "tab_automation"):
                l = self.ui.tab_automation.findChild(object, "lbl_backup_status")
                if l: l.setText(msg)

        self.backup_worker.progress_signal.connect(update_lbl)
        self.backup_worker.finished_signal.connect(self.on_backup_complete)
        self.backup_worker.start()

    def on_backup_complete(self, success, msg):
        if hasattr(self.ui, "tab_automation"):
            btn = self.ui.tab_automation.findChild(object, "btn_backup_now")
            lbl = self.ui.tab_automation.findChild(object, "lbl_backup_status")
            if btn:
                btn.setEnabled(True)
                btn.setText("EXECUTE WORLD BACKUP")
            if lbl:
                if success:
                    lbl.setText(f"Done: {msg}")
                else:
                    lbl.setText("Backup Failed")

        if success:
            self.add_system_log(f"BACKUP SUCCESS: {msg}")
        else:
            self.add_system_log(f"BACKUP ERROR: {msg}")

    def refresh_player_ledger(self):
        if not hasattr(self, "database"):
            return

        if not hasattr(self.ui, "tab_economy"): return
        table = self.ui.tab_economy.findChild(object, "table_players")
        if not table: return

        raw_data = self.database.fetch_full_ledger()
        table.setRowCount(len(raw_data))

        for row_idx, row_data in enumerate(raw_data):
            p_name = row_data.__getitem__(0)
            p_id = row_data.__getitem__(1)
            p_bucks = row_data.__getitem__(2)
            p_lvl = row_data.__getitem__(3)
            p_kills = row_data.__getitem__(4)
            p_deaths = row_data.__getitem__(5)
            p_seen = row_data.__getitem__(6)

            table.setItem(row_idx, 0, QTableWidgetItem(str(p_name)))
            table.setItem(row_idx, 1, QTableWidgetItem(str(p_id)))
            table.setItem(row_idx, 2, QTableWidgetItem(str(p_bucks)))
            table.setItem(row_idx, 3, QTableWidgetItem(str(p_lvl)))
            table.setItem(row_idx, 4, QTableWidgetItem(str(p_kills)))
            table.setItem(row_idx, 5, QTableWidgetItem(str(p_deaths)))
            table.setItem(row_idx, 6, QTableWidgetItem(str(p_seen)))

    def export_wealth_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Ledger", "player_wealth.csv", "CSV Files (*.csv)")
        if path:
            try:
                raw_data = self.database.fetch_full_ledger()
                headers = list(("Player Name", "Platform ID", "Balance (ZB)", "Level", "Kills", "Deaths", "Last Seen"))

                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(raw_data)

                QMessageBox.information(self, "Success", f"Ledger exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def initiate_atlas_registration(self):
        if not state.current_profile_id or not state.target_repo:
            self.add_system_log("ATLAS ERROR: Profile not fully loaded.")
            return

        if not hasattr(self.ui, "tab_forge"): return
        txt_desc = self.ui.tab_forge.findChild(object, "txt_atlas_desc")
        combo_stat = self.ui.tab_forge.findChild(object, "combo_atlas_status")
        
        desc = txt_desc.text().strip() if txt_desc else "A Paradoxal Server"
        if not desc: desc = "A Paradoxal Server"
        
        stat = combo_stat.currentText() if combo_stat else "ONLINE"

        self.profiles_nexus.update_profile_key(state.current_profile_name, "atlas_description", desc)
        self.profiles_nexus.update_profile_key(state.current_profile_name, "atlas_status", stat)

        manifest_filename = os.path.basename(state.manifest_path)
        from urllib.parse import quote
        safe_filename = quote(manifest_filename)

        raw_url = f"https://raw.githubusercontent.com/{state.target_repo}/main/{safe_filename}"

        public_ip = "127.0.0.1"
        try:
            ip_resp = requests.get("https://api.ipify.org", timeout=5)
            if ip_resp.status_code == 200:
                public_ip = ip_resp.text.strip()
        except Exception as e:
            self.add_system_log(f"IP FETCH WARN: Could not resolve public IP. Defaulting to loopback. ({str(e)})")

        payload = dict()
        payload.update({"display_name": state.current_profile_name})
        payload.update({"manifest_url": raw_url})
        payload.update({"description": desc})
        payload.update({"status": stat})
        payload.update({"ip": public_ip})
        payload.update({"port": state.server_port})
        payload.update({"last_active": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})

        self.pipeline.trigger_atlas_update(dict({"profile_id": state.current_profile_id}), payload)

    def log_system_event(self, message):
        """Central Logging Wrapper"""
        print(f"[SYSTEM] {message}")
        self.add_system_log(message)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        hub = ZeroHourManager()
        hub.show()
        sys.exit(app.exec())
    except Exception:
        print("\n" + "="*60)
        print(" CRITICAL RUNTIME FAILURE DETECTED")
        print("="*60)
        traceback.print_exc()
        print("="*60)
        input(" PRESS ENTER TO EXIT...")
        sys.exit(1)