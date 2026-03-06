---
name: unified-dev-monitor-autobuy
description: Unified Dev Monitor with Auto-Buy for BSC and Solana
version: "1.0.0"
author: Your Name
tags: [bsc, solana, monitor, trading, auto-buy, crypto, defi, multi-chain]
payment:
  provider: skillpay.me
  api_key: sk_f072a786149bc07fc8730b4683dc00f3e050e72441922284ca803cdee2b994b5
  price: 0.01
  currency: USDT
  billing_mode: per_call
---
# Unified Dev Monitor with Auto-Buy

## 🎯 Overview

Comprehensive Dev Wallet Monitor for BSC and Solana with automatic buy functionality. Monitor token transfers from developer addresses and automatically buy new tokens via PancakeSwap (BSC) and PumpSwap (Solana).

## 💰 Pricing

- **Per Call**: 0.01 USDT
- **Payment Method**: SkillPay.me
- **Billing Mode**: Per call

## 🚀 Quick Start

### Installation

```bash
npm install
```

### Test Run

```bash
# Test environment
npm test

# Test BSC monitoring with auto-buy disabled
node index.js test

# Test BSC monitoring with auto-buy enabled
AUTO_BUY_ENABLED="true" AUTO_BUY_AMOUNT="1" WALLET_PRIVATE_KEY="your-key" node index-bsc.js test

# Test Solana monitoring (use index-sol-safe.js)
node index-sol-safe.js test

# Test Solana monitoring with auto-buy enabled (use index-sol-safe.js)
AUTO_BUY_ENABLED="true" AUTO_BUY_AMOUNT="0.1" WALLET_PRIVATE_KEY="your-sol-key-base64" node index-sol-safe.js test
```

## 📊 Supported Chains

### 1. BSC (Binance Smart Chain)

- **Native Token**: BNB
- **DEX**: PancakeSwap
- **Payment Token**: USDT (0x55d398326f9955f0bEb)
- **Router Address**: 0x10ED43C718714eb63d5aA57B78B54704E256024E
- **Block Time**: ~3 seconds
- **Address Format**: 0x... (42 hex characters)

### 2. Solana

- **Native Token**: SOL
- **DEX**: PumpSwap
- **Payment Token**: SOL (WSOL)
- **Router Address**: Auto-detected
- **Block Time**: ~400ms
- **Address Format**: Base58 (32-44 characters)

## 📖 Usage

### Monitor BSC with Auto-Buy

```javascript
{
  "action": "monitor",
  "chain": "BSC",
  "address": "YourBSCDevAddress",
  "duration": 3600,
  "autoBuy": {
    "enabled": true,
    "amount": "10",
    "slippage": 5
  }
}
```

**Response (Detection + Auto-Buy)**:
```json
{
  "success": true,
  "chain": "BSC",
  "detected": true,
  "transaction": {
    "hash": "0x...",
    "blockNumber": 12345678,
    "timestamp": "2026-03-05T10:30:00Z",
    "from": "DevAddress",
    "to": "RecipientAddress",
    "tokenAddress": "0x...",
    "tokenSymbol": "PEPE",
    "tokenName": "Pepe Token",
    "amount": "1000000000000000000000000",
    "decimals": 18
  },
  "autoBuy": {
    "enabled": true,
    "success": true,
    "transactionHash": "0x...",
    "gasUsed": "0.005 BNB",
    "actualAmount": "10 USDT"
  }
}
```

### Monitor Solana with Auto-Buy

```javascript
{
  "action": "monitor",
  "chain": "SOL",
  "address": "YourSolanaDevAddress",
  "duration": 3600,
  "autoBuy": {
    "enabled": true,
    "amount": 0.1,
    "slippage": 5
  }
}
```

**Response (Detection + Auto-Buy)**:
```json
{
  "success": true,
  "chain": "SOL",
  "detected": true,
  "transaction": {
    "signature": "3h1y...",
    "slot": 12345678,
    "timestamp": "2026-03-05T10:30:00Z",
    "from": "DevAddress",
    "to": "RecipientAddress",
    "tokenMint": "TokenMintAddress...",
    "tokenSymbol": "TOKEN",
    "amount": "1000000",
    "decimals": 9
  },
  "autoBuy": {
    "enabled": true,
    "success": true,
    "transactionHash": "3h1y...",
    "feePaid": 0.001 SOL"
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# BSC RPC
export BSC_RPC="https://bsc-dataseed.binance.org"

# Solana RPC
export SOLANA_RPC="https://api.mainnet-beta.solana.com"
export SOLANA_RPC_API_KEY="your-api-key"

# Wallet Private Keys
export WALLET_PRIVATE_KEY="your-bsc-private-key"               # BSC
export WALLET_PRIVATE_KEY_BASE64="your-solana-key-base64"   # Solana (Base64)

# Auto-Buy Configuration
export AUTO_BUY_ENABLED="true"
export AUTO_BUY_AMOUNT="10"                      # USDT for BSC
export AUTO_BUY_AMOUNT_SOL="0.1"                # SOL for Solana
export AUTO_BUY_SLIPPAGE="5"                     # Default: 5%
```

