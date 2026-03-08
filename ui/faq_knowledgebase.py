# =========================================================
# ZERO HOUR UI: KNOWLEDGE BASE - v23.0
# =========================================================
# ROLE: Embedded Documentation & Help Center
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 15 NEW MODULE:
# FEATURE: Offline FAQ system to pass "The Wife Test".
# CONTENT: Covers GitHub Setup, Mod Workflow, and Port Forwarding.
# =========================================================

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QListWidget, 
    QTextEdit, 
    QSplitter, 
    QLabel, 
    QFrame
)

class KnowledgeBaseUI(QWidget):
    """
    The 'Brain' of the Help Tab.
    Provides a searchable (future) and navigable documentation interface.
    """
    def __init__(self):
        super().__init__()
        self.articles = {}
        self.setup_ui()
        self.load_knowledge()

    def setup_ui(self):
        """ Builds the Split-View Layout. """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background-color: #2c3e50; border-bottom: 2px solid #34495e;")
        self.header_frame.setMaximumHeight(50)
        self.h_layout = QHBoxLayout(self.header_frame)
        
        self.lbl_title = QLabel("OPERATOR SURVIVAL GUIDE")
        self.lbl_title.setStyleSheet("color: #ecf0f1; font-weight: bold; font-size: 14px;")
        self.h_layout.addWidget(self.lbl_title)
        
        self.main_layout.addWidget(self.header_frame)

        # Splitter (Left: Topics, Right: Content)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDE: TOPICS ---
        self.list_topics = QListWidget()
        self.list_topics.setFixedWidth(250)
        self.list_topics.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                color: #bdc3c7;
                border: none;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #2980b9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        self.list_topics.currentRowChanged.connect(self.display_topic)
        self.splitter.addWidget(self.list_topics)

        # --- RIGHT SIDE: READING PANE ---
        self.txt_content = QTextEdit()
        self.txt_content.setReadOnly(True)
        self.txt_content.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ecf0f1;
                border: none;
                padding: 20px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.splitter.addWidget(self.txt_content)
        
        # Adjust Splitter Ratio
        self.splitter.setStretchFactor(1, 4) # Give content 4x space
        
        self.main_layout.addWidget(self.splitter)

    def load_knowledge(self):
        """ Populates the Article Database. """
        
        # 1. QUICK START
        self.add_article("1. Quick Start Guide", """
            <h2 style='color: #2ecc71'>Zero Hour Quick Start</h2>
            <p>Welcome, Admin. Follow these 3 steps to get online fast:</p>
            <ol>
                <li><b>SETUP TAB:</b> Create a profile. Click "ADOPT EXISTING" if you have a server, or "DOWNLOAD" to make a new one.</li>
                <li><b>IDENTITY:</b> Enter a Port (default 26900) and your GitHub Repo (see 'GitHub Setup'). Click <b>SAVE IDENTITY</b>.</li>
                <li><b>SERVER SETTINGS:</b> Go to Tab 5. Uncheck 'Telnet' if you don't use it, or set a Password. Click <b>COMMIT SETTINGS</b>.</li>
                <li><b>LAUNCH:</b> Go to 'Server Logs' and click <b>START SERVER</b>.</li>
            </ol>
        """)

        # 2. GITHUB SETUP
        self.add_article("2. GitHub Setup (Cloud)", """
            <h2 style='color: #9b59b6'>Connecting to the Cloud</h2>
            <p>Zero Hour uses GitHub to store your mods. This allows players to download them automatically.</p>
            <h3 style='color: #3498db'>Step A: Create a Repository</h3>
            <ul>
                <li>Go to GitHub.com and create a new account (Free).</li>
                <li>Create a <b>New Repository</b>. Name it anything (e.g., 'My7D2D-Server').</li>
                <li>Make sure it is <b>PUBLIC</b> (so players can download).</li>
            </ul>
            <h3 style='color: #3498db'>Step B: Get a Token</h3>
            <ul>
                <li>Go to GitHub Settings -> Developer Settings -> Personal Access Tokens -> Tokens (Classic).</li>
                <li>Generate New Token. Give it 'Repo' permissions (Full Control).</li>
                <li><b>COPY THE TOKEN IMMEDIATELY.</b> You won't see it again.</li>
            </ul>
            <h3 style='color: #3498db'>Step C: Link Zero Hour</h3>
            <ul>
                <li>In Zero Hour -> SETUP Tab: Paste your <b>Repo Name</b> (e.g., 'User/Repo').</li>
                <li>The system will ask for your <b>Token</b> via a popup on first Sync.</li>
            </ul>
        """)

        # 3. MOD WORKFLOW
        self.add_article("3. Modding Workflow", """
            <h2 style='color: #e67e22'>The Iron Bridge Protocol</h2>
            <p>Managing mods requires two distinct actions:</p>
            <hr>
            <h3 style='color: #f1c40f'>Phase 1: SYNC (The Cargo)</h3>
            <p>Clicking <b>SYNC SERVER TO CLOUD</b> (Tab 2) does the heavy lifting:</p>
            <ul>
                <li>It scans your local 'Mods' folder.</li>
                <li>It Zips up any new mods.</li>
                <li>It Uploads them to your GitHub Storage.</li>
                <li><i>NOTE: This does NOT tell players to download them yet.</i></li>
            </ul>
            <br>
            <h3 style='color: #f1c40f'>Phase 2: PUBLISH (The Instructions)</h3>
            <p>Clicking <b>PUBLISH MANIFEST</b> (Purple Button) is the final step:</p>
            <ul>
                <li>It creates a list (JSON) of all your mods.</li>
                <li>It sends this list to the Cloud.</li>
                <li><b>The Launcher reads THIS list.</b></li>
            </ul>
            <p><b>Rule of Thumb:</b> Always Sync first, Publish second.</p>
        """)

        # 4. PORT FORWARDING
        self.add_article("4. Ports & Networking", """
            <h2 style='color: #e74c3c'>Opening the Gates</h2>
            <p>For friends to join, you must forward ports in your Router.</p>
            <ul>
                <li><b>Game Port (UDP):</b> Default 26900. Required for players to connect.</li>
                <li><b>Steam Browser (UDP):</b> Game Port + 1 (26901).</li>
                <li><b>Telnet Port (TCP):</b> Default 8081. Used by Zero Hour to manage the server. <b>DO NOT FORWARD THIS.</b> Keep it local for security.</li>
            </ul>
        """)

        # 5. TROUBLESHOOTING
        self.add_article("5. Troubleshooting", """
            <h2 style='color: #95a5a6'>Common Errors</h2>
            <p><b>"Existing connection forcibly closed"</b></p>
            <ul>
                <li>Means the Telnet connection dropped. Zero Hour v16.2.6+ auto-reconnects. Ignore unless persistent.</li>
            </ul>
            <p><b>"Heartbeat Failed"</b></p>
            <ul>
                <li>Zero Hour cannot find '7DaysToDieServer.exe'. Check your installation path in the Setup Tab.</li>
            </ul>
            <p><b>"GitHub Upload Failed"</b></p>
            <ul>
                <li>Check your Token permissions.</li>
                <li>Check if the file is over 2GB (Splitter handles this, but GitHub has limits).</li>
            </ul>
        """)

        # Select first item
        self.list_topics.setCurrentRow(0)

    def add_article(self, title, content):
        """ Adds an entry to the system. """
        self.articles[title] = content
        self.list_topics.addItem(title)

    def display_topic(self, current_row_int_or_item):
        """ Updates the text view. """
        # Handle both signal types (int index or QListWidgetItem)
        if isinstance(current_row_int_or_item, int):
            row = current_row_int_or_item
            if row < 0: return
            title = self.list_topics.item(row).text()
        else:
            title = current_row_int_or_item.text()
            
        content = self.articles.get(title, "<h1>Content Not Found</h1>")
        self.txt_content.setHtml(content)