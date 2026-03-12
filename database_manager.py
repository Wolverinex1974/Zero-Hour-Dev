# =========================================================
# ZERO HOUR CORE: DATABASE MANAGER - v23.2
# =========================================================
# ROLE: Global Persistent Memory (SQLite Engine)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 12 UPDATE:
# FEATURE: Added 'shop_manifest' table for Sovereign Storefront.
# FEATURE: Added 'fetch_full_ledger' for UI Tab 6 visualization.
# FEATURE: Added Storefront management methods.
# =========================================================

import sqlite3
import os
import logging
from datetime import datetime

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class DatabaseManager:
    """
    The Master Custodian of player data, economy, and storefronts.
    Handles high-speed IO for player career stats, financial audit logs,
    and the Sovereign Storefront manifest.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.db_path = os.path.join(self.base_dir, "paradoxal_master.db")
        
        # Initialize the connection
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """
        Connects to SQLite and enforces industrial-grade performance settings.
        """
        try:
            # Connect to the physical DB file
            self.conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False # Required for multi-threaded UI/Reactor access
            )
            
            # --- INDUSTRIAL PERFORMANCE OPTIMIZATION ---
            # WAL mode allows concurrent reads/writes without locking the UI
            self.conn.execute("PRAGMA journal_mode=WAL;")
            # Synchronous=NORMAL balances speed and crash safety for live environments
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            # Enable Foreign Key constraints for data integrity
            self.conn.execute("PRAGMA foreign_keys = ON;")
            
            self._initialize_tables()
            log.info(f"[DATABASE] Master Vault operational at: {self.db_path}")
            
        except Exception as e:
            log.critical(f"[DATABASE] Failed to initialize Master Vault: {str(e)}")

    def _initialize_tables(self):
        """
        Creates the sovereign data structures for the Paradoxal Ecosystem.
        """
        cursor = self.conn.cursor()
        
        # 1. THE PLAYER LEDGER
        # Links Platform ID (EOS/Steam) to their global identity.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                platform_id TEXT PRIMARY KEY,
                player_name TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                current_level INTEGER DEFAULT 1,
                total_playtime_mins INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0
            )
        """)
        
        # 2. THE ECONOMY VAULT
        # Stores global Zombie Bucks tied to the Platform ID.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                platform_id TEXT PRIMARY KEY,
                zombie_bucks INTEGER DEFAULT 0,
                lifetime_earned INTEGER DEFAULT 0,
                lifetime_spent INTEGER DEFAULT 0,
                FOREIGN KEY (platform_id) REFERENCES players (platform_id)
            )
        """)

        # 3. THE TRANSACTION AUDIT LEDGER
        # Industrial tracking of every coin. Essential for Monetization.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_id TEXT,
                amount INTEGER,
                reason TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (platform_id) REFERENCES players (platform_id)
            )
        """)
        
        # 4. CAREER TELEMETRY
        # Detailed stats extracted from the Sovereign Agent (DLL) logs.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                platform_id TEXT PRIMARY KEY,
                zombie_kills INTEGER DEFAULT 0,
                player_kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                total_xp_earned INTEGER DEFAULT 0,
                FOREIGN KEY (platform_id) REFERENCES players (platform_id)
            )
        """)
        
        # 5. SOVEREIGN STOREFRONT MANIFEST (NEW)
        # Holds the items available for purchase via /buy or Launcher.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_manifest (
                item_id TEXT PRIMARY KEY,
                display_name TEXT,
                cost INTEGER,
                category TEXT DEFAULT 'General',
                stock INTEGER DEFAULT -1
            )
        """)
        
        self.conn.commit()
        log.info("[DATABASE] Sovereignty Tables (v16.0.25) Verified.")

    # --- SOVEREIGN TELEMETRY INTEGRATION ---

    def sync_player_activity(self, platform_id, name=None, level=None):
        """
        Called by the LogTailer when [ZH_CORE] telemetry is detected.
        Updates level and timestamps in a single atomic operation.
        """
        cursor = self.conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if player exists to avoid overwriting name with None
        cursor.execute("SELECT player_name, current_level FROM players WHERE platform_id = ?", (platform_id,))
        existing = cursor.fetchone()

        if not existing:
            # New Player Discovery
            cursor.execute("""
                INSERT INTO players (platform_id, player_name, first_seen, last_seen, current_level)
                VALUES (?, ?, ?, ?, ?)
            """, (platform_id, name if name else "Unknown Survivor", now, now, level if level else 1))
        else:
            # Update Existing Player
            new_name = name if name else existing[0]
            new_level = level if level else existing[1]
            cursor.execute("""
                UPDATE players SET 
                    player_name = ?, 
                    last_seen = ?, 
                    current_level = ?
                WHERE platform_id = ?
            """, (new_name, now, new_level, platform_id))
        
        # Ensure child table entries exist
        cursor.execute("INSERT OR IGNORE INTO economy (platform_id) VALUES (?)", (platform_id,))
        cursor.execute("INSERT OR IGNORE INTO player_stats (platform_id) VALUES (?)", (platform_id,))
        
        self.conn.commit()

    def increment_stat(self, platform_id, stat_name, amount=1):
        """
        Directly increments a specific stat (zombie_kills, deaths, etc.)
        Triggered by [ZH_CORE] | KILL logs.
        """
        valid_stats = ["zombie_kills", "player_kills", "deaths", "total_xp_earned"]
        if stat_name not in valid_stats:
            return

        cursor = self.conn.cursor()
        query = f"UPDATE player_stats SET {stat_name} = {stat_name} + ? WHERE platform_id = ?"
        cursor.execute(query, (amount, platform_id))
        self.conn.commit()

    def add_playtime(self, platform_id, minutes=1):
        """
        Triggered by [ZH_CORE] | HEARTBEAT logs.
        Tracks total career time for the 'Time Pillar' reward system.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE players SET total_playtime_mins = total_playtime_mins + ? 
            WHERE platform_id = ?
        """, (minutes, platform_id))
        self.conn.commit()

    # --- ECONOMY (ZOMBIE BUCKS) LOGIC ---

    def get_balance(self, platform_id):
        """ Retrieves the current Zombie Bucks for a player. """
        cursor = self.conn.cursor()
        cursor.execute("SELECT zombie_bucks FROM economy WHERE platform_id = ?", (platform_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def adjust_balance(self, platform_id, amount, reason=""):
        """
        The Banker: Adds or subtracts Zombie Bucks.
        Records every change in the Audit Ledger for monetization security.
        """
        cursor = self.conn.cursor()
        current = self.get_balance(platform_id)
        new_total = current + amount
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if new_total < 0:
            new_total = 0
            
        # 1. Update Current Balance
        cursor.execute("UPDATE economy SET zombie_bucks = ? WHERE platform_id = ?", (new_total, platform_id))
        
        # 2. Update Lifetime Stats
        if amount > 0:
            cursor.execute("UPDATE economy SET lifetime_earned = lifetime_earned + ? WHERE platform_id = ?", (amount, platform_id))
        elif amount < 0:
            cursor.execute("UPDATE economy SET lifetime_spent = lifetime_spent + ? WHERE platform_id = ?", (abs(amount), platform_id))
            
        # 3. Log to Transaction Audit Ledger
        cursor.execute("""
            INSERT INTO transactions (platform_id, amount, reason, timestamp)
            VALUES (?, ?, ?, ?)
        """, (platform_id, amount, reason, now))
            
        self.conn.commit()
        log.info(f"[ECONOMY] Transaction: {platform_id} | Amount: {amount} | Reason: {reason}")
        return new_total

    # --- UI VISUALIZATION & REPORTING (NEW) ---

    def fetch_full_ledger(self):
        """
        Retrieves a joined dataset of ALL players for the Tab 6 UI.
        Combines Identity, Economy, and Combat Stats.
        Returns: List of Tuples
        """
        cursor = self.conn.cursor()
        # Left Joins ensure we get players even if stats/economy are somehow missing
        query = """
            SELECT 
                p.player_name,
                p.platform_id,
                e.zombie_bucks,
                p.current_level,
                s.zombie_kills,
                s.deaths,
                p.last_seen
            FROM players p
            LEFT JOIN economy e ON p.platform_id = e.platform_id
            LEFT JOIN player_stats s ON p.platform_id = s.platform_id
            ORDER BY p.last_seen DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

    def fetch_transaction_history(self, limit=100):
        """ Retrieves the latest audit logs for the Admin Panel. """
        cursor = self.conn.cursor()
        query = """
            SELECT t.timestamp, p.player_name, t.amount, t.reason
            FROM transactions t
            LEFT JOIN players p ON t.platform_id = p.platform_id
            ORDER BY t.timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()

    # --- SOVEREIGN STOREFRONT MANAGEMENT (NEW) ---

    def add_shop_item(self, item_id, display_name, cost, category="General"):
        """
        Adds or updates an item in the Sovereign Storefront.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO shop_manifest (item_id, display_name, cost, category)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                display_name = excluded.display_name,
                cost = excluded.cost,
                category = excluded.category
        """, (item_id, display_name, cost, category))
        self.conn.commit()
        log.info(f"[STORE] Updated Item: {display_name} ({cost} ZB)")

    def get_shop_manifest(self):
        """ Returns all items in the store for the UI or Launcher. """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM shop_manifest ORDER BY category, display_name")
        return cursor.fetchall()

    def get_item_cost(self, item_id):
        """ Returns the cost of a specific item ID. Returns None if not found. """
        cursor = self.conn.cursor()
        cursor.execute("SELECT cost, display_name FROM shop_manifest WHERE item_id = ?", (item_id,))
        return cursor.fetchone()

    def close(self):
        """ Gracefully shuts down the database connection. """
        if self.conn:
            self.conn.close()
            log.info("[DATABASE] Master Vault closed.")