# EV Parlay Pro - Discord Bot

## Overview
A Discord bot that finds positive expected value (EV) sports betting parlays using The Odds API. The bot analyzes real-time odds from multiple sportsbooks, removes the vig (bookmaker margin), calculates fair probabilities, and identifies profitable parlay opportunities.

## Features
- **Real-time odds analysis** from multiple sportsbooks via The Odds API
- **Vig removal** using proportional method for fair probability estimation
- **Kelly Criterion** stake sizing with conservative 15% clip and 50% fractional Kelly
- **Correlation adjustments** for same-game parlays (0.90 penalty per additional leg)
- **Multi-sport support**: NBA, NFL, NHL
- **Multiple markets**: Moneylines (ML), Spreads, Totals (Over/Under)
- **Flexible filtering**: By sportsbook, minimum EV threshold, same-game restrictions
- **Rich Discord embeds** showing parlay details, win probability, and suggested stakes

## Commands
- `/ping` - Check if bot is online
- `/best [sport] [books] [min_ev] [max_legs] [top_n] [same_game_only]` - Find top +EV parlays

## Environment Variables
- `DISCORD_BOT_TOKEN` - Discord bot authentication token (required)
- `ODDS_API_KEY` - The Odds API key (required)
- `BANKROLL` - Bankroll amount for Kelly sizing (default: 1000)
- `ODDS_REGION` - Odds region: us, uk, eu, au (default: us)
- `BOOKS` - Comma-separated list of sportsbooks to include (optional)

## Architecture
- **Backend**: Python 3.11 with discord.py
- **Web server**: Flask keepalive server on port 8080
- **API integration**: The Odds API for real-time betting odds
- **Discord integration**: Replit Discord connector for authentication

## Math & Methodology
1. **Vig Removal**: Uses proportional method to remove bookmaker margin from market prices
2. **Fair Probability**: Calculates true probability after vig removal
3. **Parlay Pricing**: Multiplies decimal odds across legs
4. **Correlation Penalty**: Applies 0.90^(n-1) penalty for same-game parlays
5. **Kelly Criterion**: Calculates optimal stake size, clipped at 15%, uses 50% fractional Kelly
6. **EV Calculation**: (P_win × Payout) - 1

## Project Structure
```
main.py - Discord bot with EV calculation engine
.gitignore - Python gitignore patterns
replit.md - Project documentation
```

## Recent Changes
- Initial project setup (Oct 27, 2025)
- Discord integration configured
- Core EV calculation engine implemented
- Added README.md with setup instructions
- Configured workflow to run Discord bot

## Setup Required
⚠️ **Important**: You must enable "Message Content Intent" in the Discord Developer Portal for the bot to work:
1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to Bot → Privileged Gateway Intents
4. Enable "MESSAGE CONTENT INTENT"
5. Save changes and restart the bot workflow

See README.md for complete setup instructions.
