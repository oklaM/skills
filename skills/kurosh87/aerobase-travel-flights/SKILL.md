---
name: aerobase-travel-flights
description: Search, compare, and score flights with jetlag optimization
metadata: {"openclaw": {"emoji": "🛫", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Flight Search

Find the perfect flight with jetlag optimization. Aerobase.app scores every flight 0-100 for recovery impact — so you arrive fresh.

**Why Aerobase?**
- 😴 **Jetlag scoring** — Every flight scored 0-100 for recovery
- 🔍 **Compare options** — Side-by-side comparison
- 🎯 **Multi-provider** — Kiwi, Amadeus, and more
- 📊 **Smart ranking** — Best value = price + jetlag combined

## What This Skill Does

- Search flights with jetlag scoring
- Compare multiple flight options
- Score flights 0-100 for recovery impact
- Recommend optimal departure/arrival times
- Generate recovery plans for each trip

## Example Conversations

```
User: "Find flights from LAX to NRT next week - but I need to be functional the next day"
→ Scores each flight for jetlag
→ Prioritizes recovery-friendly times
→ Recommends best option for productivity

User: "Compare these 3 flights for jetlag impact"
→ Side-by-side comparison
→ Shows recovery days for each
→ Recommends optimal choice
```

## API Endpoints

**POST /api/v1/flights/score**

```json
{
  "from": "LAX",
  "to": "NRT",
  "departure": "2026-04-15T13:25:00-07:00",
  "arrival": "2026-04-16T15:40:00+09:00",
  "cabin": "business"
}
```

Returns score (0-100), recovery days, direction, and strategies.

**POST /api/v1/flights/search** — Search with scoring
**POST /api/v1/flights/compare** — Compare multiple flights

## Rate Limits

- **Free tier**: 5 API requests per day
- **Premium tier**: Unlimited requests + recovery plans

Get free API key at: https://aerobase.app/connect

## Premium: Recovery Plans

Premium subscribers get personalized recovery plans:
- Pre-trip preparation schedule
- In-flight strategies
- Arrival timing recommendations
- Sleep/diet adjustments

→ https://aerobase.app/concierge/pricing

## Get the Full Experience

Want ALL travel capabilities? Install the complete **Aerobase Travel Concierge** skill:
- Flights, hotels, lounges, awards, activities, deals, wallet
- Plus premium recovery plans
- One skill for everything

→ https://clawhub.ai/kurosh87/aerobase-travel-concierge
