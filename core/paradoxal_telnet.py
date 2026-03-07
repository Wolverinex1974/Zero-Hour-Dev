# =========================================================
# ZERO HOUR CORE: PARADOXAL TELNET - v20.8
# =========================================================
# ROLE: Sovereign Socket Wrapper (Persistent & Robust)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 14 FIX:
# FEATURE: Transformed into a Stateful Client (Keep-Alive Capable).
# REASON: Stops 'Existing connection forcibly closed' errors by
#         reusing the same socket instead of reconnecting 100x/min.
# =========================================================

import socket
import time
import logging
import select

log = logging.getLogger("Paradoxal")

class ParadoxalTelnet:
    """
    A robust, persistent Telnet client for 7 Days to Die.
    Maintains a single connection session to avoid being banned 
    by the server's DoS protection.
    """
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self._buffer = b""
        self.is_authenticated = False

    def connect(self, password):
        """
        Establishes the connection and performs the handshake.
        Returns True if successful.
        """
        self.close() # Ensure clean slate
        self._buffer = b""
        
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
            
            # 1. Wait for "Please enter password:"
            # 7D2D sends this immediately upon connection
            welcome = self.read_until(b"password:", timeout=5)
            if b"password:" not in welcome.lower():
                log.warning(f"[TELNET] Unexpected handshake: {welcome}")
                # We might already be authenticated if it's a weird reconnect, but usually not.
            
            # 2. Send Password
            self.write(password.encode('ascii') + b"\r\n")
            
            # 3. Wait for confirmation (Logon successful)
            # We look for the prompt or specific success text
            response = self.read_until(b"Logon successful", timeout=5)
            
            if b"Logon successful" in response or b"Connected" in response:
                self.is_authenticated = True
                return True
            else:
                log.error(f"[TELNET] Auth failed. Response: {response}")
                self.close()
                return False
                
        except Exception as e:
            log.error(f"[TELNET] Connection Error: {e}")
            self.close()
            return False

    def send_command(self, command):
        """
        Sends a command and returns the response.
        Auto-detects broken pipes.
        """
        if not self.sock:
            return None

        try:
            # Clear previous buffer junk (e.g. log streams)
            self.read_very_eager()
            
            # Send Command
            self.write(command.encode('ascii') + b"\r\n")
            
            # Read Response
            # We don't know exactly when it ends, so we read until silent or timeout.
            # For 7D2D, getting data back usually implies success.
            time.sleep(0.1) # Grace period for server processing
            response = self.read_very_eager()
            
            return response.decode('ascii', errors='ignore')
            
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            log.warning(f"[TELNET] Socket died during command: {e}")
            self.close()
            return None

    def read_until(self, match, timeout=None):
        """
        Reads until 'match' bytes are found.
        """
        if not self.sock: return b""
        
        if timeout is None: timeout = self.timeout
        self.sock.settimeout(timeout)
        start_time = time.time()
        
        while match not in self._buffer:
            if (time.time() - start_time) > timeout:
                break
            
            try:
                chunk = self.sock.recv(4096)
                if not chunk: break # EOF
                self._buffer += chunk
            except socket.timeout:
                break
            except Exception:
                break
        
        if match in self._buffer:
            index = self._buffer.find(match) + len(match)
            result = self._buffer[:index]
            self._buffer = self._buffer[index:]
            return result
        
        # Timeout return
        result = self._buffer
        self._buffer = b""
        return result

    def write(self, data):
        """ Writes bytes to the socket. """
        if self.sock:
            self.sock.sendall(data)

    def read_very_eager(self):
        """ 
        Reads everything currently in the pipe. 
        Uses select() to avoid blocking if empty.
        """
        if not self.sock: return b""
        
        out = b""
        while True:
            try:
                # Check if data is available (non-blocking check)
                ready_to_read, _, _ = select.select([self.sock], [], [], 0.1)
                if not ready_to_read:
                    break
                    
                chunk = self.sock.recv(4096)
                if not chunk: break # Connection closed
                out += chunk
            except Exception:
                break
        
        return out

    def close(self):
        """ Clean shutdown. """
        self.is_authenticated = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception:
                pass
            self.sock = None

# Alias
Telnet = ParadoxalTelnet