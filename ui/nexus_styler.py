# ==============================================================================
# ZERO HOUR UI: NEXUS STYLER - v23.0
# ==============================================================================
# ROLE: The "Paint". Centralized CSS Stylesheet Manager.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 23 UPDATE (VISUAL REPAIR):
# FIX: Added 'QPushButton:checked' state for Navigation Tabs (Blue Highlight).
# FIX: Hardcoded Green/Red styles for Start/Stop buttons via ID selectors.
# FIX: Refined Scrollbar and GroupBox styling for high contrast.
# ==============================================================================

class NexusStyler:
    """
    Static class that returns the master QSS (Qt Style Sheet) string.
    This defines the "Zero Hour Industrial" theme.
    """

    @staticmethod
    def get_industrial_style():
        return """
        /* -----------------------------------------------------------------
           GLOBAL WINDOW SETTINGS
           ----------------------------------------------------------------- */
        QMainWindow, QWidget#central_widget {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }

        /* -----------------------------------------------------------------
           GLOBAL TEXT ELEMENTS
           ----------------------------------------------------------------- */
        QLabel {
            color: #E0E0E0;
            font-size: 12px;
        }
        
        QLabel#lbl_app_title {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        QLabel#lbl_active_profile {
            color: #00A8E8;
            font-weight: bold;
            font-size: 12px;
        }

        /* -----------------------------------------------------------------
           NAVIGATION BAR (The Tabs)
           ----------------------------------------------------------------- */
        QFrame#nav_frame {
            background-color: #1A1A1A;
            border-bottom: 2px solid #333;
        }

        /* Default Tab State */
        QPushButton#nav_btn {
            background-color: transparent;
            color: #888;
            border: none;
            border-right: 1px solid #333;
            font-weight: bold;
            text-transform: uppercase;
            padding: 10px;
            margin: 0px;
            border-radius: 0px;
        }

        QPushButton#nav_btn:hover {
            background-color: #252525;
            color: #FFF;
        }

        /* Active Tab State (THE GHOST TAB FIX) */
        QPushButton#nav_btn:checked {
            background-color: #007ACC; /* Vivid Blue */
            color: #FFFFFF;
            border-bottom: 2px solid #FFFFFF;
        }

        /* -----------------------------------------------------------------
           TACTICAL TOOLBAR (Header Buttons)
           ----------------------------------------------------------------- */
        QFrame#tactical_frame {
            background-color: #0F0F0F;
            border-bottom: 1px solid #333;
        }

        QPushButton#tactical_btn {
            background-color: #222;
            color: #DDD;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 5px 15px;
            font-size: 11px;
            font-weight: bold;
        }

        QPushButton#tactical_btn:hover {
            background-color: #333;
            border: 1px solid #666;
        }

        /* -----------------------------------------------------------------
           REACTOR CONTROL (Traffic Lights)
           ----------------------------------------------------------------- */
        /* Start Server - Green */
        QPushButton#btn_start_server {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
            border: 1px solid #219150;
            border-radius: 3px;
        }
        QPushButton#btn_start_server:hover {
            background-color: #2ecc71;
        }
        QPushButton#btn_start_server:disabled {
            background-color: #145a32;
            color: #555;
        }

        /* Stop Server - Red */
        QPushButton#btn_stop_server {
            background-color: #c0392b;
            color: white;
            font-weight: bold;
            border: 1px solid #a93226;
            border-radius: 3px;
        }
        QPushButton#btn_stop_server:hover {
            background-color: #e74c3c;
        }
        QPushButton#btn_stop_server:disabled {
            background-color: #641e16;
            color: #555;
        }

        /* Options / Shutdown - Grey */
        QPushButton#btn_shutdown_dialog {
            background-color: #7f8c8d;
            color: white;
            font-weight: bold;
            border: 1px solid #626e6e;
            border-radius: 3px;
        }
        QPushButton#btn_shutdown_dialog:hover {
            background-color: #95a5a6;
        }

        /* -----------------------------------------------------------------
           INPUT FIELDS & COMBO BOXES
           ----------------------------------------------------------------- */
        QLineEdit, QComboBox, QSpinBox {
            background-color: #000000;
            border: 1px solid #444;
            color: #00FFCC; /* Cyberpunk Text */
            padding: 5px;
            selection-background-color: #007ACC;
        }

        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #007ACC;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #444;
            border-left-style: solid;
        }

        /* -----------------------------------------------------------------
           SCROLL BARS (Thin Industrial)
           ----------------------------------------------------------------- */
        QScrollBar:vertical {
            border: none;
            background: #111;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #444;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        /* -----------------------------------------------------------------
           TABLES & LISTS
           ----------------------------------------------------------------- */
        QTableWidget, QListWidget, QTextEdit {
            background-color: #0D0D0D;
            border: 1px solid #333;
            color: #CCC;
            gridline-color: #333;
        }
        
        QHeaderView::section {
            background-color: #222;
            color: #FFF;
            padding: 5px;
            border: 1px solid #333;
            font-weight: bold;
        }

        QTableWidget::item:selected, QListWidget::item:selected {
            background-color: #004466;
            color: white;
        }

        /* -----------------------------------------------------------------
           GROUP BOXES
           ----------------------------------------------------------------- */
        QGroupBox {
            border: 1px solid #333;
            margin-top: 10px;
            padding-top: 15px;
            font-weight: bold;
            color: #00A8E8;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            background-color: #121212; /* Matches window bg to look transparent */
        }
        """