# ==============================================================================
# ZERO HOUR UI: CONFIGURATION TAB BUILDER - v23.2
# ==============================================================================
# ROLE: Constructs the 9-Page Server Settings and Provisioning UI.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE: 
# FIX: Restored full 532-line XML layout builder.
# FIX: Forced dark-mode CSS on QScrollArea, QWidget, and QGroupBoxes to 
#      eliminate the white background glitch.
# ==============================================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QStackedWidget, QScrollArea, QGroupBox, QLabel, QLineEdit, QPushButton, QGridLayout, QTextEdit
from PySide6.QtCore import Qt

class ConfigurationTabBuilder:
    @staticmethod
    def build(ui):
        tab = QWidget()
        
        # --- Base Splitter Layout ---
        h_main = QHBoxLayout()
        h_main.setContentsMargins(0, 0, 0, 0)
        h_main.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #333333; }")
        
        # --- Left Sidebar Menu ---
        sidebar = QListWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border-right: 2px solid #333333;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #0099ff;
                color: #ffffff;
                font-weight: bold;
                border-left: 5px solid #0055ff;
            }
            QListWidget::item:hover:!selected {
                background-color: #2a2a2a;
            }
        """)
        
        menu_items = list((
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
        ))
        
        for item_name in menu_items:
            sidebar.addItem(item_name)
            
        # --- Right Content Area ---
        stack = QStackedWidget()
        stack.setStyleSheet("""
            QStackedWidget {
                background-color: #252526;
            }
        """)
        
        # ---------------------------------------------------------
        # Helper: Create standard setting row
        # ---------------------------------------------------------
        def add_setting_row(grid, row, label_text, var_name, default_val=""):
            lbl = QLabel(label_text + ":")
            lbl.setStyleSheet("color: #e0e0e0;")
            
            txt = QLineEdit()
            txt.setText(str(default_val))
            txt.setStyleSheet("""
                QLineEdit {
                    background-color: #000000;
                    color: #00ffcc;
                    border: 1px solid #555555;
                    padding: 5px;
                }
            """)
            
            # Store reference in main UI object
            setattr(ui, var_name, txt)
            
            grid.addWidget(lbl, row, 0)
            grid.addWidget(txt, row, 1)

        # ---------------------------------------------------------
        # PAGE 0: Setup & Provisioning
        # ---------------------------------------------------------
        page_setup = QWidget()
        page_setup.setStyleSheet("background-color: #252526;")
        setup_layout = QVBoxLayout(page_setup)
        setup_layout.setContentsMargins(20, 20, 20, 20)
        setup_layout.setSpacing(15)

        # -- Identity Group --
        grp_identity = QGroupBox("STEP 1: IDENTITY TRAFFIC CONTROL")
        grp_identity.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 1px solid #444444;
                margin-top: 15px;
                color: #00ffcc;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #121212;
            }
            QLabel { color: #e0e0e0; }
        """)
        id_layout = QGridLayout(grp_identity)
        
        lbl_profile = QLabel("Manager Profile Name:")
        ui.txt_profile_name = QLineEdit()
        ui.txt_profile_name.setPlaceholderText("e.g. My_Survival_Server")
        ui.txt_profile_name.setStyleSheet("background-color: #000000; color: #00ffcc; border: 1px solid #555555; padding: 5px;")
        
        lbl_port = QLabel("Server Port:")
        ui.txt_server_port = QLineEdit()
        ui.txt_server_port.setText("26900")
        ui.txt_server_port.setStyleSheet("background-color: #000000; color: #00ffcc; border: 1px solid #555555; padding: 5px;")
        
        ui.btn_test_ports = QPushButton("TEST PORTS")
        ui.btn_test_ports.setStyleSheet("background-color: #9932CC; color: white; padding: 5px 10px; font-weight: bold; border: none;")
        
        ui.btn_test_cloud = QPushButton("TEST CLOUD")
        ui.btn_test_cloud.setStyleSheet("background-color: #9932CC; color: white; padding: 5px 10px; font-weight: bold; border: none;")
        
        lbl_repo = QLabel("Mod Storage Repository:")
        ui.txt_mod_repo = QLineEdit()
        ui.txt_mod_repo.setPlaceholderText("User/Repo")
        ui.txt_mod_repo.setStyleSheet("background-color: #000000; color: #00ffcc; border: 1px solid #555555; padding: 5px;")
        
        ui.btn_save_identity = QPushButton("SAVE IDENTITY")
        ui.btn_save_identity.setStyleSheet("background-color: #2ecc71; color: black; padding: 5px 10px; font-weight: bold; border: none;")
        
        port_box = QHBoxLayout()
        port_box.addWidget(ui.txt_server_port)
        port_box.addWidget(ui.btn_test_ports)
        port_box.addWidget(ui.btn_test_cloud)
        
        repo_box = QHBoxLayout()
        repo_box.addWidget(ui.txt_mod_repo)
        repo_box.addWidget(ui.btn_save_identity)

        id_layout.addWidget(lbl_profile, 0, 0)
        id_layout.addWidget(ui.txt_profile_name, 0, 1)
        id_layout.addWidget(lbl_port, 1, 0)
        id_layout.addLayout(port_box, 1, 1)
        id_layout.addWidget(lbl_repo, 2, 0)
        id_layout.addLayout(repo_box, 2, 1)
        
        setup_layout.addWidget(grp_identity)

        # -- Provisioning Group --
        grp_provision = QGroupBox("STEP 2: PROVISIONING ENGINE")
        grp_provision.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 1px solid #444444;
                margin-top: 15px;
                color: #00ffcc;
                font-weight: bold;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #121212;
            }
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border: none;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #555555; }
            QPushButton:disabled { background-color: #222222; color: #555555; }
        """)
        prov_layout = QVBoxLayout(grp_provision)
        prov_layout.setSpacing(10)
        
        ui.btn_browse_adopt = QPushButton("ADOPT EXISTING FOLDER")
        ui.btn_init_tool = QPushButton("STEP A: INITIALIZE STEAMCMD TOOL")
        ui.btn_deploy_fresh = QPushButton("STEP B: DOWNLOAD 12GB SERVER FILES")
        
        prov_layout.addWidget(ui.btn_browse_adopt)
        prov_layout.addWidget(ui.btn_init_tool)
        prov_layout.addWidget(ui.btn_deploy_fresh)
        
        lbl_warn = QLabel("WARNING: This downloads 12GB of data from Steam. Ensure you have disk space.")
        lbl_warn.setStyleSheet("color: #888888; font-style: italic;")
        prov_layout.addWidget(lbl_warn)
        
        ui.txt_steamcmd_output = QTextEdit()
        ui.txt_steamcmd_output.setReadOnly(True)
        ui.txt_steamcmd_output.setStyleSheet("background-color: #000000; color: #00ff00; font-family: Consolas; border: 1px solid #555555;")
        ui.txt_steamcmd_output.setText("SteamCMD Output will appear here...")
        prov_layout.addWidget(ui.txt_steamcmd_output)

        setup_layout.addWidget(grp_provision)
        
        # Wrap Page 0 in scroll area
        scroll_0 = QScrollArea()
        scroll_0.setWidgetResizable(True)
        scroll_0.setWidget(page_setup)
        scroll_0.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_0)

        # ---------------------------------------------------------
        # PAGE 1: Identity & Web
        # ---------------------------------------------------------
        page_1 = QWidget()
        page_1.setStyleSheet("background-color: #252526;")
        lay_1 = QGridLayout(page_1)
        lay_1.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_1, 0, "ServerName", "txt_ServerName", "My Game Host")
        add_setting_row(lay_1, 1, "ServerDescription", "txt_ServerDescription", "A 7 Days to Die server")
        add_setting_row(lay_1, 2, "ServerWebsiteURL", "txt_ServerWebsiteURL", "")
        add_setting_row(lay_1, 3, "ServerPassword", "txt_ServerPassword", "")
        add_setting_row(lay_1, 4, "ServerLoginConfirmationText", "txt_ServerLoginConfirmationText", "")
        
        scroll_1 = QScrollArea()
        scroll_1.setWidgetResizable(True)
        scroll_1.setWidget(page_1)
        scroll_1.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_1)

        # ---------------------------------------------------------
        # PAGE 2: Networking & Slots
        # ---------------------------------------------------------
        page_2 = QWidget()
        page_2.setStyleSheet("background-color: #252526;")
        lay_2 = QGridLayout(page_2)
        lay_2.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_2, 0, "ServerPort", "txt_ServerPort", "26900")
        add_setting_row(lay_2, 1, "ServerVisibility", "txt_ServerVisibility", "2")
        add_setting_row(lay_2, 2, "ServerMaxPlayerCount", "txt_ServerMaxPlayerCount", "8")
        add_setting_row(lay_2, 3, "ServerReservedSlots", "txt_ServerReservedSlots", "0")
        add_setting_row(lay_2, 4, "ServerReservedSlotsPermission", "txt_ServerReservedSlotsPermission", "100")
        
        scroll_2 = QScrollArea()
        scroll_2.setWidgetResizable(True)
        scroll_2.setWidget(page_2)
        scroll_2.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_2)

        # ---------------------------------------------------------
        # PAGE 3: Admin & Telnet
        # ---------------------------------------------------------
        page_3 = QWidget()
        page_3.setStyleSheet("background-color: #252526;")
        lay_3 = QGridLayout(page_3)
        lay_3.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_3, 0, "ServerAdminSlots", "txt_ServerAdminSlots", "0")
        add_setting_row(lay_3, 1, "ServerAdminSlotsPermission", "txt_ServerAdminSlotsPermission", "0")
        add_setting_row(lay_3, 2, "ControlPanelEnabled", "txt_ControlPanelEnabled", "false")
        add_setting_row(lay_3, 3, "ControlPanelPort", "txt_ControlPanelPort", "8080")
        add_setting_row(lay_3, 4, "ControlPanelPassword", "txt_ControlPanelPassword", "CHANGEME")
        add_setting_row(lay_3, 5, "TelnetEnabled", "txt_TelnetEnabled", "true")
        add_setting_row(lay_3, 6, "TelnetPort", "txt_TelnetPort", "8081")
        add_setting_row(lay_3, 7, "TelnetPassword", "txt_TelnetPassword", "")
        
        scroll_3 = QScrollArea()
        scroll_3.setWidgetResizable(True)
        scroll_3.setWidget(page_3)
        scroll_3.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_3)

        # ---------------------------------------------------------
        # PAGE 4: World Generation
        # ---------------------------------------------------------
        page_4 = QWidget()
        page_4.setStyleSheet("background-color: #252526;")
        lay_4 = QGridLayout(page_4)
        lay_4.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_4, 0, "GameWorld", "txt_GameWorld", "Navezgane")
        add_setting_row(lay_4, 1, "WorldGenSeed", "txt_WorldGenSeed", "asdf")
        add_setting_row(lay_4, 2, "WorldGenSize", "txt_WorldGenSize", "6144")
        add_setting_row(lay_4, 3, "GameName", "txt_GameName", "My Game")
        add_setting_row(lay_4, 4, "GameMode", "txt_GameMode", "GameModeSurvival")
        
        scroll_4 = QScrollArea()
        scroll_4.setWidgetResizable(True)
        scroll_4.setWidget(page_4)
        scroll_4.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_4)

        # ---------------------------------------------------------
        # PAGE 5: Difficulty & XP
        # ---------------------------------------------------------
        page_5 = QWidget()
        page_5.setStyleSheet("background-color: #252526;")
        lay_5 = QGridLayout(page_5)
        lay_5.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_5, 0, "GameDifficulty", "txt_GameDifficulty", "1")
        add_setting_row(lay_5, 1, "DayNightLength", "txt_DayNightLength", "60")
        add_setting_row(lay_5, 2, "DayLightLength", "txt_DayLightLength", "18")
        add_setting_row(lay_5, 3, "XPMultiplier", "txt_XPMultiplier", "100")
        add_setting_row(lay_5, 4, "PlayerBlockDamageMultiplier", "txt_PlayerBlockDamageMultiplier", "100")
        add_setting_row(lay_5, 5, "AIBlockDamageMultiplier", "txt_AIBlockDamageMultiplier", "100")
        add_setting_row(lay_5, 6, "PlayerDamageMultiplier", "txt_PlayerDamageMultiplier", "100")
        
        scroll_5 = QScrollArea()
        scroll_5.setWidgetResizable(True)
        scroll_5.setWidget(page_5)
        scroll_5.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_5)

        # ---------------------------------------------------------
        # PAGE 6: Rules & Survival
        # ---------------------------------------------------------
        page_6 = QWidget()
        page_6.setStyleSheet("background-color: #252526;")
        lay_6 = QGridLayout(page_6)
        lay_6.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_6, 0, "DropOnDeath", "txt_DropOnDeath", "1")
        add_setting_row(lay_6, 1, "DropOnQuit", "txt_DropOnQuit", "0")
        add_setting_row(lay_6, 2, "BloodMoonEnemyCount", "txt_BloodMoonEnemyCount", "8")
        add_setting_row(lay_6, 3, "BloodMoonWarning", "txt_BloodMoonWarning", "8")
        add_setting_row(lay_6, 4, "MaxSpawnedZombies", "txt_MaxSpawnedZombies", "64")
        add_setting_row(lay_6, 5, "MaxSpawnedAnimals", "txt_MaxSpawnedAnimals", "50")
        
        scroll_6 = QScrollArea()
        scroll_6.setWidgetResizable(True)
        scroll_6.setWidget(page_6)
        scroll_6.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_6)

        # ---------------------------------------------------------
        # PAGE 7: Zombies & Horde
        # ---------------------------------------------------------
        page_7 = QWidget()
        page_7.setStyleSheet("background-color: #252526;")
        lay_7 = QGridLayout(page_7)
        lay_7.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_7, 0, "EnemySpawnMode", "txt_EnemySpawnMode", "true")
        add_setting_row(lay_7, 1, "EnemyDifficulty", "txt_EnemyDifficulty", "0")
        add_setting_row(lay_7, 2, "ZombieFeralSense", "txt_ZombieFeralSense", "0")
        add_setting_row(lay_7, 3, "ZombieMove", "txt_ZombieMove", "0")
        add_setting_row(lay_7, 4, "ZombieMoveNight", "txt_ZombieMoveNight", "3")
        add_setting_row(lay_7, 5, "ZombieFeralMove", "txt_ZombieFeralMove", "3")
        add_setting_row(lay_7, 6, "ZombieBMMove", "txt_ZombieBMMove", "3")
        
        scroll_7 = QScrollArea()
        scroll_7.setWidgetResizable(True)
        scroll_7.setWidget(page_7)
        scroll_7.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_7)

        # ---------------------------------------------------------
        # PAGE 8: Loot & Multi
        # ---------------------------------------------------------
        page_8 = QWidget()
        page_8.setStyleSheet("background-color: #252526;")
        lay_8 = QGridLayout(page_8)
        lay_8.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_8, 0, "LootAbundance", "txt_LootAbundance", "100")
        add_setting_row(lay_8, 1, "LootRespawnDays", "txt_LootRespawnDays", "7")
        add_setting_row(lay_8, 2, "AirDropFrequency", "txt_AirDropFrequency", "72")
        add_setting_row(lay_8, 3, "AirDropMarker", "txt_AirDropMarker", "true")
        add_setting_row(lay_8, 4, "PartySharedKillRange", "txt_PartySharedKillRange", "100")
        add_setting_row(lay_8, 5, "PlayerKillingMode", "txt_PlayerKillingMode", "3")
        
        scroll_8 = QScrollArea()
        scroll_8.setWidgetResizable(True)
        scroll_8.setWidget(page_8)
        scroll_8.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_8)

        # ---------------------------------------------------------
        # PAGE 9: Land Claim & Misc
        # ---------------------------------------------------------
        page_9 = QWidget()
        page_9.setStyleSheet("background-color: #252526;")
        lay_9 = QGridLayout(page_9)
        lay_9.setAlignment(Qt.AlignTop)
        
        add_setting_row(lay_9, 0, "LandClaimSize", "txt_LandClaimSize", "41")
        add_setting_row(lay_9, 1, "LandClaimDeadZone", "txt_LandClaimDeadZone", "30")
        add_setting_row(lay_9, 2, "LandClaimExpiryTime", "txt_LandClaimExpiryTime", "7")
        add_setting_row(lay_9, 3, "LandClaimDecayMode", "txt_LandClaimDecayMode", "0")
        add_setting_row(lay_9, 4, "LandClaimOnlineDurabilityModifier", "txt_LandClaimOnlineDurabilityModifier", "4")
        add_setting_row(lay_9, 5, "LandClaimOfflineDurabilityModifier", "txt_LandClaimOfflineDurabilityModifier", "4")
        
        scroll_9 = QScrollArea()
        scroll_9.setWidgetResizable(True)
        scroll_9.setWidget(page_9)
        scroll_9.setStyleSheet("QScrollArea { border: none; background-color: #252526; }")
        stack.addWidget(scroll_9)

        # Link sidebar to stack
        sidebar.currentRowChanged.connect(stack.setCurrentIndex)
        sidebar.setCurrentRow(0)

        # Combine Left Sidebar and Right Stack into Splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(stack)
        splitter.setSizes(list((250, 950)))
        
        h_main.addWidget(splitter)
        
        # --- Bottom Commit Bar ---
        bottom_bar = QWidget()
        bottom_bar.setStyleSheet("background-color: #111111; border-top: 2px solid #333333;")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        
        ui.lbl_current_path = QLabel("SERVER PATH: UNCONFIGURED")
        ui.lbl_current_path.setStyleSheet("color: #888888; font-weight: bold;")
        
        ui.btn_save_srv_settings = QPushButton("COMMIT SETTINGS TO XML")
        ui.btn_save_srv_settings.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 15px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        
        bottom_layout.addWidget(ui.lbl_current_path)
        bottom_layout.addStretch()
        bottom_layout.addWidget(ui.btn_save_srv_settings)

        # Re-parent layout logic so the final UI renders perfectly
        holder_widget = QWidget()
        holder_widget.setLayout(h_main)
        
        real_main_layout = QVBoxLayout(tab)
        real_main_layout.setContentsMargins(0, 0, 0, 0)
        real_main_layout.setSpacing(0)
        real_main_layout.addWidget(holder_widget)
        real_main_layout.addWidget(bottom_bar)
        
        return tab