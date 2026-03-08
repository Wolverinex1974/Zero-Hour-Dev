# ==============================================================================
# ZERO HOUR UI: FAQ TAB - v23.0
# ==============================================================================
# ROLE: Wrapper for the Knowledge Base Module.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 22 UPDATE (DRIFT REPAIR):
# FIX: Implemented 'FaqTabBuilder' class to match the architecture of other tabs.
# FIX: Added 'ImportError' handling to prevent crash if KnowledgeBaseUI is missing.
# FIX: Ensures 'tab_faq' object name is set for correct Router mapping.
# ==============================================================================

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel
)
from PySide6.QtCore import Qt

# region [OPTIONAL_IMPORT]
# We wrap this import in a try/except block to ensure the Main Menu 
# still loads even if the FAQ module has a syntax error.
try:
    from ui.faq_knowledgebase import KnowledgeBaseUI
except ImportError:
    KnowledgeBaseUI = None
# endregion

class FaqTabBuilder:
    """
    Static Builder class for the FAQ / Knowledge Base Tab.
    This provides a standardized entry point for 'admin_layouts.py'.
    """
    
    @staticmethod
    def build(main_window):
        """
        Constructs the FAQ Tab widget.
        :param main_window: Reference to the main application window.
        :return: QWidget (The configured tab)
        """
        # 1. Create Container
        tab = QWidget()
        tab.setObjectName("tab_faq")
        
        # 2. Create Layout
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 3. Inject Content
        if KnowledgeBaseUI:
            try:
                # Attempt to initialize the Knowledge Base logic
                kb_content = KnowledgeBaseUI()
                
                # Check if it's a QWidget we can add directly
                if isinstance(kb_content, QWidget):
                    layout.addWidget(kb_content)
                
                # Check if it's a Ui_Form class that needs setup
                elif hasattr(kb_content, 'setupUi'):
                    kb_widget = QWidget()
                    kb_content.setupUi(kb_widget)
                    layout.addWidget(kb_widget)
                    
                # Check if it uses our custom 'setup_ui' pattern
                elif hasattr(kb_content, 'setup_ui'):
                    kb_content.setup_ui(tab)
                    
                else:
                    # Fallback for unknown structure
                    FaqTabBuilder._inject_error_message(layout, "Unknown KB Structure")
                    
            except Exception as e:
                # Catch instantiation errors (e.g. missing assets in KB)
                FaqTabBuilder._inject_error_message(layout, f"Knowledge Base Crash: {str(e)}")
        else:
            # Fallback if the file import failed entirely
            FaqTabBuilder._inject_error_message(layout, "Knowledge Base Module Missing (ui.faq_knowledgebase)")

        return tab

    @staticmethod
    def _inject_error_message(layout, message):
        """
        Helper to display a user-friendly error instead of crashing to desktop.
        """
        error_container = QWidget()
        error_layout = QVBoxLayout(error_container)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_icon = QLabel("⚠️")
        lbl_icon.setStyleSheet("font-size: 48px;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_layout.addWidget(lbl_icon)
        error_layout.addWidget(lbl_msg)
        
        layout.addWidget(error_container)