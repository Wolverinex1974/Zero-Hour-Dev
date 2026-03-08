# =========================================================
# ZERO HOUR UI: DIALOGS - v23.0
# =========================================================
# ROLE: Isolated UI Popups and Modals
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 18: MODULARIZATION REFACTOR
# FEATURE: Extracted AdvancedRestartDialog from admin_layouts
#          to reduce file bloat and decouple logic.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QRadioButton,
    QGridLayout,
    QSpinBox,
    QPushButton,
    QSizePolicy
)

class AdvancedRestartDialog(QDialog):
    """
    RAT-Parity Dialog for advanced server shutdown and restart procedures.
    Operates without freezing the main UI.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shutdown / Restart Server")
        self.resize(550, 250)
        
        self.main_layout = QVBoxLayout(self)
        
        self.h_reason = QHBoxLayout()
        self.lbl_reason = QLabel("Shutdown / Restart Reason")
        self.combo_reason = QComboBox()
        self.combo_reason.setEditable(True)
        self.combo_reason.addItems(list((
            "Server needs to restart, please join back in a couple of minutes.",
            "Emergency maintenance, shutting down.",
            "Applying new mods, restart imminent.",
            "Daily scheduled reboot sequence."
        )))
        self.combo_reason.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.h_reason.addWidget(self.lbl_reason)
        self.h_reason.addWidget(self.combo_reason)
        self.main_layout.addLayout(self.h_reason)
        
        self.h_checks = QHBoxLayout()
        self.chk_restart = QCheckBox("Restart Server")
        self.chk_restart.setChecked(True)
        self.chk_override = QCheckBox("Override Keep Alive")
        self.h_checks.addStretch()
        self.h_checks.addWidget(self.chk_restart)
        self.h_checks.addWidget(self.chk_override)
        self.main_layout.addLayout(self.h_checks)
        
        self.h_middle = QHBoxLayout()
        
        self.grp_type = QGroupBox("Shutdown / Restart Type")
        self.v_type = QVBoxLayout(self.grp_type)
        self.radio_no_count = QRadioButton("Shutdown No Countdown")
        self.radio_with_count = QRadioButton("Shutdown with Countdown")
        self.radio_with_count.setChecked(True)
        self.v_type.addWidget(self.radio_no_count)
        self.v_type.addWidget(self.radio_with_count)
        self.h_middle.addWidget(self.grp_type)
        
        self.grp_count = QGroupBox("Countdown Settings")
        self.g_count = QGridLayout(self.grp_count)
        self.lbl_min = QLabel("Minutes Countdown")
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 60)
        self.spin_min.setValue(5)
        self.lbl_sec = QLabel("Seconds Countdown")
        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        self.spin_sec.setValue(10)
        
        self.g_count.addWidget(self.lbl_min, 0, 0)
        self.g_count.addWidget(self.spin_min, 0, 1)
        self.g_count.addWidget(self.lbl_sec, 1, 0)
        self.g_count.addWidget(self.spin_sec, 1, 1)
        self.h_middle.addWidget(self.grp_count)
        
        self.main_layout.addLayout(self.h_middle)
        
        self.h_buttons = QHBoxLayout()
        self.btn_perform = QPushButton("Perform Action")
        self.btn_perform.setMinimumHeight(30)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumHeight(30)
        self.h_buttons.addStretch()
        self.h_buttons.addWidget(self.btn_perform)
        self.h_buttons.addWidget(self.btn_cancel)
        self.h_buttons.addStretch()
        self.main_layout.addLayout(self.h_buttons)
        
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_perform.clicked.connect(self.accept)