# ==============================================================================
# ZERO HOUR UI: NEXUS STYLER (CSS ENGINE) - v23.2
# ==============================================================================
# ROLE: The central repository for all Global CSS rules (Industrial Dark Theme).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE (v16 RESTORATION):
# FIX: Reverted main_nav_button to v16 subtle dark grey with purple accent.
# FIX: Added custom IDs for Forge Action Buttons (Install/Scan/Publish).
# FIX: Added custom styling for the v16 Header Profile controls.
# ==============================================================================

class NexusStyler:
    """
    A unified stylesheet engine that applies the 'Industrial Dark' theme
    to the entire Zero Hour Server Manager application.
    """
    @staticmethod
    def get_industrial_style():
        """
        Returns the fully compiled string of global CSS rules.
        """
        color_palette = dict()
        color_palette["background_base"] = "#161616"
        color_palette["background_alt"] = "#1E1E1E"
        color_palette["border_dark"] = "#2A2A2A"
        color_palette["text_light"] = "#E0E0E0"
        color_palette["text_muted"] = "#888888"
        color_palette["accent_purple"] = "#9b59b6"
        color_palette["accent_purple_hover"] = "#8e44ad"
        color_palette["accent_orange"] = "#e67e22"
        color_palette["accent_orange_hover"] = "#d35400"
        color_palette["accent_blue"] = "#2980b9"
        color_palette["accent_blue_hover"] = "#2471a3"
        color_palette["accent_green"] = "#2ecc71"
        color_palette["accent_red"] = "#e74c3c"
        color_palette["tab_active_bg"] = "#252526"

        stylesheet_string = f"""
            /* Global Application Rules */
            QMainWindow {{
                background-color: {color_palette["background_base"]};
                color: {color_palette["text_light"]};
            }}

            QWidget {{
                color: {color_palette["text_light"]};
            }}

            /* Top Level Navigation Tabs (Dashboard, Configuration, Forge, etc.) */
            QPushButton#main_nav_button {{
                background-color: {color_palette["background_base"]};
                color: {color_palette["text_muted"]};
                border: 1px solid transparent;
                border-bottom: 2px solid #333333;
                border-right: 1px solid #222222;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }}

            QPushButton#main_nav_button:hover {{
                background-color: {color_palette["background_alt"]};
                color: {color_palette["text_light"]};
            }}

            QPushButton#main_nav_button:checked {{
                background-color: {color_palette["tab_active_bg"]};
                color: {color_palette["text_light"]};
                border-top: 2px solid {color_palette["accent_purple"]};
                border-bottom: 2px solid transparent;
                border-left: 1px solid #333333;
                border-right: 1px solid #333333;
            }}

            /* Standard Inputs */
            QLineEdit, QSpinBox {{
                background-color: #000000;
                color: {color_palette["accent_green"]};
                border: 1px solid {color_palette["border_dark"]};
                padding: 5px;
            }}
            
            QComboBox {{
                background-color: #0078D7;
                color: #ffffff;
                border: 1px solid #005A9E;
                padding: 5px 10px;
                font-weight: bold;
            }}
            
            QComboBox::drop-down {{
                border-left: 1px solid #005A9E;
            }}

            /* Standard Output / Log Windows */
            QTextEdit {{
                background-color: #000000;
                color: {color_palette["text_light"]};
                border: 1px solid {color_palette["border_dark"]};
                font-family: Consolas, monospace;
                padding: 5px;
            }}

            /* Standard Push Buttons */
            QPushButton {{
                background-color: #333333;
                color: {color_palette["text_light"]};
                border: 1px solid #444444;
                padding: 8px 15px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: #444444;
                border: 1px solid #555555;
            }}

            QPushButton:pressed {{
                background-color: #222222;
            }}
            
            QPushButton:disabled {{
                background-color: #222222;
                color: #555555;
                border: 1px solid #333333;
            }}

            /* Main Header Title Label */
            QLabel#header_title {{
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }}
            
            /* Tactical Navigation Buttons (Folders) */
            QPushButton#tactical_btn {{
                background-color: #2D2D30;
                color: #DCDCAA;
                border: 1px solid #3E3E42;
                padding: 8px 15px;
                font-weight: bold;
                text-align: left;
            }}
            
            QPushButton#tactical_btn:hover {{
                background-color: #3E3E42;
                color: #ffffff;
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: {color_palette["background_base"]};
                width: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #555555;
                min-height: 20px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #777777;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {color_palette["background_base"]};
                height: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #555555;
                min-width: 20px;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: #777777;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}

            /* Specific Action Colors (v16 Restoration) */
            QPushButton#btn_action_start {{
                background-color: {color_palette["accent_green"]};
                color: #000000;
                border: none;
            }}
            QPushButton#btn_action_start:hover {{
                background-color: #27ae60;
            }}
            
            QPushButton#btn_action_stop {{
                background-color: {color_palette["accent_red"]};
                color: #ffffff;
                border: none;
            }}
            QPushButton#btn_action_stop:hover {{
                background-color: #c0392b;
            }}
            
            QPushButton#btn_action_delete {{
                background-color: {color_palette["accent_red"]};
                color: #ffffff;
                border: none;
                padding: 5px 20px;
            }}
            QPushButton#btn_action_delete:hover {{
                background-color: #c0392b;
            }}
            
            QPushButton#btn_install_blue {{
                background-color: {color_palette["accent_blue"]};
                color: #ffffff;
                border: none;
            }}
            QPushButton#btn_install_blue:hover {{
                background-color: {color_palette["accent_blue_hover"]};
            }}
            
            QPushButton#btn_scan_orange {{
                background-color: {color_palette["accent_orange"]};
                color: #ffffff;
                border: none;
            }}
            QPushButton#btn_scan_orange:hover {{
                background-color: {color_palette["accent_orange_hover"]};
            }}
            
            QPushButton#btn_publish_purple {{
                background-color: {color_palette["accent_purple"]};
                color: #ffffff;
                border: none;
                font-size: 14px;
                padding: 15px;
            }}
            QPushButton#btn_publish_purple:hover {{
                background-color: {color_palette["accent_purple_hover"]};
            }}
        """
        
        return stylesheet_string