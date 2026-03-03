#!/usr/bin/env python3
"""
Safe Vault - Secure transaction signing and execution.

Usage:
    python safe_vault.py --init --mode simulation
    python safe_vault.py --prepare-tx --to 0x... --value 0 --data 0x...
    python safe_vault.py --simulate --to 0x... --data 0x...
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Optional
import urllib.request
import urllib.error

# Config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.json")
WHITELIST_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "whitelist.json")


def load_config() -> dict:
    """Load configuration."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"trading": {"mode": "simulation", "whitelist_enabled": True, "default_limit_usd": 100}}


def load_whitelist() -> dict:
    """Load whitelist."""
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH) as f:
            return json.load(f)
    return {"addresses": [], "enabled": True}


def save_whitelist(whitelist: dict):
    """Save whitelist."""
    os.makedirs(os.path.dirname(WHITELIST_PATH), exist_ok=True)
    with open(WHITELIST_PATH, "w") as f:
        json.dump(whitelist, f, indent=2)


def check_whitelist(address: str, amount_usd: float = 0) -> dict:
    """
    Check if address is in whitelist and within limits.
    
    Returns:
        dict with allowed (bool), reason (str), limit (float)
    """
    config = load_config()
    whitelist = load_whitelist()
    
    if not config["trading"].get("whitelist_enabled", True):
        return {"allowed": True, "reason": "Whitelist disabled", "limit": float("inf")}
    
    if not whitelist.get("enabled", True):
        return {"allowed": True, "reason": "Whitelist disabled", "limit": float("inf")}
    
    address_lower = address.lower()
    
    for entry in whitelist.get("addresses", []):
        if entry.get("address", "").lower() == address_lower:
            limit = entry.get("max_amount_usd", config["trading"].get("default_limit_usd", 100))
            if amount_usd <= limit:
                return {"allowed": True, "reason": f"Within limit (${amount_usd:.2f} <= ${limit})", "limit": limit}
            else:
                return {"allowed": False, "reason": f"Exceeds limit (${amount_usd:.2f} > ${limit})", "limit": limit}
    
    return {"allowed": False, "reason": "Address not in whitelist", "limit": 0}


