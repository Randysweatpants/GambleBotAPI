import os, asyncio, math, traceback, itertools, time, random
from typing import List, Dict, Tuple, Any
import requests

from flask import Flask
from threading import Thread
app = Flask(__name__)

@app.get("/")
def home():
    return "EV Parlay Pro is running!", 200

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

Thread(target=run_web, daemon=True).start()

import discord
from discord.ext import commands

DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
BANKROLL = float(os.getenv("BANKROLL", "1000"))
DEFAULT_REGION = os.getenv("ODDS_REGION", "us")
DEFAULT_MARKETS = ["h2h", "spreads", "totals"]

DEFAULT_BOOKS_STR = os.getenv("BOOKS", "")
DEFAULT_BOOKS = [b.strip().lower() for b in DEFAULT_BOOKS_STR.split(",") if b.strip()]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

def american_to_decimal(american: float) -> float:
    if american > 0:
        return 1 + american / 100.0
    else:
        return 1 + 100.0 / abs(american)

def decimal_to_american(decimal_odds: float) -> int:
    if decimal_odds >= 2:
        return int(round((decimal_odds - 1) * 100))
    else:
        return int(round(-100 / (decimal_odds - 1)))

def implied_from_decimal(d: float) -> float:
    return 1.0 / d

def devig_two_way(p1_mkt: float, p2_mkt: float) -> Tuple[float, float, float]:
    s = p1_mkt + p2_mkt
    return p1_mkt / s, p2_mkt / s, s

def kelly_fraction(p: float, decimal_price: float) -> float:
    b = decimal_price - 1.0
    q = 1.0 - p
    f = (b * p - q) / b if b > 0 else 0.0
    return max(0.0, f)

def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default

def get_odds(sport_key: str, regions: str, markets: List[str], books_filter: List[str]) -> List[Dict[str, Any]]:
    if not ODDS_API_KEY:
        raise RuntimeError("ODDS_API_KEY missing. Add it in Replit Secrets.")
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": ",".join(markets),
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if books_filter:
        for ev in data:
            ev["bookmakers"] = [b for b in ev.get("bookmakers", []) if b.get("key", "").lower() in books_filter]
    return data

def sport_to_key(sport: str) -> str:
    s = sport.lower()
    if s in ("nba", "basketball", "basketball_nba"): return "basketball_nba"
    if s in ("nfl", "football_nfl"): return "americanfootball_nfl"
    if s in ("nhl", "icehockey_nhl"): return "icehockey_nhl"
    return "basketball_nba"

