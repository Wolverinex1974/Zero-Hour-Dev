# ui/style_factory.py - Zero Hour Aesthetic Factory
# Defines the Industrial Dark theme for the Master Suite.

INDUSTRIAL_STYLE = """
QMainWindow, QWidget { 
    background-color: #1e1e1e; 
    color: #e0e0e0; 
    font-family: 'Segoe UI', Arial, sans-serif; 
}
QTabWidget::pane { 
    border: 1px solid #333333; 
    background: #1e1e1e; 
    top: -1px;
}
QTabBar::tab { 
    background: #2d2d2d; 
    color: #aaaaaa; 
    padding: 12px 30px; 
    border: 1px solid #1a1a1a; 
    margin-right: 2px;
}
QTabBar::tab:selected { 
    background: #3d3d3d; 
    color: #ffffff; 
    border-bottom: 2px solid #9b59b6;
}

/* BUTTONS: SOLID COLOR BLOCKS */
QPushButton { 
    background-color: #3d3d3d; 
    color: #ffffff; 
    border: none; 
    padding: 8px 15px; 
    font-weight: bold;
    text-transform: uppercase;
}
QPushButton:hover { background-color: #4d4d4d; }

#btn_commit_deploy { background-color: #9b59b6; color: white; }
#btn_commit_deploy:hover { background-color: #8e44ad; }

#btn_start_server { background-color: #27ae60; color: white; }
#btn_start_server:hover { background-color: #2ecc71; }

#btn_stop_server { background-color: #c0392b; color: white; }
#btn_stop_server:hover { background-color: #e74c3c; }

#btn_publish_launcher { background-color: #9b59b6; color: white; }
#btn_publish_admin { background-color: #e67e22; color: white; }

#btn_save_news { background-color: #2980b9; color: white; }

/* TABLE STYLING */
QTableWidget { 
    background-color: #252525; 
    gridline-color: #333333; 
    color: #ffffff; 
    border: 1px solid #333333;
    selection-background-color: #3d3d3d;
}
QHeaderView::section { 
    background-color: #2d2d2d; 
    color: #aaaaaa; 
    padding: 10px; 
    border: 1px solid #1e1e1e; 
    font-weight: bold;
}

/* INPUTS */
QTextEdit, QPlainTextEdit, QLineEdit { 
    background-color: #121212; 
    color: #2ecc71; 
    border: 1px solid #333333; 
    font-family: 'Consolas', monospace;
}

QGroupBox { 
    border: 1px solid #333333; 
    margin-top: 15px; 
    padding-top: 15px; 
    color: #2ecc71; 
    font-weight: bold; 
}
QProgressBar { border: 1px solid #333; background: #222; text-align: center; color: white; }
QProgressBar::chunk { background-color: #2ecc71; }
"""