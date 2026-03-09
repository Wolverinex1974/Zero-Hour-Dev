# ==============================================================================
# ZERO HOUR UI: NEXUS STYLER (CSS ENGINE) - v23.2
# ==============================================================================
# ROLE: The central repository for all Global CSS rules (Industrial Dark Theme).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand - Bracket Free
# ==============================================================================
# PHASE 24 UPDATE:
# FIX: Restored @staticmethod get_industrial_style() to satisfy ZeroHourLayout.
# FIX: Maintained the solid blue background highlight for :checked navigation tabs.
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
        color_palette["background_base"] = "#1e1e1e"
        color_palette["background_alt"] = "#252526"
        color_palette["border_dark"] = "#333333"
        color_palette["text_light"] = "#e0e0e0"
        color_palette["text_muted"] = "#888888"
        color_palette["accent_blue"] = "#0078d7"
        color_palette["accent_blue_hover"] = "#005a9e"
        color_palette["accent_green"] = "#2ecc71"
        color_palette["accent_red"] = "#e74c3c"
        color_palette["accent_orange"] = "#e67e22"
        color_palette["accent_purple"] = "#9932CC"

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
                background-color: transparent;
                color: {color_palette["text_muted"]};
                border: none;
                border-bottom: 3px solid transparent;
                padding: 15px;
                font-weight: bold;
                font-size: 13px;
                text-transform: uppercase;
            }}

            QPushButton#main_nav_button:hover {{
                background-color: {color_palette["border_dark"]};
                color: {color_palette["text_light"]};
            }}

            QPushButton#main_nav_button:checked {{
                background-color: {color_palette["accent_blue"]};
                color: #ffffff;
                border-bottom: 3px solid #004c8c;
            }}

            /* Standard Inputs */
            QLineEdit, QSpinBox, QComboBox {{
                background-color: #000000;
                color: #00ffcc;
                border: 1px solid {color_palette["border_dark"]};
                padding: 5px;
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
                background-color: {color_palette["border_dark"]};
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
                color: {color_palette["text_muted"]};
                border: 1px solid {color_palette["border_dark"]};
            }}

            /* Main Header Title Label */
            QLabel#header_title {{
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            
            QLabel#header_subtitle {{
                color: {color_palette["text_muted"]};
                font-size: 14px;
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

            /* Specific Action Colors (Can be applied via setProperty or ID if needed) */
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
        """
        
        return stylesheet_string