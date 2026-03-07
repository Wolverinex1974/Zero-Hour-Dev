# =========================================================
# ZERO HOUR UI: FAQ TAB WRAPPER - v20.8
# =========================================================
# ROLE: Adapts the legacy KnowledgeBaseUI into the new
#       Phase 20 Builder Architecture.
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 20 UI RESTORATION:
# FEATURE: Imports the existing content from ui/faq_knowledgebase.py
# FIX: 100% Bracket-Free payload.
# =========================================================

from ui.faq_knowledgebase import KnowledgeBaseUI

class FAQTabBuilder:
    """
    Wrapper class that instantiates the existing KnowledgeBaseUI
    so it fits into the new admin_layouts.py Builder pattern.
    """
    @staticmethod
    def build(main_ui):
        # Instantiate the existing widget logic
        # This class (defined in ui/faq_knowledgebase.py)
        # handles its own layout, topics, and text content.
        tab = KnowledgeBaseUI()
        
        # No external signal binding is required for the FAQ
        # as it is a self-contained read-only module.
        
        return tab