### Monitor Intervals

```javascript
// BSC: 3 seconds per block
const BSC_MONITOR_INTERVAL = 3000;

// Solana: 10 seconds (Solana block time ~400ms)
const SOL_MONITOR_INTERVAL = 10000;
```

## 📊 Auto-Buy Configuration

### BSC Auto-Buy (PancakeSwap)

- **Router**: `0x10ED43C718714eb63d5aA57B78B54704E256024E`
- **Payment Token**: USDT (`0x55d398326f9955f0bEb`)
- **Slippage Default**: 5%
- **Gas Price**: ~0.005 BNB (default)
- **Min Amount**: 1 USDT
- **Recommended Amount**: 10-100 USDT

### Solana Auto-Buy (PumpSwap)

- **Router**: Auto-detected from PumpSwap
- **Payment Token**: SOL (WSOL)
- **Slippage Default**: 5%
- **Fee**: ~0.001 SOL (default)
- **Min Amount**: 0.01 SOL
- **Recommended Amount**: 0.1-1 SOL

## 🎯 Use Cases

### 1. Alpha Hunters with Auto-Buy

Monitor popular dev addresses and automatically buy new tokens:

```javascript
{
  "action": "monitor",
  "chain": "BSC",
  "address": "0x4f0f84abd0b2d8a7ae5e252fb96e07946dbbb1a4",
  "duration": 3600,
  "autoBuy": {
    "enabled": true,
    "amount": 10,
    "slippage": 5
  }
}
```

### 2. Risk-Managed Trading

```javascript
{
  "action": "monitor",
  "chain": "BOTH",
  "addresses": {
    "BSC": [
      "0x4f0f84abd0b2d8a7ae5e252fb96e07946dbbb1a4",
      "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    ],
    "SOL": [
      "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
      "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"
    ]
  },
  "duration": 3600,
  "autoBuy": {
    "enabled": true,
    "amount": 0.1,
    "slippage": 5
  }
}
```

## 📋 Logs

### BSC Logs

- Monitor: `logs-bsc/bsc-monitor.log`
- Detections: `detections-bsc/detections.json`
- Auto-Buy: `logs-bsc/autobuy.log`

### Solana Logs

- Monitor: `logs-sol/sol-monitor.log`
- Detections: `detections-sol/detections.json`
- Auto-Buy: `logs-sol/autobuy.log`

## 🛠️ Development

### Dependencies

```json
{
  "dependencies": {
    "ethers": "^5.0.0",
    "@solana/web3.js": "^1.87.0",
    "axios": "^1.6.0",
    "@solana/token": "^0.2.0",
    "@solana/spl-token": "^0.2.0"
  }
}
```

### Install Dependencies

```bash
npm install
```

### Tests

```bash
# Test BSC monitoring
node index.js test

# Test BSC monitoring with auto-buy
AUTO_BUY_ENABLED="false" node index-bsc.js YourBSCDevAddress 60

# Test Solana monitoring (use index-sol-safe.js)
node index-sol-safe.js test

# Test Solana monitoring with auto-buy (use index-sol-safe.js)
AUTO_BUY_ENABLED="false" node index-sol-safe.js YourSolanaDevAddress 60
```

## 🔒 Security Recommendations

### 1. Wallet Security

- ❌ Never hardcode wallet private keys in code
- ✅ Always use environment variables
- ✅ Use separate wallets for trading
- ✅ Start with small test amounts

### 2. Risk Management

- Set reasonable auto-buy amounts
- Set daily loss limits
- Use stop-loss orders
- Monitor gas prices

### 3. Gas Optimization

- Adjust slippage to reduce failed transactions
- Monitor gas fees before trading
- Set max gas prices

### 4. Token Safety

- Verify token contracts before buying
- Check liquidity depth
- Avoid low-liquidity tokens

## 📈 References

- [BSC Documentation](https://docs.bscscan.com/)
- [PancakeSwap Docs](https://docs.pancakeswap.finance/)
- [Solana Web3.js](https://solana-labs.github.io/solana-web3.js/)
- [SPL Token](https://spl.solana.com/token/)
- [Pump.fun](https://pump.fun/)

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License
