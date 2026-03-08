# =========================================================
# ZERO HOUR UI: CONFIGURATION TAB - v21.2
# =========================================================
# ROLE: Combines the Initial Server Provisioning (Setup)
#       with the 9-Page ARKASM Server Settings Engine.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 FIX:
# FIX: Attaches widgets to (main_ui.ui) instead of (main_ui).
#      This ensures Logic Engines can find them via attributes.
# FIX: Updated add_setting_row to attach help labels to ui.
# FIX: 100% Bracket-Free payload.
# =========================================================

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QScrollArea,
    QListWidget,
    QStackedWidget,
    QTextEdit
)
from PySide6.QtCore import Qt

class ConfigurationTabBuilder:
    """
    Builds the massive Configuration & Provisioning Tab and binds its
    interactive widgets directly to the main UI Layout instance.
    """

    @staticmethod
    def add_setting_row(ui, grid_layout, row_index, label_text, input_widget, help_attr_name, parent_widget):
        """
        ARKASM Redesign Helper: Automatically builds a perfectly aligned 3-column
        row for Server Settings (Label -> Input -> Description).
        """
        lbl_title = QLabel(label_text, parent_widget)
        lbl_title.setFixedWidth(160)

        input_widget.setFixedWidth(350)

        help_label = QLabel("", parent_widget)
        help_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding-left: 10px;")
        help_label.setWordWrap(True)

        # FIX: Attach the help label to the layout object (ui), not the window
        setattr(ui, help_attr_name, help_label)

        grid_layout.addWidget(lbl_title, row_index, 0)
        grid_layout.addWidget(input_widget, row_index, 1)
        grid_layout.addWidget(help_label, row_index, 2)

        grid_layout.setColumnStretch(2, 1)

    @staticmethod
    def build(main_ui):
        # FIX: Removed (main_ui.centralwidget) argument.
        tab = QWidget()
        
        # CRITICAL BRIDGE: Connect to ZeroHourLayout
        ui = main_ui.ui
        
        h_settings_main = QHBoxLayout(tab)
        h_settings_main.setContentsMargins(0, 0, 0, 0)
        h_settings_main.setSpacing(0)

        # --- LEFT SIDE NAVIGATION MENU ---
        # Note: nav_settings is already defined in admin_layouts.py (Sidebar),
        # but here we might be creating a SUB-navigation or reusing the Sidebar.
        # However, checking the design, this tab has its OWN internal navigation
        # for the 9 pages + Provisioning. 
        # To avoid conflict with the Sidebar 'nav_settings', we should probably
        # call this 'nav_config_pages' or similar. 
        # BUT, to keep compatibility with existing 'admin_layouts', we will attach 
        # it to ui as a new attribute if needed, or just keep it local if logic 
        # doesn't need to control it externally.
        #
        # DECISION: We will attach it to 'ui.nav_config_pages' to be safe,
        # but the logic likely doesn't control this specific list remotely yet.
        
        ui.nav_config_pages = QListWidget(tab)
        ui.nav_config_pages.setFixedWidth(220)
        ui.nav_config_pages.setObjectName("nav_config_pages")

        # Add the Setup/Provisioning as Page 0
        ui.nav_config_pages.addItem("0. Setup & Provisioning")

        # Add the 9 XML Settings Pages
        ui.nav_config_pages.addItem("1. Identity & Web")
        ui.nav_config_pages.addItem("2. Networking & Slots")
        ui.nav_config_pages.addItem("3. Admin & Telnet")
        ui.nav_config_pages.addItem("4. World Generation")
        ui.nav_config_pages.addItem("5. Difficulty & XP")
        ui.nav_config_pages.addItem("6. Rules & Survival")
        ui.nav_config_pages.addItem("7. Zombies & Horde")
        ui.nav_config_pages.addItem("8. Loot & Multi")
        ui.nav_config_pages.addItem("9. Land Claim & Misc")

        h_settings_main.addWidget(ui.nav_config_pages)

        # --- RIGHT SIDE STACKED WIDGET ---
        ui.stack_config_pages = QStackedWidget(tab)
        ui.stack_config_pages.setObjectName("stack_config_pages")
        
        # Connect internal navigation
        ui.nav_config_pages.currentRowChanged.connect(ui.stack_config_pages.setCurrentIndex)

        # -------------------------------------------------------------
        # PAGE 0: SETUP & PROVISIONING (Formerly Tab 3)
        # -------------------------------------------------------------
        p0_scroll = QScrollArea(ui.stack_config_pages)
        p0_scroll.setWidgetResizable(True)
        p0_widget = QWidget()
        v_setup = QVBoxLayout(p0_widget)

        grp_step1 = QGroupBox("STEP 1: IDENTITY & TRAFFIC CONTROL", p0_widget)
        g_step1 = QGridLayout(grp_step1)
        
        ui.txt_prof_name = QLineEdit(grp_step1)
        ui.txt_prof_name.setObjectName("txt_prof_name")
        
        ui.txt_server_port = QLineEdit("26900", grp_step1)
        ui.txt_server_port.setObjectName("txt_server_port")
        
        ui.txt_target_repo = QLineEdit(grp_step1)
        ui.txt_target_repo.setObjectName("txt_target_repo")

        h_validate = QHBoxLayout()
        ui.btn_test_ports = QPushButton("TEST PORTS", grp_step1)
        ui.btn_test_ports.setObjectName("btn_test_ports")
        ui.btn_test_ports.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        
        ui.btn_test_cloud = QPushButton("TEST CLOUD", grp_step1)
        ui.btn_test_cloud.setObjectName("btn_test_cloud")
        ui.btn_test_cloud.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        
        h_validate.addWidget(ui.btn_test_ports)
        h_validate.addWidget(ui.btn_test_cloud)

        ui.btn_save_identity = QPushButton("SAVE IDENTITY", grp_step1)
        ui.btn_save_identity.setObjectName("btn_save_identity")
        ui.btn_save_identity.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        ui.btn_save_identity.setMinimumHeight(35)
        ui.btn_save_identity.setFixedWidth(200)

        g_step1.addWidget(QLabel("Manager Profile Name:", grp_step1), 0, 0)
        g_step1.addWidget(ui.txt_prof_name, 0, 1)
        g_step1.addWidget(QLabel("Server Port:", grp_step1), 1, 0)
        g_step1.addWidget(ui.txt_server_port, 1, 1)
        g_step1.addLayout(h_validate, 1, 2)
        g_step1.addWidget(QLabel("Mod Storage Repository:", grp_step1), 2, 0)
        g_step1.addWidget(ui.txt_target_repo, 2, 1)
        g_step1.addWidget(ui.btn_save_identity, 2, 2)
        g_step1.setColumnStretch(3, 1)
        v_setup.addWidget(grp_step1)

        grp_step2 = QGroupBox("STEP 2: PROVISIONING ENGINE", p0_widget)
        v_step2 = QVBoxLayout(grp_step2)
        
        ui.btn_browse_adopt = QPushButton("ADOPT EXISTING FOLDER", grp_step2)
        ui.btn_browse_adopt.setObjectName("btn_browse_adopt")
        ui.btn_browse_adopt.setMinimumHeight(35)
        
        ui.btn_init_tool = QPushButton("STEP A: INITIALIZE STEAMCMD TOOL", grp_step2)
        ui.btn_init_tool.setObjectName("btn_init_tool")
        ui.btn_init_tool.setMinimumHeight(35)
        
        ui.lbl_tool_status = QLabel("", grp_step2)
        ui.lbl_tool_status.setObjectName("lbl_tool_status")
        ui.lbl_tool_status.setAlignment(Qt.AlignCenter)
        
        ui.btn_deploy_fresh = QPushButton("STEP B: DOWNLOAD 12GB SERVER FILES", grp_step2)
        ui.btn_deploy_fresh.setObjectName("btn_deploy_fresh")
        ui.btn_deploy_fresh.setMinimumHeight(35)

        lbl_deploy_help = QLabel("WARNING: This downloads 12GB of data from Steam. Ensure you have disk space.", grp_step2)
        lbl_deploy_help.setStyleSheet("color: #7f8c8d; font-style: italic;")

        v_step2.addWidget(ui.btn_browse_adopt)
        v_step2.addWidget(ui.btn_init_tool)
        v_step2.addWidget(ui.lbl_tool_status)
        v_step2.addWidget(ui.btn_deploy_fresh)
        v_step2.addWidget(lbl_deploy_help)

        ui.txt_setup_log = QTextEdit(grp_step2)
        ui.txt_setup_log.setObjectName("txt_setup_log")
        ui.txt_setup_log.setStyleSheet("background-color: #000; color: #2ecc71;")
        v_step2.addWidget(ui.txt_setup_log)
        v_setup.addWidget(grp_step2)

        p0_scroll.setWidget(p0_widget)
        ui.stack_config_pages.addWidget(p0_scroll)

        # -------------------------------------------------------------
        # PAGE 1: Identity & Web
        # -------------------------------------------------------------
        p1_scroll = QScrollArea(ui.stack_config_pages)
        p1_scroll.setWidgetResizable(True)
        p1_widget = QWidget()
        v1 = QVBoxLayout(p1_widget)
        g1 = QGridLayout()
        
        ui.txt_ServerName = QLineEdit(p1_widget)
        ui.txt_ServerName.setObjectName("txt_ServerName")
        
        ui.txt_ServerDescription = QLineEdit(p1_widget)
        ui.txt_ServerDescription.setObjectName("txt_ServerDescription")
        
        ui.txt_ServerWebsiteURL = QLineEdit(p1_widget)
        ui.txt_ServerWebsiteURL.setObjectName("txt_ServerWebsiteURL")
        
        ui.txt_ServerPassword = QLineEdit(p1_widget)
        ui.txt_ServerPassword.setObjectName("txt_ServerPassword")
        
        ui.combo_WebDashboardEnabled = QComboBox(p1_widget)
        ui.combo_WebDashboardEnabled.setObjectName("combo_WebDashboardEnabled")
        ui.combo_WebDashboardEnabled.addItems(list(("false", "true")))

        ConfigurationTabBuilder.add_setting_row(ui, g1, 0, "Game Server Name:", ui.txt_ServerName, "lbl_help_ServerName", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 1, "Game Description:", ui.txt_ServerDescription, "lbl_help_ServerDescription", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 2, "Website URL:", ui.txt_ServerWebsiteURL, "lbl_help_ServerWebsiteURL", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 3, "Server Password:", ui.txt_ServerPassword, "lbl_help_ServerPassword", p1_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g1, 4, "Web Dashboard:", ui.combo_WebDashboardEnabled, "lbl_help_WebDashboardEnabled", p1_widget)

        v1.addLayout(g1)
        v1.addStretch()
        p1_scroll.setWidget(p1_widget)
        ui.stack_config_pages.addWidget(p1_scroll)

        # -------------------------------------------------------------
        # PAGE 2: Networking & Slots
        # -------------------------------------------------------------
        p2_scroll = QScrollArea(ui.stack_config_pages)
        p2_scroll.setWidgetResizable(True)
        p2_widget = QWidget()
        v2 = QVBoxLayout(p2_widget)
        g2 = QGridLayout()
        
        ui.txt_ServerPort = QLineEdit(p2_widget)
        ui.txt_ServerPort.setObjectName("txt_ServerPort")
        
        ui.txt_ServerMaxPlayerCount = QLineEdit(p2_widget)
        ui.txt_ServerMaxPlayerCount.setObjectName("txt_ServerMaxPlayerCount")
        
        ui.txt_ServerVisibility = QLineEdit(p2_widget)
        ui.txt_ServerVisibility.setObjectName("txt_ServerVisibility")

        ConfigurationTabBuilder.add_setting_row(ui, g2, 0, "Server Port:", ui.txt_ServerPort, "lbl_help_ServerPort", p2_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g2, 1, "Max Players:", ui.txt_ServerMaxPlayerCount, "lbl_help_ServerMaxPlayerCount", p2_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g2, 2, "Visibility (0-2):", ui.txt_ServerVisibility, "lbl_help_ServerVisibility", p2_widget)

        v2.addLayout(g2)
        v2.addStretch()
        p2_scroll.setWidget(p2_widget)
        ui.stack_config_pages.addWidget(p2_scroll)

        # -------------------------------------------------------------
        # PAGE 3: Admin & Telnet
        # -------------------------------------------------------------
        p3_scroll = QScrollArea(ui.stack_config_pages)
        p3_scroll.setWidgetResizable(True)
        p3_widget = QWidget()
        v3 = QVBoxLayout(p3_widget)
        g3 = QGridLayout()
        
        ui.combo_TelnetEnabled = QComboBox(p3_widget)
        ui.combo_TelnetEnabled.setObjectName("combo_TelnetEnabled")
        ui.combo_TelnetEnabled.addItems(list(("true", "false")))
        
        ui.txt_TelnetPort = QLineEdit(p3_widget)
        ui.txt_TelnetPort.setObjectName("txt_TelnetPort")
        
        ui.txt_TelnetPassword = QLineEdit(p3_widget)
        ui.txt_TelnetPassword.setObjectName("txt_TelnetPassword")
        
        ui.txt_AdminID = QLineEdit(p3_widget)
        ui.txt_AdminID.setObjectName("txt_AdminID")

        ConfigurationTabBuilder.add_setting_row(ui, g3, 0, "Enable Telnet:", ui.combo_TelnetEnabled, "lbl_help_TelnetEnabled", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 1, "Telnet Port:", ui.txt_TelnetPort, "lbl_help_TelnetPort", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 2, "Telnet Password:", ui.txt_TelnetPassword, "lbl_help_TelnetPassword", p3_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g3, 3, "Primary Admin ID:", ui.txt_AdminID, "lbl_help_AdminFileName", p3_widget)

        v3.addLayout(g3)
        v3.addStretch()
        p3_scroll.setWidget(p3_widget)
        ui.stack_config_pages.addWidget(p3_scroll)

        # -------------------------------------------------------------
        # PAGE 4: World Generation
        # -------------------------------------------------------------
        p4_scroll = QScrollArea(ui.stack_config_pages)
        p4_scroll.setWidgetResizable(True)
        p4_widget = QWidget()
        v4 = QVBoxLayout(p4_widget)
        g4 = QGridLayout()
        
        ui.combo_GameWorld = QComboBox(p4_widget)
        ui.combo_GameWorld.setObjectName("combo_GameWorld")
        
        ui.combo_WorldGenName = QComboBox(p4_widget)
        ui.combo_WorldGenName.setObjectName("combo_WorldGenName")
        
        ui.txt_WorldGenSeed = QLineEdit(p4_widget)
        ui.txt_WorldGenSeed.setObjectName("txt_WorldGenSeed")
        
        ui.txt_WorldGenSize = QLineEdit(p4_widget)
        ui.txt_WorldGenSize.setObjectName("txt_WorldGenSize")

        ConfigurationTabBuilder.add_setting_row(ui, g4, 0, "World Type:", ui.combo_GameWorld, "lbl_help_GameWorld", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 1, "Generated World Name:", ui.combo_WorldGenName, "lbl_help_WorldGenName", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 2, "World Gen Seed:", ui.txt_WorldGenSeed, "lbl_help_WorldGenSeed", p4_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g4, 3, "World Gen Size:", ui.txt_WorldGenSize, "lbl_help_WorldGenSize", p4_widget)

        v4.addLayout(g4)
        v4.addStretch()
        p4_scroll.setWidget(p4_widget)
        ui.stack_config_pages.addWidget(p4_scroll)

        # -------------------------------------------------------------
        # PAGE 5: Difficulty & XP
        # -------------------------------------------------------------
        p5_scroll = QScrollArea(ui.stack_config_pages)
        p5_scroll.setWidgetResizable(True)
        p5_widget = QWidget()
        v5 = QVBoxLayout(p5_widget)
        g5 = QGridLayout()
        
        ui.combo_GameDifficulty = QComboBox(p5_widget)
        ui.combo_GameDifficulty.setObjectName("combo_GameDifficulty")
        ui.combo_GameDifficulty.addItems(list(("0","1","2","3","4","5")))
        
        ui.txt_XPMultiplier = QLineEdit(p5_widget)
        ui.txt_XPMultiplier.setObjectName("txt_XPMultiplier")
        
        ui.txt_BlockDamagePlayer = QLineEdit(p5_widget)
        ui.txt_BlockDamagePlayer.setObjectName("txt_BlockDamagePlayer")

        ConfigurationTabBuilder.add_setting_row(ui, g5, 0, "Difficulty (0-5):", ui.combo_GameDifficulty, "lbl_help_GameDifficulty", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 1, "XP Multiplier %:", ui.txt_XPMultiplier, "lbl_help_XPMultiplier", p5_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g5, 2, "Player Block Damage %:", ui.txt_BlockDamagePlayer, "lbl_help_BlockDamagePlayer", p5_widget)

        v5.addLayout(g5)
        v5.addStretch()
        p5_scroll.setWidget(p5_widget)
        ui.stack_config_pages.addWidget(p5_scroll)

        # -------------------------------------------------------------
        # PAGE 6: Rules & Survival
        # -------------------------------------------------------------
        p6_scroll = QScrollArea(ui.stack_config_pages)
        p6_scroll.setWidgetResizable(True)
        p6_widget = QWidget()
        v6 = QVBoxLayout(p6_widget)
        g6 = QGridLayout()
        
        ui.txt_DayNightLength = QLineEdit(p6_widget)
        ui.txt_DayNightLength.setObjectName("txt_DayNightLength")
        
        ui.txt_DayLightLength = QLineEdit(p6_widget)
        ui.txt_DayLightLength.setObjectName("txt_DayLightLength")
        
        ui.combo_DropOnDeath = QComboBox(p6_widget)
        ui.combo_DropOnDeath.setObjectName("combo_DropOnDeath")
        ui.combo_DropOnDeath.addItems(list(("0","1","2","3","4")))

        ConfigurationTabBuilder.add_setting_row(ui, g6, 0, "Day Night Length:", ui.txt_DayNightLength, "lbl_help_DayNightLength", p6_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g6, 1, "Daylight Hours:", ui.txt_DayLightLength, "lbl_help_DayLightLength", p6_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g6, 2, "Drop On Death (0-4):", ui.combo_DropOnDeath, "lbl_help_DropOnDeath", p6_widget)

        v6.addLayout(g6)
        v6.addStretch()
        p6_scroll.setWidget(p6_widget)
        ui.stack_config_pages.addWidget(p6_scroll)

        # -------------------------------------------------------------
        # PAGE 7: Zombies & Horde
        # -------------------------------------------------------------
        p7_scroll = QScrollArea(ui.stack_config_pages)
        p7_scroll.setWidgetResizable(True)
        p7_widget = QWidget()
        v7 = QVBoxLayout(p7_widget)
        g7 = QGridLayout()
        
        ui.txt_MaxSpawnedZombies = QLineEdit(p7_widget)
        ui.txt_MaxSpawnedZombies.setObjectName("txt_MaxSpawnedZombies")
        
        ui.txt_BloodMoonFrequency = QLineEdit(p7_widget)
        ui.txt_BloodMoonFrequency.setObjectName("txt_BloodMoonFrequency")
        
        ui.txt_BloodMoonEnemyCount = QLineEdit(p7_widget)
        ui.txt_BloodMoonEnemyCount.setObjectName("txt_BloodMoonEnemyCount")

        ConfigurationTabBuilder.add_setting_row(ui, g7, 0, "Max Zombies:", ui.txt_MaxSpawnedZombies, "lbl_help_MaxSpawnedZombies", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 1, "Blood Moon Frequency:", ui.txt_BloodMoonFrequency, "lbl_help_BloodMoonFrequency", p7_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g7, 2, "BM Enemy Count/Player:", ui.txt_BloodMoonEnemyCount, "lbl_help_BloodMoonEnemyCount", p7_widget)

        v7.addLayout(g7)
        v7.addStretch()
        p7_scroll.setWidget(p7_widget)
        ui.stack_config_pages.addWidget(p7_scroll)

        # -------------------------------------------------------------
        # PAGE 8: Loot & Multi
        # -------------------------------------------------------------
        p8_scroll = QScrollArea(ui.stack_config_pages)
        p8_scroll.setWidgetResizable(True)
        p8_widget = QWidget()
        v8 = QVBoxLayout(p8_widget)
        g8 = QGridLayout()
        
        ui.txt_LootAbundance = QLineEdit(p8_widget)
        ui.txt_LootAbundance.setObjectName("txt_LootAbundance")
        
        ui.txt_LootRespawnDays = QLineEdit(p8_widget)
        ui.txt_LootRespawnDays.setObjectName("txt_LootRespawnDays")
        
        ui.txt_AirDropFrequency = QLineEdit(p8_widget)
        ui.txt_AirDropFrequency.setObjectName("txt_AirDropFrequency")

        ConfigurationTabBuilder.add_setting_row(ui, g8, 0, "Loot Abundance %:", ui.txt_LootAbundance, "lbl_help_LootAbundance", p8_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g8, 1, "Loot Respawn (Days):", ui.txt_LootRespawnDays, "lbl_help_LootRespawnDays", p8_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g8, 2, "Air Drop (Hours):", ui.txt_AirDropFrequency, "lbl_help_AirDropFrequency", p8_widget)

        v8.addLayout(g8)
        v8.addStretch()
        p8_scroll.setWidget(p8_widget)
        ui.stack_config_pages.addWidget(p8_scroll)

        # -------------------------------------------------------------
        # PAGE 9: Land Claim & Misc
        # -------------------------------------------------------------
        p9_scroll = QScrollArea(ui.stack_config_pages)
        p9_scroll.setWidgetResizable(True)
        p9_widget = QWidget()
        v9 = QVBoxLayout(p9_widget)
        g9 = QGridLayout()
        
        ui.txt_LandClaimCount = QLineEdit(p9_widget)
        ui.txt_LandClaimCount.setObjectName("txt_LandClaimCount")
        
        ui.txt_LandClaimSize = QLineEdit(p9_widget)
        ui.txt_LandClaimSize.setObjectName("txt_LandClaimSize")
        
        ui.combo_EACEnabled = QComboBox(p9_widget)
        ui.combo_EACEnabled.setObjectName("combo_EACEnabled")
        ui.combo_EACEnabled.addItems(list(("false", "true")))

        ui.combo_TwitchServerPermission = QComboBox(p9_widget)
        ui.combo_TwitchServerPermission.setObjectName("combo_TwitchServerPermission")
        ui.combo_TwitchServerPermission.addItems(list(("0", "99")))
        
        ui.combo_DynamicMeshEnabled = QComboBox(p9_widget)
        ui.combo_DynamicMeshEnabled.setObjectName("combo_DynamicMeshEnabled")
        ui.combo_DynamicMeshEnabled.addItems(list(("true", "false")))

        ConfigurationTabBuilder.add_setting_row(ui, g9, 0, "Max Land Claims:", ui.txt_LandClaimCount, "lbl_help_LandClaimCount", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 1, "Land Claim Size:", ui.txt_LandClaimSize, "lbl_help_LandClaimSize", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 2, "Enable EAC:", ui.combo_EACEnabled, "lbl_help_EACEnabled", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 3, "Twitch Permission (0-99):", ui.combo_TwitchServerPermission, "lbl_help_TwitchServerPermission", p9_widget)
        ConfigurationTabBuilder.add_setting_row(ui, g9, 4, "Dynamic Mesh:", ui.combo_DynamicMeshEnabled, "lbl_help_DynamicMeshEnabled", p9_widget)
        
        # Save Button at the end of the last page too, for convenience
        ui.btn_save_srv_settings = QPushButton("COMMIT SETTINGS TO XML")
        ui.btn_save_srv_settings.setObjectName("btn_save_srv_settings")
        ui.btn_save_srv_settings.setStyleSheet("background-color: #d35400; font-weight: bold; height: 40px; margin-top: 20px;")
        ui.btn_save_srv_settings.setCursor(Qt.PointingHandCursor)
        v9.addWidget(ui.btn_save_srv_settings)

        v9.addLayout(g9)
        v9.addStretch()
        p9_scroll.setWidget(p9_widget)
        ui.stack_config_pages.addWidget(p9_scroll)

        # Inject stack into main tab layout
        h_settings_main.addWidget(ui.stack_config_pages)

        return tab