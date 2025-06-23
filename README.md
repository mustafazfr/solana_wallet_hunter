# Solana Wallet Hunter

This tool attempts to find Solana wallets with a balance by generating random 12-word mnemonic phrases. It offers two different operating modes: **PRO** and **GUARANTEED**.

## ⚠️ Important Warning

**This tool is for educational and experimental purposes only!** The chances of success in finding a random wallet are mathematically close to impossible. Using this tool with the expectation of real financial gain is a waste of time.

- **Probability of Success:** The likelihood of finding a wallet is far lower than finding a needle in a haystack.
- **Time:** Achieving a meaningful result could take millions of years.

## ✨ Modes

This project includes two different scripts:

### 1. `solana_hunter_pro.py` (PRO Mode)
- **Speed-Focused:** Queries wallets in batches of 100 very quickly.
- **Risk:** It **may skip** some wallet batches if the RPC server is busy or an error occurs. This could potentially cause a wallet with a balance to be missed.
- **Use Case:** Ideal for attempting a very high number of wallets in a short amount of time.

### 2. `solana_hunter_guaranteed.py` (GUARANTEED Mode)
- **Reliability-Focused:** Checks the balance of every single generated wallet, guaranteed.
- **Guarantee:** If a query fails, it retries the same batch of wallets until it succeeds. This ensures that **no wallet is skipped**.
- **Disadvantage:** It is significantly slower than the PRO mode.

## 🛠️ Installation

1.  Install Python 3.7 or higher.
2.  Install the required libraries using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

Choose your desired mode and run the corresponding script.

### Starting PRO Mode
```bash
python solana_hunter_pro.py
```
When the program starts:
1.  Read the warnings and confirm by typing `yes`.
2.  Choose how many threads you want to use (Recommendation: 2-4).

### Starting GUARANTEED Mode
```bash
python solana_hunter_guaranteed.py
```
When the program starts:
1.  Read the warnings and confirm by typing `yes`.
2.  Choose how many threads you want to use (Recommendation: 8-12).

## 📁 Output

When a wallet with a balance is found, its information is saved to the `found_wallets.txt` file in the following format:

```
--------------------------------------------------
🎉 WALLET FOUND!
⏰ 2024-05-20 15:30:00
🔑 [12-word mnemonic phrase]
📍 [Wallet address]
💰 [Balance] SOL
--------------------------------------------------
```

## 🛑 Stopping the Program

You can safely stop both scripts by pressing `Ctrl+C`. A summary report will be displayed when the program terminates.

## ❤️ Support

If you find this tool useful and would like to support its development, you can send a donation to the following Solana address:

- **SOL:** `J4zrfLTwSmoLK1utgyU78o6u5Fh5h3y3vcAprCqyTJGW`

## 📝 License

This project is distributed under the MIT License. It is intended for educational and research purposes. 
