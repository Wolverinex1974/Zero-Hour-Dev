# =========================================================
# ZERO HOUR UI: NEXUS STYLER - v20.8 (PHASE 13)
# =========================================================
# ROLE: Centralized Visual Logic & Tactile Feedback
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 13 FEATURES:
# FEATURE: Added 'Tactical Navigation' button styles.
# FEATURE: Centralized 'Sovereign' color constants.
# FIX: Refined Scrollbar width for high-DPI monitors.
# =========================================================

class NexusStyler:
    """
    The Aesthetic Engine for the Paradoxal Ecosystem.
    Manages stylesheets for Zero Hour and the Launcher.
    Implements tactile physical feedback and high-density dashboard layouts.
    """

    # --- SOVEREIGN COLOR PALETTE ---
    # Standardized hex codes for industrial uniformity.
    ACCENT_GREEN = "#2ecc71"
    ACCENT_PURPLE = "#9b59b6"
    ACCENT_ORANGE = "#e67e22"
    ACCENT_RED = "#c0392b"
    ACCENT_BLUE = "#2980b9"
    BG_MAIN = "#1e1e1e"
    BG_DARK = "#121212"
    BG_PANEL = "#252525"
    BG_INPUT = "#000000"
    TEXT_MAIN = "#e0e0e0"
    TEXT_DIM = "#aaaaaa"

    @classmethod
    def get_industrial_style(cls):
        """
        Generates and returns the master QSS stylesheet string.
        Contains the tactile physics logic and sidebar tab separation.
        """
        style_string = f"""
        /* --- MAIN WINDOW ARCHITECTURE --- */
        QMainWindow, QWidget {{ 
            background-color: {cls.BG_MAIN}; 
            color: {cls.TEXT_MAIN}; 
            font-family: 'Segoe UI', Arial, sans-serif; 
        }}

        /* --- TAB NAVIGATION SYSTEM --- */
        QTabWidget::pane {{ 
            border: 1px solid #333333; 
            background: {cls.BG_MAIN}; 
            top: -1px;
        }}
        
        QTabBar::tab {{ 
            background: #2d2d2d; 
            color: {cls.TEXT_DIM}; 
            padding: 12px 30px; 
            border: 1px solid #1a1a1a; 
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{ 
            background: #3d3d3d; 
            color: #ffffff; 
            border-bottom: 2px solid {cls.ACCENT_PURPLE};
        }}

        /* --- SETTINGS SIDEBAR (PHYSICAL CARD UPDATE) --- */
        QListWidget#nav_settings {{
            background-color: transparent;
            border: none;
            color: {cls.TEXT_DIM};
            outline: none;
        }}

        QListWidget#nav_settings::item {{
            background-color: {cls.BG_PANEL};
            border: 1px solid #333333;
            border-radius: 2px;
            margin-bottom: 4px;
            padding: 12px;
        }}

        QListWidget#nav_settings::item:selected {{
            background-color: #3d3d3d;
            color: {cls.ACCENT_GREEN};
            border: 1px solid {cls.ACCENT_GREEN};
            font-weight: bold;
        }}

        QListWidget#nav_settings::item:hover {{
            background-color: #2a2a2a;
            border: 1px solid #555555;
        }}

        /* --- TACTICAL NAVIGATION SUITE (PHASE 13) --- */
        /* Specific styling for the top-bar folder buttons */
        QPushButton#tactical_button {{
            background-color: #3d3d3d;
            border: 1px solid #555;
            height: 25px;
            font-size: 11px;
            padding: 4px 10px;
        }}
        
        QPushButton#tactical_button:hover {{
            background-color: #4d4d4d;
            border: 1px solid {cls.ACCENT_PURPLE};
        }}
        
        QPushButton#tactical_button:pressed {{
            background-color: #222;
            border: 1px solid {cls.ACCENT_GREEN};
            padding-top: 6px; /* Tactile sink */
        }}

        /* --- STANDARD BUTTON PROTOCOL --- */
        QPushButton {{ 
            background-color: #3d3d3d; 
            color: #ffffff; 
            border: 1px solid #1a1a1a; 
            padding: 8px 15px; 
            font-weight: bold;
            text-transform: uppercase;
            outline: none;
        }}
        
        QPushButton:hover {{ 
            background-color: #4d4d4d; 
            border: 1px solid {cls.ACCENT_GREEN};
        }}
        
        /* THE PHYSICAL SINK: Simulates mechanical compression */
        QPushButton:pressed {{ 
            background-color: #1a1a1a;
            padding-top: 11px;
            padding-left: 18px;
            border: 1px solid #000000;
        }}

        QPushButton:disabled {{ 
            background-color: {cls.BG_PANEL}; 
            color: #555555; 
            border: 1px solid #1a1a1a;
        }}

        /* --- SPECIALIZED ACTION BUTTONS --- */
        #btn_commit_deploy {{ 
            background-color: {cls.ACCENT_PURPLE}; 
            color: white; 
        }}
        #btn_commit_deploy:hover {{ 
            background-color: #8e44ad; 
        }}

        #btn_start_server {{ 
            background-color: #27ae60; 
            color: white; 
        }}
        #btn_start_server:hover {{ 
            background-color: {cls.ACCENT_GREEN}; 
        }}

        #btn_stop_server {{ 
            background-color: {cls.ACCENT_RED}; 
            color: white; 
        }}
        #btn_stop_server:hover {{ 
            background-color: #e74c3c; 
        }}

        #btn_save_news {{ 
            background-color: {cls.ACCENT_BLUE}; 
            color: white; 
        }}
        
        #btn_validate_env {{
            background-color: #8e44ad;
            color: white;
        }}

        /* --- DATA GRID & TABLE INTERFACE --- */
        QTableWidget {{ 
            background-color: {cls.BG_PANEL}; 
            gridline-color: #333333; 
            color: #ffffff; 
            border: 1px solid #333333;
            selection-background-color: #3d3d3d;
        }}
        
        QHeaderView::section {{ 
            background-color: #2d2d2d; 
            color: {cls.TEXT_DIM}; 
            padding: 10px; 
            border: 1px solid #1e1e1e; 
            font-weight: bold;
        }}

        /* --- INPUT FIELD THEMING --- */
        QTextEdit, QPlainTextEdit, QLineEdit {{ 
            background-color: {cls.BG_INPUT}; 
            color: {cls.ACCENT_GREEN}; 
            border: 1px solid #333333; 
            font-family: 'Consolas', 'Courier New', monospace;
            padding: 5px;
        }}

        /* --- CONTAINERS & GROUP BOXES --- */
        QGroupBox {{ 
            border: 1px solid #333333; 
            margin-top: 15px; 
            padding-top: 15px; 
            color: {cls.ACCENT_GREEN}; 
            font-weight: bold; 
        }}
        
        /* --- PROGRESS REPORTING SYSTEM --- */
        QProgressBar {{ 
            border: 1px solid #333333; 
            background: #222222; 
            text-align: center; 
            color: white; 
        }}
        
        QProgressBar::chunk {{ 
            background-color: {cls.ACCENT_GREEN}; 
        }}

        /* --- SCROLLBAR ARCHITECTURE --- */
        QScrollBar:vertical {{
            border: none;
            background: {cls.BG_DARK};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: #444;
            min-height: 20px;
            border-radius: 2px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
        return style_string

    @classmethod
    def apply_dirty_state(cls, button, is_dirty):
        """
        Shifts the button appearance based on unsaved logic.
        """
        if is_dirty:
            button.setStyleSheet(f"background-color: {cls.ACCENT_PURPLE}; color: white;")
        else:
            button.setStyleSheet("background-color: #3d3d3d; color: white;")