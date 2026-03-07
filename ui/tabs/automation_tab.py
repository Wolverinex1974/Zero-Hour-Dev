# =========================================================
# ZERO HOUR UI: AUTOMATION TAB - v20.8
# =========================================================
# ROLE: Manages Background Tasks (Backups, Auto-Restarts,
#       and Discord Webhooks).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 FIX:
# FIX: Attaches widgets to (main_ui.ui) instead of (main_ui).
#      This ensures Logic Engines can find them via attributes.
# FIX: 100% Bracket-Free payload.
# =========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QFormLayout,
    QTextEdit,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt

class AutomationTabBuilder:
    """
    Builds the Automation & Tasks Tab.
    Handles World Backups, Restart Scheduling, and Webhooks.
    """
    @staticmethod
    def build(main_ui):
        # FIX: Removed (main_ui.centralwidget) argument.
        tab = QWidget()
        
        # CRITICAL BRIDGE: Connect to ZeroHourLayout
        ui = main_ui.ui
        
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # ---------------------------------------------------------
        # SECTION 1: WORLD ARCHIVER (BACKUPS)
        # ---------------------------------------------------------
        grp_backup = QGroupBox("World Archiver Protocol")
        grp_backup.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #3498db; }")
        layout_backup = QVBoxLayout(grp_backup)

        lbl_info = QLabel("Manual or Automated backups of the 'Saves' directory. Zip archives are stored in /Backups/.")
        lbl_info.setStyleSheet("color: #aaa; font-style: italic;")
        layout_backup.addWidget(lbl_info)

        h_backup_ctrl = QHBoxLayout()
        
        ui.btn_backup_now = QPushButton("EXECUTE WORLD BACKUP")
        ui.btn_backup_now.setObjectName("btn_backup_now")
        ui.btn_backup_now.setMinimumHeight(40)
        ui.btn_backup_now.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        ui.chk_auto_backup = QCheckBox("Enable Auto-Backup (Every 60 Minutes)")
        ui.chk_auto_backup.setObjectName("chk_auto_backup")
        ui.chk_auto_backup.setChecked(True)

        h_backup_ctrl.addWidget(ui.btn_backup_now)
        h_backup_ctrl.addWidget(ui.chk_auto_backup)
        
        layout_backup.addLayout(h_backup_ctrl)

        ui.lbl_backup_status = QLabel("Status: Archiver Idle")
        ui.lbl_backup_status.setObjectName("lbl_backup_status")
        ui.lbl_backup_status.setAlignment(Qt.AlignCenter)
        ui.lbl_backup_status.setStyleSheet("color: #3498db; font-weight: bold;")
        layout_backup.addWidget(ui.lbl_backup_status)

        main_layout.addWidget(grp_backup)

        # ---------------------------------------------------------
        # SECTION 2: WATCHDOG & RESTART SCHEDULER
        # ---------------------------------------------------------
        grp_watchdog = QGroupBox("Watchdog & Auto-Restart")
        grp_watchdog.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #e74c3c; }")
        layout_watchdog = QFormLayout(grp_watchdog)

        ui.chk_enable_watchdog = QCheckBox("Enable Crash Detection (Restart on Crash)")
        ui.chk_enable_watchdog.setObjectName("chk_enable_watchdog")
        ui.chk_enable_watchdog.setChecked(True)
        
        ui.spin_restart_interval = QSpinBox()
        ui.spin_restart_interval.setObjectName("spin_restart_interval")
        ui.spin_restart_interval.setRange(0, 24)
        ui.spin_restart_interval.setValue(6)
        ui.spin_restart_interval.setSuffix(" Hours")
        
        ui.chk_announce_restart = QCheckBox("Announce Restart in Chat (10m, 5m, 1m warnings)")
        ui.chk_announce_restart.setObjectName("chk_announce_restart")
        ui.chk_announce_restart.setChecked(True)

        layout_watchdog.addRow("Process Monitor:", ui.chk_enable_watchdog)
        layout_watchdog.addRow("Scheduled Restart Every:", ui.spin_restart_interval)
        layout_watchdog.addRow("Chat Notifications:", ui.chk_announce_restart)

        main_layout.addWidget(grp_watchdog)

        # ---------------------------------------------------------
        # SECTION 3: DISCORD WEBHOOKS
        # ---------------------------------------------------------
        grp_discord = QGroupBox("Discord Integration (Webhooks)")
        grp_discord.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #7289da; }")
        layout_discord = QVBoxLayout(grp_discord)

        h_webhook = QHBoxLayout()
        ui.txt_webhook_url = QLineEdit()
        ui.txt_webhook_url.setObjectName("txt_webhook_url")
        ui.txt_webhook_url.setPlaceholderText("https://discord.com/api/webhooks/...")
        
        ui.btn_test_webhook = QPushButton("TEST PAYLOAD")
        ui.btn_test_webhook.setObjectName("btn_test_webhook")
        ui.btn_test_webhook.setStyleSheet("background-color: #7289da; color: white;")

        h_webhook.addWidget(QLabel("Webhook URL:"))
        h_webhook.addWidget(ui.txt_webhook_url)
        h_webhook.addWidget(ui.btn_test_webhook)
        
        layout_discord.addLayout(h_webhook)

        # Event Toggles
        h_events = QHBoxLayout()
        ui.chk_discord_chat = QCheckBox("Bridge Chat")
        ui.chk_discord_chat.setObjectName("chk_discord_chat")
        
        ui.chk_discord_joins = QCheckBox("Player Joins/Leaves")
        ui.chk_discord_joins.setObjectName("chk_discord_joins")
        
        ui.chk_discord_system = QCheckBox("Server Status")
        ui.chk_discord_system.setObjectName("chk_discord_system")
        
        h_events.addWidget(ui.chk_discord_chat)
        h_events.addWidget(ui.chk_discord_joins)
        h_events.addWidget(ui.chk_discord_system)
        
        layout_discord.addLayout(h_events)

        main_layout.addWidget(grp_discord)

        # Spacer to push content up
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(vertical_spacer)
        
        return tab