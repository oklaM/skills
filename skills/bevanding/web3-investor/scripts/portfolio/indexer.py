#!/usr/bin/env python3
"""
Simple on-chain portfolio indexer for Ethereum mainnet.

Usage:
    python indexer.py --address 0x...
    python indexer.py --address 0x... --expiring-within 7
    python indexer.py --address 0x... --output json
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Optional

# Default RPC endpoints (public, free - for demo testing)
# Priority: User config > Environment > Alchemy > Cloudflare > Gateway.fm
DEFAULT_RPCS = [
    "https://cloudflare-eth.com",
    "https://mainnet.gateway.fm",
    "https://rpc.ankr.com/eth",
    "https://ethereum.publicnode.com",
]

# Alchemy API (requires API key - configure via environment or config)
ALCHEMY_RPC_TEMPLATE = "https://eth-mainnet.g.alchemy.com/v2/{api_key}"

# ERC20 ABI (minimal)
ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"}]')

# Common tokens on Ethereum
KNOWN_TOKENS = {
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": {"symbol": "WETH", "name": "Wrapped Ether", "decimals": 18},
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {"symbol": "USDC", "name": "USD Coin", "decimals": 6},
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": {"symbol": "USDT", "name": "Tether USD", "decimals": 6},
    "0x6B175474E89094C44Da98b954EesdeAC495271d0F": {"symbol": "DAI", "name": "Dai Stablecoin", "decimals": 18},
    "0x514910771AF9Ca656af840dff83E8264EcF986CA": {"symbol": "LINK", "name": "ChainLink Token", "decimals": 18},
    "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984": {"symbol": "UNI", "name": "Uniswap", "decimals": 18},
    "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9": {"symbol": "AAVE", "name": "Aave Token", "decimals": 18},
    "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84": {"symbol": "stETH", "name": "Lido Staked ETH", "decimals": 18},
}


def get_config() -> dict:
    """Load configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_rpc_url() -> str:
    """Get RPC URL from config or environment.
    
    Priority:
    1. WEB3_INVESTOR_RPC_URL environment variable
    2. config.json portfolio.rpc_url
    3. ALCHEMY_API_KEY environment variable (Alchemy)
    4. Default public RPCs (Cloudflare, Gateway.fm, etc.)
    """
    config = get_config()
    
    # 1. Check environment for custom RPC
    rpc = os.environ.get("WEB3_INVESTOR_RPC_URL")
    if rpc:
        return rpc
    
    # 2. Check config for custom RPC
    if config.get("portfolio", {}).get("rpc_url"):
        return config["portfolio"]["rpc_url"]
    
    # 3. Check for Alchemy API key
    alchemy_key = os.environ.get("ALCHEMY_API_KEY") or \
                  config.get("portfolio", {}).get("alchemy_api_key")
    if alchemy_key:
        return ALCHEMY_RPC_TEMPLATE.format(api_key=alchemy_key)
    
    # 4. Return first default RPC (Cloudflare)
    return DEFAULT_RPCS[0]


def get_eth_balance(address: str) -> float:
    """Get ETH balance using RPC."""
    rpc_url = get_rpc_url()
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    
    try:
        req = urllib.request.Request(
            rpc_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
            balance_wei = int(result.get("result", "0x0"), 16)
            return balance_wei / 1e18
    except Exception as e:
        print(f"Error fetching ETH balance: {e}", file=sys.stderr)
        return 0


def get_token_balance(address: str, token_address: str) -> dict:
    """Get token balance using RPC."""
    rpc_url = get_rpc_url()
    
    # For known tokens, use cached info
    token_info = KNOWN_TOKENS.get(token_address, {})
    
    # Encode balanceOf call
    # balanceOf(address) = 0x70a08231 + padded address
    padded_address = address[2:].lower().zfill(64)
    data = f"0x70a08231{padded_address}"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{"to": token_address, "data": data}, "latest"],
        "id": 1
    }
    
    try:
        req = urllib.request.Request(
            rpc_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
            balance_hex = result.get("result", "0x0")
            balance_raw = int(balance_hex, 16)
            
            decimals = token_info.get("decimals", 18)
            balance = balance_raw / (10 ** decimals)
            
            return {
                "address": token_address,
                "symbol": token_info.get("symbol", "UNKNOWN"),
                "name": token_info.get("name", "Unknown Token"),
                "balance": balance,
                "balance_raw": balance_hex,
                "decimals": decimals
            }
    except Exception as e:
        return {
            "address": token_address,
            "symbol": "ERROR",
            "balance": 0,
            "error": str(e)
        }


def get_prices(tokens: list) -> dict:
    """Get token prices from CoinGecko."""
    if not tokens:
        return {}
    
    # Map symbols to CoinGecko IDs
    symbol_to_id = {
        "ETH": "ethereum",
        "WETH": "ethereum",
        "USDC": "usd-coin",
        "USDT": "tether",
        "DAI": "dai",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "AAVE": "aave",
        "stETH": "staked-ether"
    }
    
    ids = []
    for t in tokens:
        symbol = t.get("symbol", "").upper()
        if symbol in symbol_to_id:
            ids.append(symbol_to_id[symbol])
    
    if not ids:
        return {}
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(set(ids))}&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching prices: {e}", file=sys.stderr)
        return {}


