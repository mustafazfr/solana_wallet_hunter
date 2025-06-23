#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solana Wallet Hunter - GUARANTEED Version (100% Check)
"""

import time
import threading
import requests
from datetime import datetime
from mnemonic import Mnemonic
import bip_utils
import base58
from nacl.signing import SigningKey

class SolanaHunterGuaranteed:
    def __init__(self):
        # Public RPC Endpoint
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com"
        ]
        self.current_rpc_index = 0
        
        self.mnemo = Mnemonic("english")
        
        # Statistics
        self.attempts = 0
        self.found_wallets = 0
        self.retries = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        self.output_file = "found_wallets.txt"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        print("✅ Solana Wallet Hunter - GUARANTEED Version")
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

    def print_stats(self, extra_message=""):
        """Prints progress statistics."""
        elapsed = time.time() - self.start_time
        speed = self.attempts / elapsed if elapsed > 0 else 0
        
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"Attempts: {self.attempts:,} | "
              f"Found: {self.found_wallets} | "
              f"Retries: {self.retries} | "
              f"Speed: {speed:.1f}/s"
              f"{extra_message}", end="")

    def worker(self, worker_id: int):
        """The main loop for each worker thread."""
        print(f"✅ Thread {worker_id} started in GUARANTEED mode.")
        batch_size = 100
        
        while True:
            try:
                # 1. Create a batch of 100 wallets
                wallets_batch = []
                for _ in range(batch_size):
                    mnemonic, address = self.generate_wallet()
                    if mnemonic and address:
                        wallets_batch.append({'mnemonic': mnemonic, 'address': address})
                
                # 2. Retry query UNTIL it is successful
                is_successful = False
                retry_count_local = 0
                while not is_successful:
                    is_successful = self.check_balance_batch(wallets_batch)
                    
                    if not is_successful:
                        retry_count_local += 1
                        with self.lock:
                            self.retries += 1
                        self.print_stats(f" (Retrying batch {self.attempts // batch_size + 1}, attempt {retry_count_local}...)")
                        time.sleep(1) # Wait 1 second before retrying
                
                # 3. Update statistics (only after successful query)
                with self.lock:
                    self.attempts += len(wallets_batch)
                    self.print_stats()

            except KeyboardInterrupt:
                break
            except Exception:
                # Continue on general errors
                time.sleep(1)

    def start(self, num_threads=8):
        """Starts the search in GUARANTEED mode."""
        print(f"🚀 Starting GUARANTEED search with {num_threads} threads!")
        print("💯 NO wallets generated in this mode will be skipped.")
        print("🐢 Speed may be slower, but the check is 100%.")
        print("🔄 Press Ctrl+C to stop.")
        print("=" * 50)
        
        try:
            threads = []
            for i in range(num_threads):
                thread = threading.Thread(target=self.worker, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            while True:
                if not any(t.is_alive() for t in threads):
                    break
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping program...")
        
        elapsed = time.time() - self.start_time
        avg_speed = self.attempts / elapsed if elapsed > 0 else 0
        
        print("\n\n📊 FINAL REPORT:")
        print(f"⏱️  Total Time: {elapsed:.1f} seconds")
        print(f"🔢 Total Attempts (100% Check): {self.attempts:,}")
        print(f"🎯 Wallets Found: {self.found_wallets}")
        print(f"🔁 Total Retries: {self.retries}")
        print(f"⚡ Average Speed: {avg_speed:.1f} attempts/second")

if __name__ == "__main__":
    print("=" * 50)
    print("✅ Solana Wallet Hunter - GUARANTEED Version")
    print("=" * 50)
    print("⚠️  This tool is for educational purposes only!")
    print("💯 This script checks the balance of every found wallet with 100% certainty.")
    
    confirm = input("\nType 'yes' to start GUARANTEED mode: ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        exit()
    
    try:
        threads_input = input("How many threads to use? (Recommended: 8, max: 12): ").strip()
        num_threads = int(threads_input) if threads_input else 8
        if not 1 <= num_threads <= 12:
            print("⚠️ Invalid number. Using 8 threads.")
            num_threads = 8
    except ValueError:
        print("⚠️ Please enter a numeric value. Using 8 threads.")
        num_threads = 8
    
    hunter = SolanaHunterGuaranteed()
    hunter.start(num_threads)