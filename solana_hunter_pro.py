#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solana Wallet Hunter - PRO Version (Batch Query)
"""

import time
import threading
import requests
from datetime import datetime
from mnemonic import Mnemonic
import bip_utils
import base58
from nacl.signing import SigningKey

class SolanaHunterPro:
    def __init__(self):
        # Most reliable RPC endpoints
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://rpc.ankr.com/solana"
        ]
        self.current_rpc_index = 0
        
        self.mnemo = Mnemonic("english")
        
        # Statistics
        self.attempts = 0
        self.found_wallets = 0
        self.rpc_errors = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        self.output_file = "found_wallets.txt"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        print("🚀 Solana Wallet Hunter - PRO Version")
        print("=" * 50)

    def get_rpc_url(self) -> str:
        """RPC URL rotation"""
        url = self.rpc_endpoints[self.current_rpc_index]
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
        return url

    def generate_wallet(self) -> tuple:
        """Generates a single wallet (mnemonic, address)"""
        try:
            mnemonic = self.mnemo.generate(strength=128)
            seed = self.mnemo.to_seed(mnemonic)
            
            bip44_mst_ctx = bip_utils.Bip44.FromSeed(seed, bip_utils.Bip44Coins.SOLANA)
            bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(bip_utils.Bip44Changes.CHAIN_EXT)
            bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
            
            private_key_bytes = bip44_addr_ctx.PrivateKey().Raw().ToBytes()
            signing_key = SigningKey(private_key_bytes[:32])
            public_key = signing_key.verify_key.encode()
            address = base58.b58encode(public_key).decode('utf-8')
            
            return mnemonic, address
        except Exception:
            return None, None

    def check_balance_batch(self, wallets: list):
        """Checks the balance of a batch of 100 wallets at once."""
        try:
            addresses = [wallet['address'] for wallet in wallets]
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getMultipleAccounts",
                "params": [addresses]
            }
            
            rpc_url = self.get_rpc_url()
            # Batch query can take longer, let's set timeout to 5 seconds
            response = self.session.post(rpc_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'value' in data['result']:
                    accounts = data['result']['value']
                    
                    for i, account in enumerate(accounts):
                        if account is not None:
                            balance_lamports = account['lamports']
                            if balance_lamports > 0:
                                balance_sol = balance_lamports / 1_000_000_000
                                wallet = wallets[i]
                                self.save_wallet(wallet['mnemonic'], wallet['address'], balance_sol)
                return True # Successful query
        except Exception:
            # Silently pass on error
            pass
        
        return False # Failed query

    def save_wallet(self, mnemonic: str, address: str, balance: float):
        """Saves the found wallet."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wallet_info = f"""--------------------------------------------------
🎉 WALLET FOUND!
⏰ {timestamp}
🔑 {mnemonic}
📍 {address}
💰 {balance:.9f} SOL
--------------------------------------------------\n\n"""
        
        with self.lock:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(wallet_info)
            self.found_wallets += 1
            
        print(f"\n🎉🎉🎉 NEW WALLET FOUND! 🎉🎉🎉")
        print(f"📍 Address: {address}")
        print(f"💰 Balance: {balance:.9f} SOL\n")

    def print_stats(self):
        """Prints progress statistics."""
        elapsed = time.time() - self.start_time
        speed = self.attempts / elapsed if elapsed > 0 else 0
        
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"Attempts: {self.attempts:,} | "
              f"Found: {self.found_wallets} | "
              f"Errors: {self.rpc_errors} | "
              f"Speed: {speed:.1f}/s", end="")

    def worker(self, worker_id: int):
        """The main loop for each worker thread."""
        print(f"⚡ Thread {worker_id} started in PRO mode.")
        batch_size = 100
        
        while True:
            try:
                # 1. Create a batch of 100 wallets (very fast)
                wallets_batch = []
                for _ in range(batch_size):
                    mnemonic, address = self.generate_wallet()
                    if mnemonic and address:
                        wallets_batch.append({'mnemonic': mnemonic, 'address': address})
                
                # 2. Query the balance of 100 wallets in a single batch
                success = self.check_balance_batch(wallets_batch)
                
                # 3. Update statistics
                with self.lock:
                    self.attempts += len(wallets_batch)
                    if not success:
                        self.rpc_errors += 1
                    
                    self.print_stats()
                
                # A short wait to avoid overloading the RPC
                time.sleep(0.1)

            except KeyboardInterrupt:
                break
            except Exception:
                # Continue on general errors
                time.sleep(1)

    def start(self, num_threads=4):
        """Starts the PRO search."""
        print(f"🚀 Starting PRO search with {num_threads} threads!")
        print("⚡ It will query in batches of 100.")
        print("🔄 Press Ctrl+C to stop.")
        print("=" * 50)
        
        try:
            threads = []
            for i in range(num_threads):
                thread = threading.Thread(target=self.worker, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            # The main thread will wait for a Ctrl+C command here.
            # This loop prevents the program from closing while also allowing for interrupts.
            while True:
                # Check if any of the threads have closed unexpectedly
                # This prevents the program from running forever
                if not any(t.is_alive() for t in threads):
                    break
                time.sleep(1) # Wait without using CPU
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping program...")
        
        elapsed = time.time() - self.start_time
        avg_speed = self.attempts / elapsed if elapsed > 0 else 0
        
        print("\n\n📊 FINAL REPORT:")
        print(f"⏱️  Total Time: {elapsed:.1f} seconds")
        print(f"🔢 Total Attempts: {self.attempts:,}")
        print(f"🎯 Wallets Found: {self.found_wallets}")
        print(f"❌ Failed Query Batches: {self.rpc_errors}")
        print(f"⚡ Average Speed: {avg_speed:.1f} attempts/second")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Solana Wallet Hunter - PRO Version")
    print("=" * 50)
    print("⚠️  This tool is for educational purposes only!")
    print("⚡ Maximum efficiency is targeted with batch query mode.")
    
    confirm = input("\nType 'yes' to start PRO mode: ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        exit()
    
    try:
        threads_input = input("How many threads to use? (default: 2, max: 4): ").strip()
        num_threads = int(threads_input) if threads_input else 2
        if not 1 <= num_threads <= 4:
            print("⚠️ Invalid number. Using 2 threads.")
            num_threads = 2
    except ValueError:
        print("⚠️ Please enter a numeric value. Using 2 threads.")
        num_threads = 2
    
    hunter = SolanaHunterPro()
    hunter.start(num_threads) 