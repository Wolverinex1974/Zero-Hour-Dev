# =========================================================
# ZERO HOUR CORE: ECONOMY PARSER - v21.2
# =========================================================
# ROLE: Mathematical Engine & Commerce Transactions
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 16.5 UPDATE:
# NEW FILE: Extracted from reactor_engine.py to prevent 
#           LogTailer thread stalling during heavy load.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# =========================================================

import logging
import re
from PySide6.QtCore import QObject, Signal, Slot

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

class EconomyParser(QObject):
    """
    The Mathematical Engine for Zero Hour Commerce and Identity.
    Catches raw log lines from the LogTailer and processes them
    without blocking the file reader thread.
    """
    
    # Broadcasts commands back to the Telnet Socket
    telnet_signal = Signal(str)
    
    # Pings the UI to update Tab 6 in real-time
    ledger_signal = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        # --- REWARD CONFIGURATION ---
        self.reward_kill = 50
        self.reward_level = 500
        self.reward_heartbeat = 25
        
        # Identity Map: Resolves in-game names to EOS IDs for /pay commands
        self.player_map = dict()

    @Slot(str)
    def process_log_line(self, line):
        """
        Primary intake slot. Routes the raw string to the appropriate parser.
        Executed entirely decoupled from the file-reading thread.
        """
        # 1. Parse Standard Game Logs (Chat & Identity)
        self._parse_standard_logs(line)
        
        # 2. Parse Sovereign Telemetry (DLL Hooks)
        if "ZH_CORE" in line:
            self._process_sovereign_telemetry(line)

    def _parse_standard_logs(self, line):
        """ Watches for Player Connections and Chat Commands. """
        
        # --- IDENTITY MAPPING ---
        if "Player connected" in line:
            name_match = re.search(r"name=(.+?),", line)
            id_match = re.search(r"platformid=(.+?),", line)
            
            if not id_match:
                id_match = re.search(r"steamid=(.+?),", line)
            
            if name_match and id_match:
                name = name_match.group(1).lower()
                pid = id_match.group(1)
                
                if not pid.startswith("EOS_") and not pid.startswith("Steam_"):
                    if len(pid) > 17:
                        pid = f"EOS_{pid}"
                    else:
                        pid = f"Steam_{pid}"
                
                # Safely update dictionary without brackets
                self.player_map.__setitem__(name, pid)
                
                self.db_manager.sync_player_activity(pid, name=name_match.group(1))
                self.ledger_signal.emit()
                log.info(f" Identity Mapped: {name} -> {pid}")

        # --- CHAT COMMANDS ---
        if "INF Chat" in line and "': /" in line:
            try:
                # Regex extracts PID, Player Name, and the slash command
                pattern = r"Chat \(from '(?P<pid>.*?)',.*?\): '(?P<name>.*?)': (?P<msg>/.*)"
                match = re.search(pattern, line)
                
                if match:
                    pid = match.group("pid")
                    msg = match.group("msg").strip()
                    self._handle_chat_command(pid, msg)
            except Exception as e:
                log.warning(f" Chat Parse Error: {e}")

    def _handle_chat_command(self, platform_id, message):
        """ Processes in-game slash commands intercepted from the log. """
        parts = message.split(" ")
        
        # Safe extraction without brackets
        raw_cmd = "unknown"
        if len(parts) > 0:
            raw_cmd = parts.pop(0).lower()
            
        args = parts

        # --- COMMAND: /buy ---
        if raw_cmd.startswith("/buy"):
            
            alias = raw_cmd.replace("/buy", "") 
            count = 1
            
            # Case A: /buy 762 20 (Alias is separated by a space)
            if not alias:
                if len(args) == 0:
                    self.telnet_signal.emit(f'pm {platform_id} "Usage: /buy <item> <amount>"')
                    return
                    
                alias = args.pop(0).lower()
                
                # Check if the next argument exists and is a number
                if len(args) > 0:
                    next_arg = args.__getitem__(0)
                    if next_arg.isdigit():
                        count_str = args.pop(0)
                        count = int(count_str)
            
            # Case B: /buy762 20 (Alias is jammed into the command)
            else:
                if len(args) > 0:
                    next_arg = args.__getitem__(0)
                    if next_arg.isdigit():
                        count_str = args.pop(0)
                        count = int(count_str)

            # Sanity Limits
            if count < 1: 
                count = 1
            if count > 1000: 
                count = 1000

            manifest = self.db_manager.get_shop_manifest()
            target_item = None
            
            # Search Priority 1: Exact Alias Match
            for item in manifest:
                item_alias = item.__getitem__(1)
                if item_alias.lower() == alias:
                    target_item = item
                    break
            
            # Search Priority 2: Substring Match
            if not target_item:
                for item in manifest:
                    item_alias = item.__getitem__(1)
                    if alias in item_alias.lower():
                        target_item = item
                        break

            if target_item:
                item_id = target_item.__getitem__(0)
                display_name = target_item.__getitem__(1)
                cost = target_item.__getitem__(2)
                total_cost = cost * count
                
                balance = self.db_manager.get_balance(platform_id)
                
                if balance >= total_cost:
                    self.db_manager.adjust_balance(platform_id, -total_cost, f"Bought {count}x {display_name}")
                    self.ledger_signal.emit() 
                    
                    self.telnet_signal.emit(f'give {platform_id} {item_id} {count}')
                    self.telnet_signal.emit(f'pm {platform_id} "Purchased {count}x {display_name} for {total_cost} ZB."')
                    log.info(f" {platform_id} bought {count}x {item_id}")
                else:
                    self.telnet_signal.emit(f'pm {platform_id} "Insufficient Funds. Cost: {total_cost} | Balance: {balance}"')
            else:
                self.telnet_signal.emit(f'pm {platform_id} "Item \'{alias}\' not found in store."')

    def _process_sovereign_telemetry(self, line):
        """ Handles the handshake between the C# DLL and the Python Database. """
        try:
            parts = line.split("|")
            
            if len(parts) < 3:
                return

            # Clean parts array
            clean_parts = list()
            for p in parts:
                clean_parts.append(p.strip())

            # Safe extraction
            msg_type = clean_parts.__getitem__(1)
            platform_id = clean_parts.__getitem__(2)

            if msg_type == "KILL":
                if len(clean_parts) > 3:
                    victim = clean_parts.__getitem__(3)
                    self.db_manager.adjust_balance(platform_id, self.reward_kill, f"Kill: {victim}")
                    self.db_manager.increment_stat(platform_id, "zombie_kills", 1)
                    self.ledger_signal.emit()

            elif msg_type == "LEVEL_UP":
                if len(clean_parts) > 3:
                    level_str = clean_parts.__getitem__(3)
                    if level_str.isdigit():
                        level = int(level_str)
                        self.db_manager.adjust_balance(platform_id, self.reward_level, f"Level Up: {level}")
                        self.db_manager.sync_player_activity(platform_id, level=level)
                        self.ledger_signal.emit()

            elif msg_type == "HEARTBEAT":
                if len(clean_parts) > 3:
                    level_str = clean_parts.__getitem__(3)
                    if level_str.isdigit():
                        level = int(level_str)
                        self.db_manager.adjust_balance(platform_id, self.reward_heartbeat, "Active Playtime")
                        self.db_manager.add_playtime(platform_id, 1)
                        self.db_manager.sync_player_activity(platform_id, level=level)
                        self.ledger_signal.emit()

            elif msg_type == "REQ_BANK":
                balance = self.db_manager.get_balance(platform_id)
                cmd = f'pm {platform_id} " Your current balance:{balance} ZombieBucks"'
                self.telnet_signal.emit(cmd)
                log.info(f" Handshake Complete: {platform_id} balance check.")

            elif msg_type == "REQ_PAY":
                if len(clean_parts) > 4:
                    target_name = clean_parts.__getitem__(3).lower()
                    amount_str = clean_parts.__getitem__(4)
                    
                    if amount_str.isdigit():
                        amount = int(amount_str)
                        
                        current_balance = self.db_manager.get_balance(platform_id)
                        if current_balance < amount:
                            self.telnet_signal.emit(f'pm {platform_id} " Insufficient funds! Balance: {current_balance}"')
                            return

                        target_id = self.player_map.get(target_name)
                        
                        if target_id:
                            self.db_manager.adjust_balance(platform_id, -amount, f"Paid {target_name}")
                            self.db_manager.adjust_balance(target_id, amount, f"Received from {platform_id}")
                            self.ledger_signal.emit()
                            
                            self.telnet_signal.emit(f'pm {platform_id} " You paid {target_name} {amount} ZombieBucks."')
                            self.telnet_signal.emit(f'pm {target_id} " You received {amount} ZombieBucks from a friend."')
                            log.info(f" Transfer: {platform_id} -> {target_id} | Amount: {amount}")
                        else:
                            self.telnet_signal.emit(f'pm {platform_id} " Player \'{target_name}\' not found or offline."')

        except Exception as e:
            log.error(f" Telemetry Parsing Error: {str(e)}")