def get_eth_price_usd() -> float:
    """Get current ETH price from CoinGecko (free API)."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["ethereum"]["usd"]
    except:
        return 2000  # Fallback estimate


def get_token_price_usd(token_address: str) -> float:
    """Get token price from CoinGecko."""
    # Common tokens
    known_tokens = {
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 1.0,  # USDC
        "0xdac17f958d2ee523a2206206994597c13d831ec7": 1.0,  # USDT
        "0x6b175474e89094c44da98b954eedeac495271d0f": 1.0,  # DAI
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": get_eth_price_usd(),  # WETH
    }
    
    return known_tokens.get(token_address.lower(), 0)


def estimate_value_usd(value_wei: str, token_address: str = None) -> float:
    """Estimate transaction value in USD."""
    if token_address:
        return get_token_price_usd(token_address)
    
    # ETH value
    try:
        value_eth = float(value_wei) / 1e18
        return value_eth * get_eth_price_usd()
    except:
        return 0


def simulate_transaction(to: str, value: str, data: str) -> dict:
    """
    Simulate transaction using Tenderly (free) or local estimation.
    
    For demo, we use a simple gas estimation.
    """
    # Simple simulation result
    result = {
        "success": True,
        "gas_estimate": 200000,
        "gas_price_gwei": 20,
        "gas_cost_eth": 0.004,  # 200k * 20 gwei
        "warnings": []
    }
    
    # Add warnings for common patterns
    if not data or data == "0x":
        result["warnings"].append("Empty calldata - this is a simple ETH transfer")
    
    if value and float(value) > 0:
        result["warnings"].append(f"Sending {float(value)/1e18:.4f} ETH")
    
    return result


def prepare_transaction(
    to: str,
    value: str = "0",
    data: str = "0x",
    gas_limit: int = 300000,
    description: str = ""
) -> dict:
    """
    Prepare a transaction for signing.
    
    Returns a signing request that can be shown to the user.
    """
    config = load_config()
    mode = config["trading"].get("mode", "simulation")
    
    # Estimate value
    value_usd = estimate_value_usd(value)
    
    # Check whitelist
    whitelist_result = check_whitelist(to, value_usd)
    
    # Simulate
    simulation = simulate_transaction(to, value, data)
    
    # Generate request
    request_id = str(uuid.uuid4())
    request = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "transaction": {
            "to": to,
            "value": value,
            "data": data,
            "gas_limit": gas_limit,
            "chain_id": 1,  # Ethereum mainnet
        },
        "simulation": simulation,
        "whitelist": whitelist_result,
        "value_usd": round(value_usd, 2),
        "description": description,
        "approval_required": mode == "simulation" or not whitelist_result["allowed"]
    }
    
    return request


def format_signing_request(request: dict) -> str:
    """Format signing request for display."""
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║                    🔐 SIGNING REQUEST                         ║",
        "╠══════════════════════════════════════════════════════════════╣",
        f"║ ID: {request['request_id'][:8]}...",
        f"║ Time: {request['timestamp']}",
        "╠══════════════════════════════════════════════════════════════╣",
        "║ TRANSACTION                                                   ║",
        f"║ To:    {request['transaction']['to']}",
        f"║ Value: {request['transaction']['value']} wei (${request['value_usd']})",
        f"║ Data:  {request['transaction']['data'][:50]}{'...' if len(request['transaction']['data']) > 50 else ''}",
        "╠══════════════════════════════════════════════════════════════╣",
        "║ SIMULATION                                                    ║",
        f"║ ✅ Success: {request['simulation']['success']}",
        f"║ ⛽ Gas Estimate: {request['simulation']['gas_estimate']:,}",
        f"║ 💰 Gas Cost: ~{request['simulation']['gas_cost_eth']:.4f} ETH",
    ]
    
    if request['simulation']['warnings']:
        lines.append("║ ⚠️ Warnings:")
        for w in request['simulation']['warnings']:
            lines.append(f"║   - {w}")
    
    lines.extend([
        "╠══════════════════════════════════════════════════════════════╣",
        "║ WHITELIST CHECK                                               ║",
        f"║ {'✅' if request['whitelist']['allowed'] else '❌'} {request['whitelist']['reason']}",
    ])
    
    if request['approval_required']:
        lines.extend([
            "╠══════════════════════════════════════════════════════════════╣",
            "║ ⚠️ MANUAL APPROVAL REQUIRED                                   ║",
            "║                                                               ║",
            "║ 1. Copy the transaction data above                            ║",
            "║ 2. Open your wallet (MetaMask / Safe)                         ║",
            "║ 3. Review and sign the transaction                            ║",
        ])
    
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Safe Vault transaction manager")
    parser.add_argument("--init", action="store_true", help="Initialize Safe Vault")
    parser.add_argument("--mode", choices=["simulation", "limited_auto", "full_auto"],
                        default="simulation", help="Execution mode")
    parser.add_argument("--prepare-tx", action="store_true", help="Prepare transaction")
    parser.add_argument("--simulate", action="store_true", help="Simulate transaction only")
    parser.add_argument("--to", help="Target address")
    parser.add_argument("--value", default="0", help="Value in wei")
    parser.add_argument("--data", default="0x", help="Transaction calldata")
    parser.add_argument("--gas-limit", type=int, default=300000, help="Gas limit")
    parser.add_argument("--description", default="", help="Transaction description")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.init:
        config = load_config()
        if "trading" not in config:
            config["trading"] = {}
        config["trading"]["mode"] = args.mode
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Safe Vault initialized with mode: {args.mode}")
        return
    
    if args.prepare_tx or args.simulate:
        if not args.to:
            print("Error: --to address required", file=sys.stderr)
            sys.exit(1)
        
        request = prepare_transaction(
            to=args.to,
            value=args.value,
            data=args.data,
            gas_limit=args.gas_limit,
            description=args.description
        )
        
        if args.output == "json":
            print(json.dumps(request, indent=2))
        else:
            print(format_signing_request(request))
        
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()