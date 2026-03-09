# ==============================================================================
# ZERO HOUR UI: CONFIGURATION TAB - v23.2
# ==============================================================================
# ROLE: The Setup Wizard & XML Editor.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 22 UPDATE (MERGE & REPAIR):
# FIX: RESTORED the 9-Page XML Editor (Pages 1-9) previously deleted.
# FIX: APPLIED layout improvements (Expanding widths, Tooltips) to Page 0.
# FIX: Wired up 'nav_config_pages' to 'stack_config_pages' for navigation.
# ==============================================================================

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QFrame, 
    QScrollArea,
    QSizePolicy,
    QGridLayout,
    QGroupBox,
    QListWidget,
    QStackedWidget,
    QComboBox,
    QTextEdit
)
from PySide6.QtCore import Qt

class ConfigurationTabBuilder:
    """
    Builds the massive Configuration Tab containing:
    1. The 'Setup & Provisioning' Wizard (Page 0)
    2. The 9-Page XML Server Settings Editor (Pages 1-9)
    """

    @staticmethod
    def add_setting_row(ui, grid_layout, row_index, label_text, input_widget, help_attr_name, parent_widget):
        """
        Helper: Builds a perfectly aligned 3-column row for XML Settings.
        (Label -> Input -> Description)
        """
        lbl_title = QLabel(label_text, parent_widget)
        lbl_title.setFixedWidth(160)
        lbl_title.setStyleSheet("color: #ccc;")

        # Ensure inputs act consistently
        input_widget.setMinimumWidth(250)
        input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        help_label = QLabel("", parent_widget)
        help_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding-left: 10px;")
        help_label.setWordWrap(True)

        # Attach help label to the layout object (ui) so Logic can update it
        setattr(ui, help_attr_name, help_label)

        grid_layout.addWidget(lbl_title, row_index, 0)
        grid_layout.addWidget(input_widget, row_index, 1)
        grid_layout.addWidget(help_label, row_index, 2)

        # Give description column the most space
        grid_layout.setColumnStretch(2, 1)

    @staticmethod
    def build(main_ui):
        """
        Constructs the Tab.
        :param main_ui: Reference to the Main Window (holds the .ui namespace)
        """
        tab = QWidget()
        tab.setObjectName("tab_configuration")
        ui = main_ui.ui
        
        # Main Horizontal Layout (Splitter logic)
        h_main = QHBoxLayout(tab)
        h_main.setContentsMargins(0, 0, 0, 0)
        h_main.setSpacing(0)

        # -------------------------------------------------------------
        # LEFT SIDE: NAVIGATION MENU
        # -------------------------------------------------------------
        ui.nav_config_pages = QListWidget(tab)
        ui.nav_config_pages.setObjectName("nav_config_pages")
        ui.nav_config_pages.setFixedWidth(240)
        ui.nav_config_pages.setStyleSheet("""
            QListWidget { background-color: #111; border-right: 1px solid #333; font-size: 13px; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #222; }
            QListWidget::item:selected { background-color: #00A8E8; color: black; font-weight: bold; border-left: 4px solid white; }
            QListWidget::item:hover { background-color: #222; }
        """)

        # Populate Menu
        pages = [
            "0. Setup & Provisioning",
            "1. Identity & Web",
            "2. Networking & Slots",
            "3. Admin & Telnet",
            "4. World Generation",
            "5. Difficulty & XP",
            "6. Rules & Survival",
            "7. Zombies & Horde",
            "8. Loot & Multi",
            "9. Land Claim & Misc"
        ]
        for p in pages:
            ui.nav_config_pages.addItem(p)

        h_main.addWidget(ui.nav_config_pages)

        # -------------------------------------------------------------
        # RIGHT SIDE: CONTENT STACK
        # -------------------------------------------------------------
        ui.stack_config_pages = QStackedWidget(tab)
        ui.stack_config_pages.setObjectName("stack_config_pages")
        
        # Connect navigation logic (handled in Logic/Router usually, but wired here for UI responsiveness)
        ui.nav_config_pages.currentRowChanged.connect(ui.stack_config_pages.setCurrentIndex)

        # =============================================================
        # PAGE 0: SETUP & PROVISIONING (The Fixed Layout)
        # =============================================================
        p0_scroll = QScrollArea()
        p0_scroll.setWidgetResizable(True)
        p0_widget = QWidget()
        v_setup = QVBoxLayout(p0_widget)
        v_setup.setContentsMargins(20, 20, 20, 20)
        v_setup.setSpacing(20)

        # --- GROUP 1: IDENTITY ---
        grp_identity = QGroupBox("STEP 1: IDENTITY TRAFFIC CONTROL")
        grp_identity.setStyleSheet("QGroupBox { border: 1px solid #333; font-weight: bold; color: #00A8E8; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        g_identity = QGridLayout(grp_identity)
        g_identity.setVerticalSpacing(15)

        # Name
        lbl_name = QLabel("Manager Profile Name:")
        lbl_name.setToolTip("Unique name for this server instance.")
        ui.txt_prof_name = QLineEdit()
        ui.txt_prof_name.setObjectName("txt_prof_name")
        ui.txt_prof_name.setPlaceholderText("e.g. My_Survival_Server")
        ui.txt_prof_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        g_identity.addWidget(lbl_name, 0, 0)
        g_identity.addWidget(ui.txt_prof_name, 0, 1, 1, 3)

        # Port
        lbl_port = QLabel("Server Port:")
        lbl_port.setToolTip("Default 26900 (TCP/UDP). Ensure Firewall allows this +2.")
        ui.txt_server_port = QLineEdit()
        ui.txt_server_port.setObjectName("txt_server_port")
        ui.txt_server_port.setPlaceholderText("26900")
        
        ui.btn_test_ports = QPushButton("TEST PORTS")
        ui.btn_test_ports.setObjectName("btn_test_ports")
        ui.btn_test_cloud = QPushButton("TEST CLOUD")
        ui.btn_test_cloud.setObjectName("btn_test_cloud")

        g_identity.addWidget(lbl_port, 1, 0)
        g_identity.addWidget(ui.txt_server_port, 1, 1)
        g_identity.addWidget(ui.btn_test_ports, 1, 2)
        g_identity.addWidget(ui.btn_test_cloud, 1, 3)

        # Repo
        lbl_repo = QLabel("Mod Storage Repository:")
        lbl_repo.setToolTip("GitHub 'User/Repo' for syncing mods.")
        ui.txt_target_repo = QLineEdit()
        ui.txt_target_repo.setObjectName("txt_target_repo")
        ui.txt_target_repo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        ui.btn_save_identity = QPushButton("SAVE IDENTITY")
        ui.btn_save_identity.setObjectName("btn_save_identity")
        ui.btn_save_identity.setCursor(Qt.CursorShape.PointingHandCursor)
        ui.btn_save_identity.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        ui.btn_save_identity.setToolTip("Writes settings to disk (Persistence).")

        g_identity.addWidget(lbl_repo, 2, 0)
        g_identity.addWidget(ui.txt_target_repo, 2, 1, 1, 2)
        g_identity.addWidget(ui.btn_save_identity, 2, 3)

        v_setup.addWidget(grp_identity)

        # --- GROUP 2: PROVISIONING ---
        grp_provision = QGroupBox("STEP 2: PROVISIONING ENGINE")
        grp_provision.setStyleSheet("QGroupBox { border: 1px solid #333; font-weight: bold; color: #00A8E8; margin-top: 10px; }")
        v_provision = QVBoxLayout(grp_provision)
        v_provision.setSpacing(10)

        ui.btn_browse_adopt = QPushButton("ADOPT EXISTING FOLDER")
        ui.btn_browse_adopt.setObjectName("btn_browse_adopt")
        ui.btn_browse_adopt.setToolTip("Choose a folder that already contains 7DaysToDieServer.exe")
        ui.btn_browse_adopt.setMinimumHeight(40)
        
        ui.btn_init_tool = QPushButton("STEP A: INITIALIZE STEAMCMD TOOL")
        ui.btn_init_tool.setObjectName("btn_init_tool")
        ui.btn_init_tool.setToolTip("Download & Install SteamCMD Engine from Valve.")
        ui.btn_init_tool.setMinimumHeight(40)
        
        ui.btn_deploy_fresh = QPushButton("STEP B: DOWNLOAD 12GB SERVER FILES")
        ui.btn_deploy_fresh.setObjectName("btn_deploy_fresh")
        ui.btn_deploy_fresh.setToolTip("Use SteamCMD to download the Dedicated Server.")
        ui.btn_deploy_fresh.setMinimumHeight(40)
        
        # Log area for SteamCMD output
        ui.txt_setup_log = QTextEdit()
        ui.txt_setup_log.setObjectName("txt_setup_log")
        ui.txt_setup_log.setMaximumHeight(150)
        ui.txt_setup_log.setPlaceholderText("SteamCMD Output will appear here...")
        ui.txt_setup_log.setStyleSheet("background-color: #000; color: #2ecc71; font-family: Consolas;")

        v_provision.addWidget(ui.btn_browse_adopt)
        v_provision.addWidget(ui.btn_init_tool)
        v_provision.addWidget(ui.btn_deploy_fresh)
        v_provision.addWidget(ui.txt_setup_log)
        
        v_setup.addWidget(grp_provision)
        v_setup.addStretch()

        p0_scroll.setWidget(p0_widget)
        ui.stack_config_pages.addWidget(p0_scroll)

        # =============================================================
        # PAGE 1: Identity & Web
        # =============================================================
        p1_scroll = QScrollArea()
        p1_scroll.setWidgetResizable(True)
        p1_widget = QWidget()
        v1 = QVBoxLayout(p1_widget)
        g1 = QGridLayout()
        
        ui.txt_ServerName = QLineEdit()
        ui.txt_ServerName.setObjectName("txt_ServerName")
        ui.txt_ServerDescription = QLineEdit()
        ui.txt_ServerDescription.setObjectName("txt_ServerDescription")
        ui.txt_ServerWebsiteURL = QLineEdit()
        ui.txt_ServerWebsiteURL.setObjectName("txt_ServerWebsiteURL")
        ui.txt_ServerPassword = QLineEdit()
        ui.txt_ServerPassword.setObjectName("txt_ServerPassword")
        ui.combo_WebDashboardEnabled = QComboBox()
        ui.combo_WebDashboardEnabled.setObjectName("combo_WebDashboardEnabled")
        ui.combo_WebDashboardEnabled.addItems(["false", "true"])

        ConfigurationTabBuilder.add_setting_row(ui, g1, 0, "Game Server Name:", ui.txt_ServerName, "lbl_help_ServerName", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 1, "Game Description:", ui.txt_ServerDescription, "lbl_help_ServerDescription", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 2, "Website URL:", ui.txt_ServerWebsiteURL, "lbl_help_ServerWebsiteURL", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 3, "Server Password:", ui.txt_ServerPassword, "lbl_help_ServerPassword", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 4, "Web Dashboard:", ui.combo_WebDashboardEnabled, "lbl_help_WebDashboardEnabled", p1_widget)

        v1.addLayout(g1)
        v1.addStretch()
        p1_scroll.setWidget(p1_widget)
        ui.stack_config_pages.addWidget(p1_scroll)

        # =============================================================
        # PAGE 2: Networking & Slots
        # =============================================================
        p2_scroll = QScrollArea()
        p2_scroll.setWidgetResizable(True)
        p2_widget = QWidget()
        v2 = QVBoxLayout(p2_widget)
        g2 = QGridLayout()

        ui.txt_ServerPort = QLineEdit()
        ui.txt_ServerPort.setObjectName("txt_ServerPort")
        ui.combo_ServerVisibility = QComboBox()
        ui.combo_ServerVisibility.setObjectName("combo_ServerVisibility")
        ui.combo_ServerVisibility.addItems(["2", "1", "0"]) # Public, Friends, Private
        ui.txt_ServerMaxPlayerCount = QLineEdit()
        ui.txt_ServerMaxPlayerCount.setObjectName("txt_ServerMaxPlayerCount")
        ui.txt_ServerReservedSlots = QLineEdit()
        ui.txt_ServerReservedSlots.setObjectName("txt_ServerReservedSlots")

        ConfigurationTabBuilder.add_setting_row(ui, g2, 0, "Server Port:", ui.txt_ServerPort, "lbl_help_ServerPort", p2_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g2, 1, "Visibility:", ui.combo_ServerVisibility, "lbl_help_ServerVisibility", p2_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g2, 2, "Max Players:", ui.txt_ServerMaxPlayerCount, "lbl_help_ServerMaxPlayerCount", p2_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g2, 3, "Reserved Slots:", ui.txt_ServerReservedSlots, "lbl_help_ServerReservedSlots", p2_widget)

        v2.addLayout(g2)
        v2.addStretch()
        p2_scroll.setWidget(p2_widget)
        ui.stack_config_pages.addWidget(p2_scroll)

        # =============================================================
        # PAGE 3: Admin & Telnet
        # =============================================================
        p3_scroll = QScrollArea()
        p3_scroll.setWidgetResizable(True)
        p3_widget = QWidget()
        v3 = QVBoxLayout(p3_widget)
        g3 = QGridLayout()

        ui.combo_TelnetEnabled = QComboBox()
        ui.combo_TelnetEnabled.setObjectName("combo_TelnetEnabled")
        ui.combo_TelnetEnabled.addItems(["true", "false"])
        ui.txt_TelnetPort = QLineEdit()
        ui.txt_TelnetPort.setObjectName("txt_TelnetPort")
        ui.txt_TelnetPassword = QLineEdit()
        ui.txt_TelnetPassword.setObjectName("txt_TelnetPassword")
        ui.txt_AdminFileName = QLineEdit()
        ui.txt_AdminFileName.setObjectName("txt_AdminFileName")
        ui.txt_UserDataFolder = QLineEdit()
        ui.txt_UserDataFolder.setObjectName("txt_UserDataFolder")

        ConfigurationTabBuilder.add_setting_row(ui, g3, 0, "Enable Telnet:", ui.combo_TelnetEnabled, "lbl_help_TelnetEnabled", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 1, "Telnet Port:", ui.txt_TelnetPort, "lbl_help_TelnetPort", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 2, "Telnet Password:", ui.txt_TelnetPassword, "lbl_help_TelnetPassword", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 3, "Admin File:", ui.txt_AdminFileName, "lbl_help_AdminFileName", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 4, "User Data Folder:", ui.txt_UserDataFolder, "lbl_help_UserDataFolder", p3_widget)

        v3.addLayout(g3)
        v3.addStretch()
        p3_scroll.setWidget(p3_widget)
        ui.stack_config_pages.addWidget(p3_scroll)

        # =============================================================
        # PAGE 4: World Generation
        # =============================================================
        p4_scroll = QScrollArea()
        p4_scroll.setWidgetResizable(True)
        p4_widget = QWidget()
        v4 = QVBoxLayout(p4_widget)
        g4 = QGridLayout()

        ui.txt_GameWorld = QLineEdit()
        ui.txt_GameWorld.setObjectName("txt_GameWorld")
        ui.txt_WorldGenSize = QLineEdit()
        ui.txt_WorldGenSize.setObjectName("txt_WorldGenSize")
        ui.txt_WorldGenSeed = QLineEdit()
        ui.txt_WorldGenSeed.setObjectName("txt_WorldGenSeed")
        ui.txt_GameName = QLineEdit()
        ui.txt_GameName.setObjectName("txt_GameName")
        ui.txt_GameMode = QLineEdit()
        ui.txt_GameMode.setObjectName("txt_GameMode")

        ConfigurationTabBuilder.add_setting_row(ui, g4, 0, "Game World:", ui.txt_GameWorld, "lbl_help_GameWorld", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 1, "World Size:", ui.txt_WorldGenSize, "lbl_help_WorldGenSize", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 2, "Gen Seed:", ui.txt_WorldGenSeed, "lbl_help_WorldGenSeed", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 3, "Game Name (Save):", ui.txt_GameName, "lbl_help_GameName", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 4, "Game Mode:", ui.txt_GameMode, "lbl_help_GameMode", p4_widget)

        v4.addLayout(g4)
        v4.addStretch()
        p4_scroll.setWidget(p4_widget)
        ui.stack_config_pages.addWidget(p4_scroll)

        # =============================================================
        # PAGE 5: Difficulty & XP
        # =============================================================
        p5_scroll = QScrollArea()
        p5_scroll.setWidgetResizable(True)
        p5_widget = QWidget()
        v5 = QVBoxLayout(p5_widget)
        g5 = QGridLayout()

        ui.txt_GameDifficulty = QLineEdit()
        ui.txt_GameDifficulty.setObjectName("txt_GameDifficulty")
        ui.txt_DayNightLength = QLineEdit()
        ui.txt_DayNightLength.setObjectName("txt_DayNightLength")
        ui.txt_DayLightLength = QLineEdit()
        ui.txt_DayLightLength.setObjectName("txt_DayLightLength")
        ui.txt_XPMultiplier = QLineEdit()
        ui.txt_XPMultiplier.setObjectName("txt_XPMultiplier")
        ui.txt_BlockDamagePlayer = QLineEdit()
        ui.txt_BlockDamagePlayer.setObjectName("txt_BlockDamagePlayer")

        ConfigurationTabBuilder.add_setting_row(ui, g5, 0, "Difficulty (0-5):", ui.txt_GameDifficulty, "lbl_help_GameDifficulty", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 1, "Day/Night Length:", ui.txt_DayNightLength, "lbl_help_DayNightLength", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 2, "Daylight Hours:", ui.txt_DayLightLength, "lbl_help_DayLightLength", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 3, "XP Multiplier:", ui.txt_XPMultiplier, "lbl_help_XPMultiplier", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 4, "Player Block Dmg:", ui.txt_BlockDamagePlayer, "lbl_help_BlockDamagePlayer", p5_widget)

        v5.addLayout(g5)
        v5.addStretch()
        p5_scroll.setWidget(p5_widget)
        ui.stack_config_pages.addWidget(p5_scroll)

        # =============================================================
        # PAGE 6: Rules & Survival
        # =============================================================
        p6_scroll = QScrollArea()
        p6_scroll.setWidgetResizable(True)
        p6_widget = QWidget()
        v6 = QVBoxLayout(p6_widget)
        g6 = QGridLayout()

        ui.combo_DropOnDeath = QComboBox()
        ui.combo_DropOnDeath.setObjectName("combo_DropOnDeath")
        ui.combo_DropOnDeath.addItems(["0", "1", "2", "3"])
        ui.combo_DropOnQuit = QComboBox()
        ui.combo_DropOnQuit.setObjectName("combo_DropOnQuit")
        ui.combo_DropOnQuit.addItems(["0", "1", "2", "3"])
        ui.combo_PlayerKillingMode = QComboBox()
        ui.combo_PlayerKillingMode.setObjectName("combo_PlayerKillingMode")
        ui.combo_PlayerKillingMode.addItems(["0", "1", "2", "3"])
        ui.txt_BloodMoonFrequency = QLineEdit()
        ui.txt_BloodMoonFrequency.setObjectName("txt_BloodMoonFrequency")

        ConfigurationTabBuilder.add_setting_row(ui, g6, 0, "Drop On Death:", ui.combo_DropOnDeath, "lbl_help_DropOnDeath", p6_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g6, 1, "Drop On Quit:", ui.combo_DropOnQuit, "lbl_help_DropOnQuit", p6_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g6, 2, "Player Killing:", ui.combo_PlayerKillingMode, "lbl_help_PlayerKillingMode", p6_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g6, 3, "Blood Moon Freq:", ui.txt_BloodMoonFrequency, "lbl_help_BloodMoonFrequency", p6_widget)

        v6.addLayout(g6)
        v6.addStretch()
        p6_scroll.setWidget(p6_widget)
        ui.stack_config_pages.addWidget(p6_scroll)

        # =============================================================
        # PAGE 7: Zombies & Horde
        # =============================================================
        p7_scroll = QScrollArea()
        p7_scroll.setWidgetResizable(True)
        p7_widget = QWidget()
        v7 = QVBoxLayout(p7_widget)
        g7 = QGridLayout()

        ui.combo_EnemySpawnMode = QComboBox()
        ui.combo_EnemySpawnMode.setObjectName("combo_EnemySpawnMode")
        ui.combo_EnemySpawnMode.addItems(["true", "false"])
        ui.txt_BloodMoonEnemyCount = QLineEdit()
        ui.txt_BloodMoonEnemyCount.setObjectName("txt_BloodMoonEnemyCount")
        ui.combo_ZombieMove = QComboBox()
        ui.combo_ZombieMove.setObjectName("combo_ZombieMove")
        ui.combo_ZombieMove.addItems(["0", "1", "2", "3", "4"])
        ui.combo_ZombieMoveNight = QComboBox()
        ui.combo_ZombieMoveNight.setObjectName("combo_ZombieMoveNight")
        ui.combo_ZombieMoveNight.addItems(["0", "1", "2", "3", "4"])
        ui.combo_ZombieFeralMove = QComboBox()
        ui.combo_ZombieFeralMove.setObjectName("combo_ZombieFeralMove")
        ui.combo_ZombieFeralMove.addItems(["0", "1", "2", "3", "4"])

        ConfigurationTabBuilder.add_setting_row(ui, g7, 0, "Enemy Spawning:", ui.combo_EnemySpawnMode, "lbl_help_EnemySpawnMode", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 1, "Blood Moon Count:", ui.txt_BloodMoonEnemyCount, "lbl_help_BloodMoonEnemyCount", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 2, "Zombie Move:", ui.combo_ZombieMove, "lbl_help_ZombieMove", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 3, "Zombie Night Move:", ui.combo_ZombieMoveNight, "lbl_help_ZombieMoveNight", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 4, "Feral Move:", ui.combo_ZombieFeralMove, "lbl_help_ZombieFeralMove", p7_widget)

        v7.addLayout(g7)
        v7.addStretch()
        p7_scroll.setWidget(p7_widget)
        ui.stack_config_pages.addWidget(p7_scroll)

        # =============================================================
        # PAGE 8: Loot & Multipliers
        # =============================================================
        p8_scroll = QScrollArea()
        p8_scroll.setWidgetResizable(True)
        p8_widget = QWidget()
        v8 = QVBoxLayout(p8_widget)
        g8 = QGridLayout()

        ui.txt_LootAbundance = QLineEdit()
        ui.txt_LootAbundance.setObjectName("txt_LootAbundance")
        ui.txt_LootRespawnDays = QLineEdit()
        ui.txt_LootRespawnDays.setObjectName("txt_LootRespawnDays")
        ui.txt_AirDropFrequency = QLineEdit()
        ui.txt_AirDropFrequency.setObjectName("txt_AirDropFrequency")
        ui.txt_PartySharedKillRange = QLineEdit()
        ui.txt_PartySharedKillRange.setObjectName("txt_PartySharedKillRange")
        
        ConfigurationTabBuilder.add_setting_row(ui, g8, 0, "Loot Abundance:", ui.txt_LootAbundance, "lbl_help_LootAbundance", p8_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g8, 1, "Respawn Days:", ui.txt_LootRespawnDays, "lbl_help_LootRespawnDays", p8_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g8, 2, "Airdrop Freq:", ui.txt_AirDropFrequency, "lbl_help_AirDropFrequency", p8_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g8, 3, "Party Kill Range:", ui.txt_PartySharedKillRange, "lbl_help_PartySharedKillRange", p8_widget)

        v8.addLayout(g8)
        v8.addStretch()
        p8_scroll.setWidget(p8_widget)
        ui.stack_config_pages.addWidget(p8_scroll)

        # =============================================================
        # PAGE 9: Land Claim & Misc
        # =============================================================
        p9_scroll = QScrollArea()
        p9_scroll.setWidgetResizable(True)
        p9_widget = QWidget()
        v9 = QVBoxLayout(p9_widget)
        g9 = QGridLayout()

        ui.txt_LandClaimSize = QLineEdit()
        ui.txt_LandClaimSize.setObjectName("txt_LandClaimSize")
        ui.txt_LandClaimDeadZone = QLineEdit()
        ui.txt_LandClaimDeadZone.setObjectName("txt_LandClaimDeadZone")
        ui.txt_LandClaimExpiryTime = QLineEdit()
        ui.txt_LandClaimExpiryTime.setObjectName("txt_LandClaimExpiryTime")
        ui.combo_EACEnabled = QComboBox()
        ui.combo_EACEnabled.setObjectName("combo_EACEnabled")
        ui.combo_EACEnabled.addItems(["true", "false"])

        ConfigurationTabBuilder.add_setting_row(ui, g9, 0, "Claim Size:", ui.txt_LandClaimSize, "lbl_help_LandClaimSize", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 1, "Claim Deadzone:", ui.txt_LandClaimDeadZone, "lbl_help_LandClaimDeadZone", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 2, "Expiry Days:", ui.txt_LandClaimExpiryTime, "lbl_help_LandClaimExpiryTime", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 3, "EAC Enabled:", ui.combo_EACEnabled, "lbl_help_EACEnabled", p9_widget)

        v9.addLayout(g9)
        v9.addStretch()
        p9_scroll.setWidget(p9_widget)
        ui.stack_config_pages.addWidget(p9_scroll)

        # =============================================================
        # FINAL ASSEMBLY
        # =============================================================
        # Add the Navigation + Content Stack to the Main HBox
        h_main.addWidget(ui.stack_config_pages)
        
        # Add Action Bar at bottom (Always Visible)
        ui.btn_save_srv_settings = QPushButton("COMMIT SETTINGS TO XML")
        ui.btn_save_srv_settings.setObjectName("btn_save_srv_settings")
        ui.btn_save_srv_settings.setMinimumHeight(45)
        ui.btn_save_srv_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        ui.btn_save_srv_settings.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; border-top: 2px solid #333;")
        
        # We need a wrapping layout to include the button at the bottom
        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addLayout(h_main)
        final_layout.addWidget(ui.btn_save_srv_settings)
        
        # Re-parent the layout to the tab
        # Note: We used h_main initially on 'tab', so we need to be careful.
        # Better strategy: Create a holder widget for h_main
        holder_widget = QWidget()
        holder_widget.setLayout(h_main)
        
        real_main_layout = QVBoxLayout(tab)
        real_main_layout.setContentsMargins(0, 0, 0, 0)
        real_main_layout.addWidget(holder_widget)
        real_main_layout.addWidget(ui.btn_save_srv_settings)

        return tab