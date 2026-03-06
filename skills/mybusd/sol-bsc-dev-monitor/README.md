# Unified Dev Monitor with Auto-Buy

## 🎯 Overview

Multi-chain developer wallet monitor with automatic buy functionality for BSC and Solana. Monitor token transfers from developer addresses and automatically buy new tokens via PancakeSwap (BSC) and Jupiter (Solana).

## 🔒 Security First

### Private Key Management

This tool offers **two ways** to provide your private key:

#### Option 1: Environment Variables (Recommended for Automation)

```bash
export WALLET_PRIVATE_KEY_BASE64=$(cat wallet.key | base64)
export SOLANA_RPC=https://api.mainnet-beta.solana.com
export WALLET_PRIVATE_KEY=0x...
export BSC_RPC=https://bsc-dataseed.binance.org
```

#### Option 2: Interactive Input (More Secure for Manual Use)

When you run the tool without environment variables set, it will **prompt you** to enter your private key securely:

```bash
# For BSC
Enter your BSC wallet private key (0x...): [you type here]

# For Solana
Enter your Solana wallet private key (Base64 encoded): [you type here]
```

**Benefits of Interactive Input:**
- ✅ No need to set environment variables
- ✅ Private key is not stored anywhere
- ✅ More secure for manual, one-off operations
- ✅ Reduced risk of accidentally committing secrets

---

## 📊 Supported Chains

### 1. BSC (Binance Smart Chain)
- **Native Token**: BNB
- **DEX**: PancakeSwap
- **Router Address**: 0x10ED43C718714eb63d5aA57B78B54704E256024E

### 2. Solana
- **Native Token**: SOL
- **DEX**: Jupiter Aggregator
- **API**: https://quote-api.jup.ag/v6

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Monitoring

**Option A: Use Environment Variables (Automation)**
```bash
# Set environment variables first
export WALLET_PRIVATE_KEY_BASE64=$(cat wallet.key | base64)
export SOLANA_RPC=https://api.mainnet-beta.solana.com
export WALLET_PRIVATE_KEY=0x...
export BSC_RPC=https://bsc-dataseed.binance.org

# Run
node index-sol-safe.js monitor <ADDRESS> SOL 3600
node index-bsc.js monitor <ADDRESS> BSC 3600
```

**Option B: Interactive Input (More Secure)**
```bash
# Just run - the tool will prompt for private key
node index-sol-safe.js monitor <ADDRESS> SOL 3600
node index-bsc.js monitor <ADDRESS> BSC 3600
```

---

## 📖 Usage

### Monitor with Auto-Buy (Interactive)

```bash
# Solana - will prompt for private key
node index-sol-safe.js monitor <ADDRESS> SOL 3600

# BSC - will prompt for private key
node index-bsc.js monitor <ADDRESS> BSC 3600
```

**You'll see:**
```
Enter your Solana wallet private key (Base64 encoded): [type here]
📊 Starting Solana monitoring for address: <ADDRESS>
...
```

### Monitor with Auto-Buy (Environment Variables)

```bash
# Set environment variables
export WALLET_PRIVATE_KEY_BASE64=$(cat wallet.key | base64)
export WALLET_PRIVATE_KEY=0x...

# Run - will use environment variables
node index-sol-safe.js monitor <ADDRESS> SOL 3600
node index-bsc.js monitor <ADDRESS> BSC 3600
```

**You'll see:**
```
✅ Using WALLET_PRIVATE_KEY_BASE64 from environment
📊 Starting Solana monitoring for address: <ADDRESS>
...
```

---

## ⚙️ Configuration Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `address` | Target address to monitor | Required | `'7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU'` |
| `duration` | Monitoring duration in seconds | `3600` (1 hour) | `3600` |
| `autoBuy.enabled` | Enable auto-buy | `false` | `true` |
| `autoBuy.amount` | Amount per buy | `0.1` | `0.05` |
| `autoBuy.slippage` | Slippage tolerance (%) | `5` | `3` |

---

## 🔒 Security Best Practices

### For Interactive Input

✅ **Most secure for manual use:**
- Private key is never stored
- Private key is never logged
- Private key is used only in memory
- Perfect for one-off operations

### For Environment Variables

✅ **Best for automation:**
- Set private key per session
- Never commit to version control
- Use `.env` files with restricted permissions
- Clear environment variables after use

### General Security

- ✅ Use a dedicated trading wallet
- ✅ Start with small test amounts (0.001 SOL/BNB)
- ✅ Verify transactions on blockchain explorers
- ✅ Never share your private key
- ✅ Keep backups in secure locations

---

## 📝 Logging

Logs are written to:
- `logs-sol/sol-monitor.log` - Solana monitoring logs
- `logs-bsc/bsc-monitor.log` - BSC monitoring logs

**Important:** Private keys are **never logged**.

View logs:
```bash
tail -f logs-sol/sol-monitor.log
tail -f logs-bsc/bsc-monitor.log
```

---

## 🔍 Transaction Verification

### Solana
- Explorer: https://explorer.solana.com/
- Check transaction signatures in logs

### BSC
- Explorer: https://bscscan.com/
- Check transaction hashes in logs

---

## 📦 Dependencies

- `@solana/web3.js` (^1.98.4) - Solana blockchain interaction
- `axios` (^1.13.6) - HTTP requests (Jupiter API)
- `ethers` (^5.0.0) - EVM blockchain interaction (BSC)

---

## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. The user assumes all risks associated with trading cryptocurrency. Always verify transactions independently and only trade with funds you can afford to lose.

**Important:**
- Always start with small test amounts
- Verify every transaction
- Use a dedicated trading wallet
- Keep your private keys secure

---

## 📄 License

MIT

---

**Version**: 1.0.0
**Node.js**: >=14.0.0