def get_portfolio(address: str, use_debank: bool = False) -> dict:
    """
    Get portfolio for an address.
    
    Args:
        address: Ethereum address
        use_debank: Use Debank API if available
    
    Returns:
        Portfolio dict with tokens and positions
    """
    config = get_config()
    
    # Try Debank first if configured
    if use_debank:
        debank_key = config.get("portfolio", {}).get("debank_api_key") or \
                     os.environ.get("WEB3_INVESTOR_DEBANK_API_KEY")
        if debank_key:
            return get_portfolio_debank(address, debank_key)
    
    # Fallback to simple indexer
    return get_portfolio_simple(address)


def get_portfolio_simple(address: str) -> dict:
    """Simple portfolio indexer using RPC."""
    address = address.lower()
    
    # Get ETH balance
    eth_balance = get_eth_balance(address)
    
    # Get token balances for known tokens
    tokens = []
    for token_address in KNOWN_TOKENS:
        token = get_token_balance(address, token_address)
        if token.get("balance", 0) > 0:
            tokens.append(token)
    
    # Get prices
    prices = get_prices(tokens)
    eth_price = prices.get("ethereum", {}).get("usd", 2000)
    
    # Calculate values
    total_value = eth_balance * eth_price
    
    for token in tokens:
        symbol = token.get("symbol", "").upper()
        symbol_map = {
            "WETH": "ethereum",
            "USDC": "usd-coin",
            "USDT": "tether",
            "DAI": "dai",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "AAVE": "aave",
            "STETH": "staked-ether"
        }
        price_id = symbol_map.get(symbol)
        token["price_usd"] = prices.get(price_id, {}).get("usd", 0)
        token["value_usd"] = token.get("balance", 0) * token.get("price_usd", 0)
        total_value += token["value_usd"]
    
    # Add ETH as a token
    eth_token = {
        "address": "0x0000000000000000000000000000000000000000",
        "symbol": "ETH",
        "name": "Ethereum",
        "balance": eth_balance,
        "price_usd": eth_price,
        "value_usd": eth_balance * eth_price
    }
    
    all_tokens = [eth_token] + [t for t in tokens if t.get("value_usd", 0) > 0.01]
    all_tokens.sort(key=lambda x: x.get("value_usd", 0), reverse=True)
    
    return {
        "address": address,
        "chain": "ethereum",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_value_usd": round(total_value, 2),
        "tokens": all_tokens,
        "defi_positions": [],  # Requires more complex indexing
        "expiring_positions": [],  # Populated from DeFi positions
        "data_source": "simple_indexer"
    }


def get_portfolio_debank(address: str, api_key: str) -> dict:
    """Get portfolio using Debank API."""
    url = f"https://api.debank.com/v1/user/total_balance?id={address}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"Access-Key": api_key}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            
        # Transform Debank response
        return {
            "address": address,
            "chain": "ethereum",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_value_usd": data.get("total_usd_value", 0),
            "tokens": [],  # Would need additional API calls
            "defi_positions": [],  # Would need additional API calls
            "expiring_positions": [],
            "data_source": "debank"
        }
    except Exception as e:
        print(f"Debank API error: {e}, falling back to simple indexer", file=sys.stderr)
        return get_portfolio_simple(address)


def find_expiring_positions(portfolio: dict, days: int = 7) -> list:
    """Find positions expiring within N days."""
    # This would require DeFi position data
    # For now, return empty list
    # TODO: Implement when DeFi position indexing is added
    return []


def format_report(portfolio: dict, output_format: str = "markdown") -> str:
    """Format portfolio as report."""
    if output_format == "json":
        return json.dumps(portfolio, indent=2)
    
    lines = [
        f"# Portfolio Report",
        "",
        f"**Address**: `{portfolio['address']}`",
        f"**Chain**: {portfolio['chain'].title()}",
        f"**Total Value**: **${portfolio['total_value_usd']:,.2f}**",
        f"**Data Source**: {portfolio['data_source']}",
        f"**Updated**: {portfolio['timestamp']}",
        "",
        "---",
        "",
        "## 🪙 Token Holdings",
        "",
        "| Token | Balance | Price | Value (USD) |",
        "|-------|---------|-------|-------------|"
    ]
    
    for token in portfolio.get("tokens", []):
        lines.append(
            f"| {token.get('symbol', '?')} | {token.get('balance', 0):.4f} | "
            f"${token.get('price_usd', 0):.2f} | ${token.get('value_usd', 0):,.2f} |"
        )
    
    if portfolio.get("defi_positions"):
        lines.extend([
            "",
            "---",
            "",
            "## 🏦 DeFi Positions",
            ""
        ])
        for pos in portfolio["defi_positions"]:
            lines.append(f"- **{pos.get('protocol', 'Unknown')}**: ${pos.get('value_usd', 0):,.2f}")
    
    if portfolio.get("expiring_positions"):
        lines.extend([
            "",
            "---",
            "",
            "## ⏰ Expiring Soon",
            ""
        ])
        for pos in portfolio["expiring_positions"]:
            lines.append(f"- {pos}")
    else:
        lines.extend([
            "",
            "---",
            "",
            "*No positions expiring soon.*"
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Portfolio indexer for Ethereum")
    parser.add_argument("--address", required=True, help="Ethereum address to index")
    parser.add_argument("--expiring-within", type=int, help="Find positions expiring within N days")
    parser.add_argument("--use-debank", action="store_true", help="Use Debank API if available")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    
    args = parser.parse_args()
    
    portfolio = get_portfolio(args.address, args.use_debank)
    
    if args.expiring_within:
        portfolio["expiring_positions"] = find_expiring_positions(portfolio, args.expiring_within)
    
    print(format_report(portfolio, args.output))


if __name__ == "__main__":
    main()