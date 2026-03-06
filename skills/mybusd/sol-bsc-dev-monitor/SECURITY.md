# Security Information

## 🔒 Private Key Input Methods

This tool offers **two secure ways** to provide your private key:

### Option 1: Interactive Input (Recommended for Manual Use)

**How it works:**
- Run the tool without environment variables
- The tool will prompt you to enter your private key
- Your input is handled securely and never stored

**Example:**
```bash
node index-sol-safe.js monitor <ADDRESS> SOL 3600
```

**You'll see:**
```
Enter your Solana wallet private key (Base64 encoded): [you type here]
✅ Using WALLET_PRIVATE_KEY_BASE64 from input
📊 Starting Solana monitoring...
```

**Benefits:**
- ✅ No environment variables needed
- ✅ Private key is never stored anywhere
- ✅ Private key is never logged
- ✅ Perfect for one-off operations
- ✅ Reduced risk of accidental exposure

**Best for:**
- Manual, one-time monitoring
- Testing and experimentation
- Users who prefer not to set environment variables

---

### Option 2: Environment Variables (Recommended for Automation)

**How it works:**
- Set environment variables before running
- The tool will automatically detect and use them
- Private key is kept in process memory only

**Example:**
```bash
export WALLET_PRIVATE_KEY_BASE64=$(cat wallet.key | base64)
export SOLANA_RPC=https://api.mainnet-beta.solana.com
export WALLET_PRIVATE_KEY=0x...
export BSC_RPC=https://bsc-dataseed.binance.org

node index-sol-safe.js monitor <ADDRESS> SOL 3600
```

**You'll see:**
```
✅ Using WALLET_PRIVATE_KEY_BASE64 from environment
📊 Starting Solana monitoring...
```

**Benefits:**
- ✅ Perfect for automation and scripts
- ✅ Easy to integrate with CI/CD
- ✅ Can be set per session
- ✅ Compatible with `.env` files

**Best for:**
- Automated monitoring
- Scheduled tasks
- CI/CD integration

---

## 🔒 Security Best Practices

### 1. Never Commit Private Keys

**❌ Don't do this:**
```bash
git add .env
git commit -m "Add config"
```

**✅ Do this instead:**
```bash
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
```

---

### 2. Use a Dedicated Trading Wallet

**Why:**
- Never use your main wallet for automated trading
- Only keep funds you're willing to risk
- Transfer profits regularly to your main wallet

**How:**
- Create a new wallet specifically for this tool
- Fund it with test amounts first
- Only increase amounts after successful tests

---

### 3. Start with Small Amounts

**Recommended testing amounts:**
- Solana: 0.001 SOL
- BSC: 0.001 BNB

**Only increase after:**
- ✅ Successful test transactions
- ✅ Verified on blockchain explorer
- ✅ Confirmed received expected tokens

---

### 4. Verify Every Transaction

**For Solana:**
- Visit: https://explorer.solana.com/
- Check: Transaction signature from logs
- Verify: Token mint addresses and amounts

**For BSC:**
- Visit: https://bscscan.com/
- Check: Transaction hash from logs
- Verify: Token contract addresses and amounts

---

### 5. Monitor Logs Regularly

**View logs in real-time:**
```bash
# Solana
tail -f logs-sol/sol-monitor.log

# BSC
tail -f logs-bsc/bsc-monitor.log
```

**What to look for:**
- ✅ Successful detections
- ✅ Auto-buy completions
- ❌ Any errors or warnings
- ❌ Failed transactions

---

## 🔍 How Private Keys Are Handled

### In Memory Only

- Private keys are **never written to disk**
- Private keys are **never logged**
- Private keys are only kept in **process memory**
- Memory is cleared when process exits

### No Storage

- No database storage
- No file storage
- No environment variable storage (unless you set them)
- No caching

### Secure Input

Interactive input uses Node.js `readline`:
- Input is handled securely
- Not echoed to terminal
- Not recorded in shell history
- Cleaned from memory after use

---

## ⚠️ Important Security Notes

### What This Tool Does Not Do

- ❌ It does not store your private key
- ❌ It does not log your private key
- ❌ It does not send your private key to any server
- ❌ It does not share your private key with anyone

### What This Tool Does

- ✅ It uses your private key only to sign transactions
- ✅ It keeps your private key in memory only
- ✅ It signs transactions locally on your machine
- ✅ It broadcasts signed transactions to the blockchain

---

## 📊 Trading Mechanisms

### Solana
- **DEX**: Jupiter Aggregator
- **API**: https://quote-api.jup.ag/v6
- **Payment Token**: SOL (native)
- **Swap Method**: Token swap via Jupiter
- **Authorization**: Not required (native token)

### BSC
- **DEX**: PancakeSwap
- **Router**: 0x10ED43C718714eb63d5aA57B78B54704E256024E
- **Payment Token**: BNB (native)
- **Swap Method**: swapExactETHForTokens
- **Authorization**: Not required (native token)

---

## 🚨 Important Notes

- This is a trading tool for educational and research purposes
- Use at your own risk
- Only trade with funds you can afford to lose
- Always verify transactions independently
- Keep private keys secure at all times

---

## 📝 Logging and Detection

**Logs are written to:**
- `logs-sol/sol-monitor.log` - Solana monitoring logs
- `logs-bsc/bsc-monitor.log` - BSC monitoring logs

**Detections are saved to:**
- `detections-sol/detections.json` - Solana detection history
- `detections-bsc/detections.json` - BSC detection history

**Important:**
- Private keys are **never logged**
- Only transaction data is logged
- Logs can be safely shared for debugging

---

## ⚖️ Disclaimer

This tool is provided for educational and research purposes only. The user assumes all risks associated with trading cryptocurrency. The developers are not responsible for any financial losses.

**Always:**
- Start with small test amounts
- Verify every transaction
- Use a dedicated trading wallet
- Keep your private keys secure
- Never share your private key with anyone