def extract_two_way_legs(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    legs = []
    for ev in events:
        game_id = ev.get("id")
        game_time = ev.get("commence_time")
        home = ev.get("home_team", "")
        away = ev.get("away_team", "")
        for bm in ev.get("bookmakers", []):
            book = bm.get("key", "")
            for m in bm.get("markets", []):
                market_key = m.get("key")
                outcomes = m.get("outcomes", [])
                if market_key == "h2h" and len(outcomes) >= 2:
                    oc = outcomes[:2]
                    p1_mkt = implied_from_decimal(american_to_decimal(oc[0]["price"]))
                    p2_mkt = implied_from_decimal(american_to_decimal(oc[1]["price"]))
                    p1_fair, p2_fair, overround = devig_two_way(p1_mkt, p2_mkt)
                    if 0.98 <= overround <= 1.10:
                        for idx in (0, 1):
                            sel = oc[idx]
                            team = sel.get("name")
                            dec = american_to_decimal(sel["price"])
                            legs.append({
                                "game_id": game_id,
                                "game_time": game_time,
                                "market": "ML",
                                "selection": team,
                                "price_dec": dec,
                                "price_amer": sel["price"],
                                "p_fair": p1_fair if idx == 0 else p2_fair,
                                "book": book,
                                "notes": f"{away} @ {home} — {book}",
                            })
                elif market_key == "totals" and len(outcomes) >= 2:
                    oc = sorted(outcomes, key=lambda x: x.get("name",""))
                    p1_mkt = implied_from_decimal(american_to_decimal(oc[0]["price"]))
                    p2_mkt = implied_from_decimal(american_to_decimal(oc[1]["price"]))
                    p1_fair, p2_fair, overround = devig_two_way(p1_mkt, p2_mkt)
                    if 0.98 <= overround <= 1.10:
                        for idx in (0, 1):
                            sel = oc[idx]
                            dec = american_to_decimal(sel["price"])
                            legs.append({
                                "game_id": game_id,
                                "game_time": game_time,
                                "market": f"Total {sel.get('point')}",
                                "selection": sel.get("name"),
                                "price_dec": dec,
                                "price_amer": sel["price"],
                                "p_fair": p1_fair if idx == 0 else p2_fair,
                                "book": book,
                                "notes": f"{away} @ {home} — {book}",
                            })
                elif market_key == "spreads" and len(outcomes) >= 2:
                    oc = outcomes[:2]
                    p1_mkt = implied_from_decimal(american_to_decimal(oc[0]["price"]))
                    p2_mkt = implied_from_decimal(american_to_decimal(oc[1]["price"]))
                    p1_fair, p2_fair, overround = devig_two_way(p1_mkt, p2_mkt)
                    if 0.98 <= overround <= 1.10:
                        for idx in (0, 1):
                            sel = oc[idx]
                            side = sel.get("name")
                            pt = sel.get("point")
                            dec = american_to_decimal(sel["price"])
                            legs.append({
                                "game_id": game_id,
                                "game_time": game_time,
                                "market": f"Spread {pt}",
                                "selection": side,
                                "price_dec": dec,
                                "price_amer": sel["price"],
                                "p_fair": p1_fair if idx == 0 else p2_fair,
                                "book": book,
                                "notes": f"{away} @ {home} — {book}",
                            })
    return legs

def correlation_multiplier(legs: List[Dict[str, Any]]) -> float:
    by_game = {}
    for leg in legs:
        by_game.setdefault(leg["game_id"], 0)
        by_game[leg["game_id"]] += 1
    penalty = 1.0
    for _, cnt in by_game.items():
        if cnt > 1:
            penalty *= (0.90 ** (cnt - 1))
    return penalty

def parlay_ev(legs: List[Dict[str, Any]]) -> Dict[str, Any]:
    price_dec = 1.0
    p_fair = 1.0
    for lg in legs:
        price_dec *= lg["price_dec"]
        p_fair *= lg["p_fair"]
    corr = correlation_multiplier(legs)
    p_parlay = max(0.0, min(1.0, p_fair * corr))
    ev_per_1 = p_parlay * price_dec - 1.0
    k = kelly_fraction(p_parlay, price_dec)
    k_clipped = min(k, 0.15)
    k_suggest = 0.5 * k_clipped
    return {
        "price_dec": price_dec,
        "price_amer": decimal_to_american(price_dec),
        "p_win": p_parlay,
        "ev_per_1": ev_per_1,
        "kelly": k,
        "kelly_clipped": k_clipped,
        "stake_suggest": k_suggest * BANKROLL,
        "corr_mult": corr
    }

def build_parlays(cands: List[Dict[str, Any]], max_legs: int, min_ev: float, same_game_only: bool, diversify: bool=True) -> List[Dict[str, Any]]:
    key_map = {}
    for lg in cands:
        k = (lg["game_id"], lg["market"], lg["selection"], lg["book"])
        old = key_map.get(k)
        if not old or lg["price_dec"] > old["price_dec"]:
            key_map[k] = lg
    legs = list(key_map.values())

    combos = []
    pool = legs

    sizes = [2, 3] if max_legs <= 3 else [2, 3, 4]
    for r in sizes:
        for comb in itertools.combinations(pool, r):
            gset = {x["game_id"] for x in comb}
            if same_game_only and len(gset) != 1:
                continue
            ok = True
            seen = {}
            for x in comb:
                mk = (x["game_id"], x["market"])
                seen.setdefault(mk, set())
                if x["selection"] in seen[mk]:
                    ok = False
                    break
                seen[mk].add(x["selection"])
            if not ok:
                continue
            meta = parlay_ev(list(comb))
            if meta["ev_per_1"] >= min_ev:
                combos.append({
                    "legs": list(comb),
                    "meta": meta
                })

    combos.sort(key=lambda x: (x["meta"]["ev_per_1"], x["meta"]["p_win"]), reverse=True)
    if diversify and not same_game_only:
        chosen = []
        used_games = set()
        for c in combos:
            games = {lg["game_id"] for lg in c["legs"]}
            if len(used_games.intersection(games)) == len(games):
                continue
            chosen.append(c)
            used_games.update(games)
        if len(chosen) >= 3:
            return chosen
    return combos

def format_parlay_embed_title(sport: str, min_ev: float) -> str:
    return f"Top +EV Parlays — {sport.upper()}, min EV {int(min_ev*100)}%"

def parlay_to_embed_field(idx: int, parlay: Dict[str, Any]) -> Tuple[str, str, bool]:
    meta = parlay["meta"]
    price_dec = meta["price_dec"]
    price_amer = meta["price_amer"]
    p_win = meta["p_win"]
    ev_per_1 = meta["ev_per_1"]
    stake = meta["stake_suggest"]
    corr = meta["corr_mult"]

    legs_lines = []
    for lg in parlay["legs"]:
        legs_lines.append(f"• **{lg['selection']}** ({lg['market']}) @ **{lg['book']}** — {lg['price_dec']:.2f} ({lg['price_amer']:+d})")

    notes = []
    notes.append(f"P(win): **{p_win:.2%}**")
    notes.append(f"Price: **{price_dec:.2f} ({price_amer:+d})**")
    notes.append(f"EV per $1: **{ev_per_1:+.3f}**")
    notes.append(f"Correlation: ×**{corr:.3f}**")
    notes.append(f"Suggested stake: **${stake:.2f}** (½ of Kelly, clip 15%)")

    value = "\n".join(legs_lines + [""] + notes)
    name = f"#{idx+1}"
    return name, value, False

async def fetch_and_build(sport: str, books: str, min_ev: float, max_legs: int, top_n: int, same_game_only: bool):
    sport_key = sport_to_key(sport if sport and sport.lower() != "any" else "nba")
    books_filter = [b.strip().lower() for b in books.split(",") if b.strip()] if books else DEFAULT_BOOKS

    def _pull():
        evs = get_odds(sport_key, DEFAULT_REGION, DEFAULT_MARKETS, books_filter)
        return evs
    events = await asyncio.to_thread(_pull)

    candidates = extract_two_way_legs(events)
    random.shuffle(candidates)
    parlays = build_parlays(candidates, max_legs=max_legs, min_ev=min_ev, same_game_only=same_game_only, diversify=True)
    return parlays[:top_n]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (latency {round(bot.latency*1000)} ms)")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("EV Parlay Pro online and sharp 👌")

@bot.command(name="best")
async def best(ctx, sport: str = "ANY", books: str = "", min_ev: float = 0.02, max_legs: int = 3, top_n: int = 5, same_game_only: bool = False):
    await ctx.trigger_typing()
    try:
        parlays = await fetch_and_build(sport, books, float(min_ev), int(max_legs), int(top_n), bool(same_game_only))
        title = format_parlay_embed_title(sport, float(min_ev))
        embed = discord.Embed(title=title, color=0x2ecc71)
        if not parlays:
            embed.description = "No +EV parlays found with those filters. Try lowering min_ev or allowing more books."
        else:
            for i, p in enumerate(parlays):
                name, value, inline = parlay_to_embed_field(i, p)
                embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Educational use only. Gamble responsibly. Kelly clipped at 15%, suggestion uses 50% of clip.")
        await ctx.send(embed=embed)
    except Exception as e:
        traceback.print_exc()
        await ctx.send(f"⚠️ Error: {e}\n(Verify ODDS_API_KEY and that your sport has upcoming games.)")

async def main():
    while True:
        try:
            await bot.start(DISCORD_TOKEN)
        except Exception:
            traceback.print_exc()
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
