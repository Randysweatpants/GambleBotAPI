# EV Parlay Pro - Discord Bot Setup

## Quick Start

Your bot is configured and ready to go! Here's what you need to do:

### 1. Enable Message Content Intent in Discord Developer Portal

To allow your bot to read and respond to commands, you need to enable the "Message Content Intent":

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application (the one you got your bot token from)
3. Click on the **Bot** tab in the left sidebar
4. Scroll down to **Privileged Gateway Intents**
5. Enable **MESSAGE CONTENT INTENT** (toggle it ON)
6. Click **Save Changes**

### 2. Invite Your Bot to Your Server

If you haven't already invited your bot to your Discord server:

1. In the Discord Developer Portal, go to **OAuth2** → **URL Generator**
2. Under **Scopes**, select: `bot`
3. Under **Bot Permissions**, select:
   - Send Messages
   - Embed Links
   - Read Messages/View Channels
   - Read Message History
4. Copy the generated URL at the bottom
5. Paste it in your browser and select your server to add the bot

### 3. Restart the Bot

After enabling the Message Content Intent, click the **Stop** button on the Discord Bot workflow in Replit, then click **Run** again. The bot will reconnect with the proper permissions.

## Using the Bot

Once your bot is running and invited to your server, you can use these commands:

### `/ping`
Check if the bot is online and responsive.
```
/ping
```

### `/best`
Find the top +EV (positive expected value) parlays based on current odds.

**Usage:**
```
/best [sport] [books] [min_ev] [max_legs] [top_n] [same_game_only]
```

**Parameters:**
- `sport` - Sport to analyze: `NBA`, `NFL`, `NHL`, or `ANY` (default: ANY)
- `books` - Comma-separated sportsbooks (e.g., `draftkings,fanduel,betmgm`). Leave blank for all available books.
- `min_ev` - Minimum expected value threshold as decimal (default: 0.02 = 2% edge)
- `max_legs` - Maximum parlay legs 2-4 (default: 3)
- `top_n` - Number of parlays to show, 1-10 (default: 5)
- `same_game_only` - Only show same-game parlays: `True` or `False` (default: False)

**Examples:**
```
/best
/best NBA
/best NFL fanduel,draftkings 0.03 3 5 False
/best NBA "" 0.05 2 3 True
```

## How It Works

The bot uses advanced betting mathematics to find profitable parlay opportunities:

1. **Fetches Real-Time Odds** - Pulls current odds from The Odds API across multiple sportsbooks
2. **Removes the Vig** - Calculates fair probabilities by removing bookmaker margins
3. **Builds Parlays** - Generates 2-4 leg parlay combinations from available legs
4. **Applies Correlation Penalty** - Reduces win probability for same-game parlays (0.90 multiplier per additional leg)
5. **Calculates EV** - Computes expected value: (Fair Win % × Payout) - 1
6. **Kelly Criterion Sizing** - Suggests optimal stake size based on your bankroll (clipped at 15%, uses 50% fractional Kelly)

## Configuration

You can customize the bot's behavior with environment variables:

- `BANKROLL` - Your betting bankroll for Kelly sizing (default: 1000)
- `ODDS_REGION` - Region for odds: `us`, `uk`, `eu`, `au` (default: us)
- `BOOKS` - Default sportsbooks to filter (comma-separated)

## Important Notes

⚠️ **Educational Use Only** - This bot is for educational and research purposes. Always gamble responsibly.

⚠️ **API Usage** - The Odds API has usage limits. The free tier allows ~500 requests/month. Each `/best` command uses 1 request.

⚠️ **No Guarantees** - Past performance doesn't guarantee future results. Positive EV doesn't mean guaranteed profit on individual bets.

## Troubleshooting

**Bot doesn't respond to commands:**
- Make sure you enabled "Message Content Intent" in Discord Developer Portal
- Restart the bot workflow after enabling the intent
- Verify the bot has proper permissions in your server

**"ODDS_API_KEY missing" error:**
- Check that your Odds API key is set in Replit Secrets
- Verify the key is valid at [the-odds-api.com](https://the-odds-api.com)

**"No +EV parlays found" message:**
- Try lowering the `min_ev` parameter (e.g., 0.01 for 1% edge)
- Remove book filters to search across all available sportsbooks
- Check that there are upcoming games in your selected sport
