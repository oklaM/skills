#!/usr/bin/env python3
"""
Find investment opportunities from DefiLlama API.

Usage:
    python find_opportunities.py --min-apy 5 --max-risk medium
    python find_opportunities.py --protocol aave-v3 --output json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional
import urllib.request
import urllib.error

# DefiLlama API endpoints
DEFILLAMA_BASE = "https://yields.llama.fi"
DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"

# Risk scoring (see references/risk-framework.md)
def calculate_risk_score(protocol: dict) -> int:
    """Calculate risk score 0-10 based on framework."""
    score = 0
    
    # Maturity (0-3)
    if protocol.get("audits") and protocol.get("audit_note"):
        score += 0  # Audited
    else:
        score += 2  # No audit
    
    # TVL (0-2)
    tvl = protocol.get("tvl", 0) or 0
    if tvl > 1_000_000_000:  # > $1B
        score += 0
    elif tvl > 100_000_000:  # > $100M
        score += 1
    else:
        score += 2
    
    # Age (0-3) - proxy from audits and known protocols
    known_protocols = [
        "aave", "compound", "makerdao", "lido", "rocket-pool",
        "uniswap", "curve", "convex", "yearn"
    ]
    if any(kp in protocol.get("name", "").lower() for kp in known_protocols):
        score += 0
    else:
        score += 2
    
    return min(score, 10)


def risk_level(score: int) -> str:
    """Convert risk score to level."""
    if score <= 3:
        return "low"
    elif score <= 6:
        return "medium"
    else:
        return "high"


def fetch_yields() -> dict:
    """Fetch all yield data from DefiLlama."""
    url = f"{DEFILLAMA_BASE}/pools"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching yields: {e}", file=sys.stderr)
        return {"data": []}


def fetch_protocols() -> list:
    """Fetch protocol list from DefiLlama."""
    try:
        with urllib.request.urlopen(DEFILLAMA_PROTOCOLS, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching protocols: {e}", file=sys.stderr)
        return []


def find_opportunities(
    min_apy: float = 0,
    max_risk: str = "medium",
    chain: str = "Ethereum",
    min_tvl: float = 0,
    require_audit: bool = False,
    limit: int = 20
) -> list:
    """
    Find investment opportunities matching criteria.
    
    Args:
        min_apy: Minimum APY percentage
        max_risk: Maximum risk level (low, medium, high)
        chain: Blockchain to search
        min_tvl: Minimum TVL in USD
        require_audit: Require audited protocols
        limit: Maximum results to return
    
    Returns:
        List of opportunity dicts
    """
    # Fetch data
    yields_data = fetch_yields()
    protocols_data = fetch_protocols()
    
    if not yields_data.get("data"):
        print("Warning: No yield data received", file=sys.stderr)
        return []
    
    # Build protocol lookup
    protocol_map = {}
    for p in protocols_data:
        slug = p.get("slug", p.get("name", "")).lower()
        protocol_map[slug] = p
        # Also map by name
        protocol_map[p.get("name", "").lower()] = p
    
    opportunities = []
    risk_order = {"low": 0, "medium": 1, "high": 2}
    max_risk_value = risk_order.get(max_risk, 1)
    
    for pool in yields_data.get("data", []):
        # Filter by chain
        if chain.lower() not in pool.get("chain", "").lower():
            continue
        
        # Filter by APY
        apy = pool.get("apy", 0) or 0
        if apy < min_apy:
            continue
        
        # Filter by TVL
        tvl = pool.get("tvlUsd", 0) or 0
        if tvl < min_tvl:
            continue
        
        # Get protocol info
        protocol_name = pool.get("project", "")
        protocol = protocol_map.get(protocol_name.lower(), {})
        
        # Calculate risk
        risk_score = calculate_risk_score(protocol)
        risk_lvl = risk_level(risk_score)
        
        # Filter by risk
        if risk_order.get(risk_lvl, 1) > max_risk_value:
            continue
        
        # Filter by audit requirement
        if require_audit and not protocol.get("audits"):
            continue
        
        opportunities.append({
            "pool": pool.get("pool", ""),
            "protocol": protocol_name,
            "protocol_name": protocol.get("name", protocol_name),
            "chain": pool.get("chain", "Ethereum"),
            "symbol": pool.get("symbol", ""),
            "apy": round(apy, 2),
            "apy_base": round(pool.get("apyBase", 0) or 0, 2),
            "apy_reward": round(pool.get("apyReward", 0) or 0, 2),
            "tvl_usd": tvl,
            "risk_score": risk_score,
            "risk_level": risk_lvl,
            "underlying_tokens": pool.get("underlyingTokens", []),
            "reward_tokens": pool.get("rewardTokens", []),
            "stablecoin": pool.get("stablecoin", False),
            "audited": bool(protocol.get("audits")),
            "url": f"https://defillama.com/yield/pool/{pool.get('pool', '')}"
        })
    
    # Sort by APY (descending)
    opportunities.sort(key=lambda x: x["apy"], reverse=True)
    
    return opportunities[:limit]


def format_report(opportunities: list, output_format: str = "markdown") -> str:
    """Format opportunities as report."""
    if not opportunities:
        return "No opportunities found matching criteria."
    
    if output_format == "json":
        return json.dumps(opportunities, indent=2)
    
    # Markdown format
    lines = [
        "# Investment Opportunities",
        f"\nGenerated: {datetime.now().isoformat()}",
        f"Found: {len(opportunities)} pools\n",
        "---\n"
    ]
    
    for i, opp in enumerate(opportunities, 1):
        lines.extend([
            f"## {i}. {opp['protocol']} - {opp['symbol']}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| APY | **{opp['apy']}%** |",
            f"| TVL | ${opp['tvl_usd']:,.0f} |",
            f"| Risk Level | {opp['risk_level'].upper()} ({opp['risk_score']}/10) |",
            f"| Chain | {opp['chain']} |",
            f"| Audited | {'✅' if opp['audited'] else '❌'} |",
            "",
            f"**Pool**: `{opp['pool']}`",
            f"**Link**: {opp['url']}",
            ""
        ])
        
        if opp['apy_reward'] > 0:
            lines.extend([
                f"**Yield Breakdown**: Base {opp['apy_base']}% + Rewards {opp['apy_reward']}%",
                ""
            ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find DeFi investment opportunities")
    parser.add_argument("--min-apy", type=float, default=0, help="Minimum APY %%")
    parser.add_argument("--max-risk", choices=["low", "medium", "high"], default="medium",
                        help="Maximum risk level")
    parser.add_argument("--chain", default="Ethereum", help="Blockchain to search")
    parser.add_argument("--min-tvl", type=float, default=0, help="Minimum TVL in USD")
    parser.add_argument("--require-audit", action="store_true", help="Require audited protocols")
    parser.add_argument("--limit", type=int, default=20, help="Maximum results")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    
    args = parser.parse_args()
    
    opportunities = find_opportunities(
        min_apy=args.min_apy,
        max_risk=args.max_risk,
        chain=args.chain,
        min_tvl=args.min_tvl,
        require_audit=args.require_audit,
        limit=args.limit
    )
    
    print(format_report(opportunities, args.output))


if __name__ == "__main__":
    main()