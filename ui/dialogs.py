# ==============================================================================
# ZERO HOUR UI: DIALOGS - v23.2
# ==============================================================================
# ROLE: Isolated UI Popups and Modals (Restart, Confirmations).
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ==============================================================================
# PHASE 23 UPDATE (RAT REPLACEMENT):
# FIX: Implemented 'AdvancedRestartDialog' with full countdown/reason logic.
# FIX: Styled with 'NexusStyler' CSS for consistent Dark Mode look.
# ==============================================================================

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QRadioButton,
    QSpinBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class AdvancedRestartDialog(QDialog):
    """
    A complex dialog mimicking the 'RAT' Shutdown/Restart interface.
    Returns a dictionary of settings when accepted.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shutdown / Restart Server")
        self.resize(500, 350)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #ddd; }
            QGroupBox { border: 1px solid #444; margin-top: 10px; font-weight: bold; color: #00A8E8; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QLabel { color: #ccc; }
            QComboBox, QSpinBox { background-color: #111; color: #fff; border: 1px solid #555; padding: 4px; }
            QPushButton { background-color: #333; color: white; border: 1px solid #555; padding: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #444; border-color: #00A8E8; }
        """)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # -------------------------------------------------------------
        # SECTION 1: REASON
        # -------------------------------------------------------------
        lbl_reason = QLabel("Shutdown / Restart Reason:")
        self.main_layout.addWidget(lbl_reason)

        self.combo_reason = QComboBox()
        self.combo_reason.setEditable(True)
        self.combo_reason.addItems([
            "Server needs to restart, please join back in a couple of minutes.",
            "Scheduled Maintenance.",
            "Updating Mods.",
            "Installing Game Update.",
            "Performance Restart."
        ])
        self.main_layout.addWidget(self.combo_reason)

        # -------------------------------------------------------------
        # SECTION 2: TOGGLES
        # -------------------------------------------------------------
        h_toggles = QHBoxLayout()
        
        self.chk_restart = QCheckBox("Restart Server Process")
        self.chk_restart.setChecked(True) # Default to restart logic
        self.chk_restart.setToolTip("If unchecked, server will simply stop.")
        self.chk_restart.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        self.chk_override = QCheckBox("Override Keep Alive")
        self.chk_override.setToolTip("Prevents the Watchdog from interfering if it's active.")
        
        h_toggles.addWidget(self.chk_restart)
        h_toggles.addStretch()
        h_toggles.addWidget(self.chk_override)
        
        self.main_layout.addLayout(h_toggles)

        # -------------------------------------------------------------
        # SECTION 3: TIMING OPTIONS
        # -------------------------------------------------------------
        h_split = QHBoxLayout()
        
        # Left: Type
        grp_type = QGroupBox("Shutdown / Restart Type")
        v_type = QVBoxLayout(grp_type)
        
        self.rad_now = QRadioButton("Immediate (No Countdown)")
        self.rad_countdown = QRadioButton("Scheduled (With Countdown)")
        self.rad_countdown.setChecked(True)
        
        # Connect logic to disable/enable spinners
        self.rad_now.toggled.connect(self._toggle_spinners)
        
        v_type.addWidget(self.rad_now)
        v_type.addWidget(self.rad_countdown)
        v_type.addStretch()
        
        h_split.addWidget(grp_type)
        
        # Right: Timer
        grp_timer = QGroupBox("Countdown Settings")
        grid_timer = QVBoxLayout(grp_timer)
        
        h_min = QHBoxLayout()
        lbl_min = QLabel("Minutes:")
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 60)
        self.spin_min.setValue(5)
        h_min.addWidget(lbl_min)
        h_min.addWidget(self.spin_min)
        
        h_sec = QHBoxLayout()
        lbl_sec = QLabel("Seconds:")
        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        self.spin_sec.setValue(0)
        h_sec.addWidget(lbl_sec)
        h_sec.addWidget(self.spin_sec)
        
        grid_timer.addLayout(h_min)
        grid_timer.addLayout(h_sec)
        
        h_split.addWidget(grp_timer)
        
        self.main_layout.addLayout(h_split)

        # -------------------------------------------------------------
        # SECTION 4: ACTIONS
        # -------------------------------------------------------------
        self.main_layout.addStretch()
        
        h_btns = QHBoxLayout()
        h_btns.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setMinimumWidth(80)
        
        self.btn_action = QPushButton("Perform Action")
        self.btn_action.clicked.connect(self.accept)
        self.btn_action.setMinimumWidth(120)
        self.btn_action.setStyleSheet("background-color: #c0392b; border-color: #e74c3c;")
        
        h_btns.addWidget(self.btn_action)
        h_btns.addWidget(self.btn_cancel)
        
        self.main_layout.addLayout(h_btns)

    def _toggle_spinners(self):
        """
        Enables/Disables the timers based on Radio Button selection.
        """
        is_countdown = not self.rad_now.isChecked()
        self.spin_min.setEnabled(is_countdown)
        self.spin_sec.setEnabled(is_countdown)

    def get_data(self):
        """
        Returns a clean dictionary of the user's choices.
        """
        return {
            "reason": self.combo_reason.currentText(),
            "restart_process": self.chk_restart.isChecked(),
            "override_watchdog": self.chk_override.isChecked(),
            "immediate": self.rad_now.isChecked(),
            "minutes": self.spin_min.value(),
            "seconds": self.spin_sec.value()
        }