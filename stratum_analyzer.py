#!/usr/bin/env python3
"""
ZCash Stratum Protocol Analyzer
================================
This script connects to a ZCash mining pool and analyzes the stratum
protocol messages to understand exactly what format they expect.

Usage:
    python stratum_analyzer.py <pool_host> <pool_port> <wallet_address> [password]

Example:
    python stratum_analyzer.py zec.suprnova.cc 2142 t1YourWalletAddress x
"""

import socket
import json
import sys
import time
import ssl
from datetime import datetime

class StratumAnalyzer:
    def __init__(self, host, port, user, password="x", use_ssl=False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.use_ssl = use_ssl
        self.sock = None
        self.buffer = ""
        
        # Stratum state
        self.session_id = None
        self.extranonce1 = None
        self.extranonce1_size = 0
        self.extranonce2_size = 0
        self.difficulty = 1.0
        self.jobs = []
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        colors = {
            "INFO": "\033[97m",      # White
            "RECV": "\033[92m",      # Green
            "SEND": "\033[96m",      # Cyan
            "WARN": "\033[93m",      # Yellow
            "ERROR": "\033[91m",     # Red
            "ANALYSIS": "\033[95m",  # Magenta
        }
        reset = "\033[0m"
        color = colors.get(level, "\033[97m")
        print(f"{color}[{timestamp}] [{level}] {msg}{reset}")
    
    def connect(self):
        """Connect to the stratum server"""
        self.log(f"Connecting to {self.host}:{self.port}...")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            
            if self.use_ssl:
                context = ssl.create_default_context()
                self.sock = context.wrap_socket(self.sock, server_hostname=self.host)
            
            self.sock.connect((self.host, self.port))
            self.log(f"Connected successfully!", "INFO")
            return True
        except Exception as e:
            self.log(f"Connection failed: {e}", "ERROR")
            return False
    
    def send(self, data):
        """Send a JSON-RPC message"""
        msg = json.dumps(data) + "\n"
        self.log(f">>> {json.dumps(data)}", "SEND")
        self.sock.sendall(msg.encode())
    
    def recv_line(self):
        """Receive a single line from the server"""
        while "\n" not in self.buffer:
            try:
                chunk = self.sock.recv(4096).decode()
                if not chunk:
                    return None
                self.buffer += chunk
            except socket.timeout:
                return None
        
        line, self.buffer = self.buffer.split("\n", 1)
        return line
    
    def recv_json(self):
        """Receive and parse a JSON message"""
        line = self.recv_line()
        if line:
            self.log(f"<<< {line}", "RECV")
            try:
                return json.loads(line)
            except json.JSONDecodeError as e:
                self.log(f"JSON decode error: {e}", "ERROR")
        return None
    
    def subscribe(self):
        """Send mining.subscribe"""
        self.log("=" * 60, "ANALYSIS")
        self.log("STEP 1: SUBSCRIBING TO POOL", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        
        self.send({
            "id": 1,
            "method": "mining.subscribe",
            "params": ["stratum-analyzer/1.0"]
        })
        
        response = self.recv_json()
        if not response:
            self.log("No response to subscribe", "ERROR")
            return False
        
        if "result" in response and response["result"]:
            result = response["result"]
            
            self.log("", "ANALYSIS")
            self.log("SUBSCRIBE RESPONSE ANALYSIS:", "ANALYSIS")
            self.log(f"  Raw result: {json.dumps(result, indent=2)}", "ANALYSIS")
            
            # Try to parse ZCash format: [session_or_null, extranonce1, extranonce2_size]
            # Or Bitcoin format: [[subscriptions], extranonce1, extranonce2_size]
            
            if isinstance(result, list):
                if len(result) >= 2:
                    # Check if first element is a string (ZCash) or array (Bitcoin)
                    if isinstance(result[0], str) or result[0] is None:
                        # ZCash format
                        self.session_id = result[0]
                        self.extranonce1 = result[1] if len(result) > 1 else None
                        self.extranonce2_size = result[2] if len(result) > 2 else 0
                        self.log(f"  Format: ZCash stratum", "ANALYSIS")
                    else:
                        # Bitcoin format
                        self.session_id = None
                        self.extranonce1 = result[1] if len(result) > 1 else None
                        self.extranonce2_size = result[2] if len(result) > 2 else 0
                        self.log(f"  Format: Bitcoin stratum", "ANALYSIS")
                    
                    if self.extranonce1:
                        self.extranonce1_size = len(self.extranonce1) // 2
                    
                    self.log(f"  Session ID: {self.session_id}", "ANALYSIS")
                    self.log(f"  Extranonce1: {self.extranonce1} ({self.extranonce1_size} bytes)", "ANALYSIS")
                    self.log(f"  Extranonce2 size: {self.extranonce2_size} bytes", "ANALYSIS")
                    
                    # Calculate nonce structure
                    total_nonce = self.extranonce1_size + self.extranonce2_size
                    self.log(f"  Total nonce space: {total_nonce} bytes", "ANALYSIS")
                    
                    if total_nonce <= 32:
                        self.log(f"  → This matches ZCash's 32-byte nonce field!", "ANALYSIS")
                    
            return True
        else:
            error = response.get("error", "Unknown error")
            self.log(f"Subscribe failed: {error}", "ERROR")
            return False
    
    def authorize(self):
        """Send mining.authorize"""
        self.log("", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        self.log("STEP 2: AUTHORIZING WORKER", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        
        self.send({
            "id": 2,
            "method": "mining.authorize",
            "params": [self.user, self.password]
        })
        
        # May receive difficulty or job before auth response
        while True:
            response = self.recv_json()
            if not response:
                self.log("No response to authorize", "ERROR")
                return False
            
            # Handle methods (difficulty, notify)
            if "method" in response:
                self.handle_method(response)
                continue
            
            # Check for auth response
            if response.get("id") == 2:
                if response.get("result") == True:
                    self.log("Authorization successful!", "ANALYSIS")
                    return True
                else:
                    error = response.get("error", "Unknown error")
                    self.log(f"Authorization failed: {error}", "ERROR")
                    return False
    
    def handle_method(self, msg):
        """Handle incoming method calls from pool"""
        method = msg.get("method", "")
        params = msg.get("params", [])
        
        if method == "mining.set_difficulty":
            self.difficulty = params[0] if params else 1.0
            self.log(f"  Pool set difficulty: {self.difficulty}", "ANALYSIS")
            
        elif method == "mining.notify":
            self.analyze_notify(params)
    
    def analyze_notify(self, params):
        """Analyze mining.notify parameters to understand job format"""
        self.log("", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        self.log("MINING.NOTIFY ANALYSIS (Job Parameters)", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        
        self.log(f"Number of parameters: {len(params)}", "ANALYSIS")
        
        # Detect format based on parameter structure
        # ZCash: [job_id, version, prevhash, merkle_root, reserved, ntime, nbits, clean]
        # Bitcoin: [job_id, prevhash, coinb1, coinb2, merkle[], version, nbits, ntime, clean]
        
        is_zcash = False
        
        if len(params) >= 5:
            # Check if param[4] is a string (ZCash reserved field) or array (Bitcoin merkle)
            if isinstance(params[4], str):
                is_zcash = True
                self.log("", "ANALYSIS")
                self.log("DETECTED: ZCash Stratum Format!", "ANALYSIS")
                self.log("-" * 40, "ANALYSIS")
                
                job_id = params[0] if len(params) > 0 else None
                version = params[1] if len(params) > 1 else None
                prevhash = params[2] if len(params) > 2 else None
                merkle_root = params[3] if len(params) > 3 else None
                reserved = params[4] if len(params) > 4 else None
                ntime = params[5] if len(params) > 5 else None
                nbits = params[6] if len(params) > 6 else None
                clean = params[7] if len(params) > 7 else None
                
                self.log(f"  [0] job_id:      {job_id}", "ANALYSIS")
                self.log(f"  [1] version:     {version} ({len(version)//2 if version else 0} bytes)", "ANALYSIS")
                self.log(f"  [2] prevhash:    {prevhash[:16]}... ({len(prevhash)//2 if prevhash else 0} bytes)", "ANALYSIS")
                self.log(f"  [3] merkle_root: {merkle_root[:16]}... ({len(merkle_root)//2 if merkle_root else 0} bytes)", "ANALYSIS")
                self.log(f"  [4] reserved:    {reserved[:16]}... ({len(reserved)//2 if reserved else 0} bytes)", "ANALYSIS")
                self.log(f"  [5] ntime:       {ntime} ({len(ntime)//2 if ntime else 0} bytes)", "ANALYSIS")
                self.log(f"  [6] nbits:       {nbits} ({len(nbits)//2 if nbits else 0} bytes)", "ANALYSIS")
                self.log(f"  [7] clean:       {clean}", "ANALYSIS")
                
                # Store job for later analysis
                self.jobs.append({
                    "job_id": job_id,
                    "version": version,
                    "prevhash": prevhash,
                    "merkle_root": merkle_root,
                    "reserved": reserved,
                    "ntime": ntime,
                    "nbits": nbits,
                    "clean": clean
                })
                
            else:
                self.log("", "ANALYSIS")
                self.log("DETECTED: Bitcoin Stratum Format", "ANALYSIS")
                self.log("-" * 40, "ANALYSIS")
                
                job_id = params[0]
                prevhash = params[1]
                coinb1 = params[2]
                coinb2 = params[3]
                merkle = params[4]
                version = params[5]
                nbits = params[6]
                ntime = params[7]
                clean = params[8] if len(params) > 8 else False
                
                self.log(f"  [0] job_id:   {job_id}", "ANALYSIS")
                self.log(f"  [1] prevhash: {prevhash[:16]}...", "ANALYSIS")
                self.log(f"  [2] coinb1:   {coinb1[:32]}... ({len(coinb1)//2} bytes)", "ANALYSIS")
                self.log(f"  [3] coinb2:   {coinb2[:32]}... ({len(coinb2)//2} bytes)", "ANALYSIS")
                self.log(f"  [4] merkle:   {len(merkle)} branches", "ANALYSIS")
                self.log(f"  [5] version:  {version}", "ANALYSIS")
                self.log(f"  [6] nbits:    {nbits}", "ANALYSIS")
                self.log(f"  [7] ntime:    {ntime}", "ANALYSIS")
                self.log(f"  [8] clean:    {clean}", "ANALYSIS")
        
        # Now explain what mining.submit should look like
        self.log("", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        self.log("EXPECTED mining.submit FORMAT", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        
        if is_zcash:
            self.log("For ZCash pools, mining.submit typically expects:", "ANALYSIS")
            self.log("", "ANALYSIS")
            self.log('  ["worker_name", "job_id", "ntime", "extranonce2", "solution"]', "ANALYSIS")
            self.log("", "ANALYSIS")
            self.log("Where:", "ANALYSIS")
            self.log(f"  - worker_name: Your wallet/worker (e.g., '{self.user}')", "ANALYSIS")
            self.log(f"  - job_id:      From mining.notify param[0]", "ANALYSIS")
            self.log(f"  - ntime:       4 bytes hex (8 chars) - from param[5]", "ANALYSIS")
            self.log(f"  - extranonce2: {self.extranonce2_size} bytes hex ({self.extranonce2_size * 2} chars)", "ANALYSIS")
            self.log(f"  - solution:    Equihash solution (see below)", "ANALYSIS")
            self.log("", "ANALYSIS")
            self.log("SOLUTION FORMAT OPTIONS:", "ANALYSIS")
            self.log("-" * 40, "ANALYSIS")
            self.log("  Option A: Raw solution (1344 bytes = 2688 hex chars)", "ANALYSIS")
            self.log("  Option B: CompactSize prefix + solution:", "ANALYSIS")
            self.log("            fd4005 + <1344 bytes> = 1347 bytes = 2694 hex chars", "ANALYSIS")
            self.log("            (0xfd = 2-byte length follows, 0x0540 = 1344 in little-endian)", "ANALYSIS")
            self.log("", "ANALYSIS")
            self.log("NOTE: Different pools expect different formats!", "ANALYSIS")
            self.log("      Try both and see which one the pool accepts.", "ANALYSIS")
        else:
            self.log("For Bitcoin-style pools, mining.submit expects:", "ANALYSIS")
            self.log("", "ANALYSIS")
            self.log('  ["worker_name", "job_id", "extranonce2", "ntime", "nonce"]', "ANALYSIS")
    
    def listen_for_jobs(self, duration=10):
        """Listen for incoming messages for a duration"""
        self.log("", "ANALYSIS")
        self.log(f"Listening for {duration} seconds for additional messages...", "INFO")
        
        self.sock.settimeout(2)
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                msg = self.recv_json()
                if msg:
                    if "method" in msg:
                        self.handle_method(msg)
            except:
                pass
    
    def print_summary(self):
        """Print a summary of findings"""
        self.log("", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        self.log("SUMMARY - WHAT YOUR MINER NEEDS TO DO", "ANALYSIS")
        self.log("=" * 60, "ANALYSIS")
        
        self.log("", "ANALYSIS")
        self.log("1. HEADER CONSTRUCTION (140 bytes for ZCash):", "ANALYSIS")
        self.log("   Bytes 0-3:     Version (4 bytes)", "ANALYSIS")
        self.log("   Bytes 4-35:    PrevHash (32 bytes)", "ANALYSIS")
        self.log("   Bytes 36-67:   MerkleRoot (32 bytes)", "ANALYSIS")
        self.log("   Bytes 68-99:   Reserved (32 bytes)", "ANALYSIS")
        self.log("   Bytes 100-103: nTime (4 bytes)", "ANALYSIS")
        self.log("   Bytes 104-107: nBits (4 bytes)", "ANALYSIS")
        self.log("   Bytes 108-139: nNonce (32 bytes) = extranonce1 + extranonce2 + padding", "ANALYSIS")
        
        self.log("", "ANALYSIS")
        self.log("2. YOUR NONCE STRUCTURE:", "ANALYSIS")
        self.log(f"   extranonce1: {self.extranonce1} ({self.extranonce1_size} bytes) - from pool", "ANALYSIS")
        self.log(f"   extranonce2: {self.extranonce2_size} bytes - you generate this", "ANALYSIS")
        self.log(f"   padding:     {32 - self.extranonce1_size - self.extranonce2_size} bytes of zeros", "ANALYSIS")
        
        self.log("", "ANALYSIS")
        self.log("3. SUBMIT FORMAT:", "ANALYSIS")
        self.log('   {"method": "mining.submit", "params": [', "ANALYSIS")
        self.log(f'       "{self.user}",      // worker', "ANALYSIS")
        self.log('       "<job_id>",          // from mining.notify', "ANALYSIS")
        self.log('       "<ntime>",           // 8 hex chars', "ANALYSIS")
        self.log(f'       "<extranonce2>",    // {self.extranonce2_size * 2} hex chars', "ANALYSIS")
        self.log('       "<solution>"         // see solution format below', "ANALYSIS")
        self.log('   ], "id": 4}', "ANALYSIS")
        
        self.log("", "ANALYSIS")
        self.log("4. SOLUTION FORMAT (try both if rejected):", "ANALYSIS")
        self.log("   WITHOUT prefix: 2688 hex chars (raw 1344 bytes)", "ANALYSIS")
        self.log("   WITH prefix:    2694 hex chars (fd4005 + 1344 bytes)", "ANALYSIS")
        
        self.log("", "ANALYSIS")
        self.log("5. CURRENT POOL SETTINGS:", "ANALYSIS")
        self.log(f"   Difficulty: {self.difficulty}", "ANALYSIS")
        self.log(f"   Jobs received: {len(self.jobs)}", "ANALYSIS")
    
    def close(self):
        """Close the connection"""
        if self.sock:
            self.sock.close()
            self.log("Connection closed", "INFO")

def main():
    print("\n" + "=" * 60)
    print("  ZCash Stratum Protocol Analyzer")
    print("  Discovers what format the pool expects for mining.submit")
    print("=" * 60 + "\n")
    
    if len(sys.argv) < 4:
        print("Usage: python stratum_analyzer.py <host> <port> <wallet> [password]")
        print("")
        print("Examples:")
        print("  python stratum_analyzer.py zec.suprnova.cc 2142 t1YourWallet x")
        print("  python stratum_analyzer.py eu1-zcash.flypool.org 3333 t1YourWallet x")
        print("  python stratum_analyzer.py zec.2miners.com 1010 t1YourWallet x")
        print("")
        print("Common ZCash pools:")
        print("  - zec.suprnova.cc:2142")
        print("  - eu1-zcash.flypool.org:3333")
        print("  - zec.2miners.com:1010")
        print("  - zec-us.luxor.tech:6666")
        return 1
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    wallet = sys.argv[3]
    password = sys.argv[4] if len(sys.argv) > 4 else "x"
    
    # Check for SSL (typically ports like 6666, 3443, etc.)
    use_ssl = port in [6666, 3443, 443] or "ssl" in host.lower() or "tls" in host.lower()
    
    analyzer = StratumAnalyzer(host, port, wallet, password, use_ssl)
    
    try:
        if not analyzer.connect():
            return 1
        
        if not analyzer.subscribe():
            return 1
        
        if not analyzer.authorize():
            return 1
        
        # Listen for jobs
        analyzer.listen_for_jobs(duration=15)
        
        # Print summary
        analyzer.print_summary()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

