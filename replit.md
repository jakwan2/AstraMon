# Astramon Discord Bot

## Overview
Astramon is a Discord bot for collecting, battling, and caring for elemental monsters. The bot uses prefix-based commands (not slash commands) with an Owo-style cute messaging theme.

## Project Status
✅ Core implementation complete
✅ 24/7 uptime system configured with Flask keep-alive server
✅ Bot is running and ready for use

## Features Implemented
- **Monster Catching System**: Catch random monsters with 5 elemental types (Fire 🔥, Water 💧, Earth 🌱, Wind 🌪️, Lightning ⚡)
- **Rarity System**: Common (75%), Rare (20%), Legendary (5%) with dual-element legendaries
- **Feeding & Hunger**: Monsters get hungry over time, send DM alerts when starving, die if neglected
- **Shop System**: Purchase food items with shards (in-game currency)
- **Evolution System**: Evolve common monsters into rare forms for 500 shards
- **Battle System**: PvP or battle bot with elemental advantage mechanics
- **Anime Quiz**: Answer trivia for shard rewards with 5-minute cooldown
- **Profile Command**: View monster collection, stats, and shards
- **Help Command**: Display all commands with descriptions

## Technical Stack
- **Language**: Python 3.11
- **Libraries**: 
  - discord.py 2.6.4 (Discord bot framework)
  - Flask 3.1.2 (Keep-alive web server for 24/7 uptime)
- **Data Storage**: JSON file (data.json) for persistence
- **Prefix**: `astramon ` (with space)
- **24/7 Uptime**: Flask web server on port 5000 for UptimeRobot monitoring

## Commands
- `astramon catch` - Catch a random wild monster (30s cooldown)
- `astramon feed <monster>` - Feed a monster (costs 50💎)
- `astramon train <monster>` - Train a monster to increase level & attack (costs 100💎)
- `astramon shop` - View the food shop
- `astramon evolve <monster>` - Evolve a monster (costs 500💎)
- `astramon battle [@user]` - Battle another user or the bot
- `astramon quiz` - Answer anime trivia for rewards (5min cooldown)
- `astramon profile [@user]` - View monster collection and stats
- `astramon help` - Display help message

## Game Mechanics
### Elements & Advantages
Fire > Wind > Earth > Lightning > Water > Fire

### Currency System (Shards 💎)
- Earn 50💎 per catch
- Earn 150💎 per battle win
- Earn 100💎 per correct quiz answer
- Spend on feeding (50💎), training (100💎), and evolution (500💎)

### Hunger System
- Hunger increases 10 points per hour
- At 90+ hunger: DM alert sent to owner
- At 100 hunger: Monster dies and is removed

## Monster Database
### Common Monsters
Fire Pup, Water Bunny, Earth Turtle, Wind Purr, Spark Mouse, Flame Fox, Wave Frog, Stone Panda, Gust Bird, Bolt Hamster

### Rare Monsters
Inferno Wolf, Tidal Dolphin, Stonefang, Stormlynx, Thunder Drake

### Legendary Monsters
Phoenix Emperor (Fire|Wind), Leviathan King (Water|Earth), Storm Dragon (Lightning|Wind), Terra Beast (Earth|Fire)

## Setup Instructions

### ⚠️ CRITICAL: Discord Developer Portal Setup
**Before running the bot, you MUST enable the Message Content Intent:**

1. Go to https://discord.com/developers/applications/
2. Select your bot application
3. Navigate to **Bot** section → **Privileged Gateway Intents**
4. **Enable "MESSAGE CONTENT INTENT"** toggle
5. Click **Save Changes**

### Adding Bot Token to Replit
1. Python 3.11 and discord.py are already installed
2. Add your Discord bot token to Replit Secrets (🔒 icon):
   - Secret name: `DISCORD_BOT_TOKEN`
   - Value: Your Discord bot token from Discord Developer Portal
3. Run the bot - it will print "Astramon is online! 🐾" when ready

### 24/7 Uptime Setup (Optional)
The bot includes a Flask web server on port 5000 for keep-alive monitoring:

1. **Get Your Replit URL**: Copy the webview URL (e.g., `https://yourproject.yourname.repl.co`)
2. **Set Up UptimeRobot** (free service):
   - Go to https://uptimerobot.com and create a free account
   - Create a new monitor:
     - Monitor Type: HTTP(s)
     - URL: Your Replit webview URL
     - Monitoring Interval: 5 minutes
   - This will ping your bot every 5 minutes to keep it alive 24/7

The Flask server responds with "Astramon bot is running 24/7!" when accessed.

### Troubleshooting
- If bot crashes with "PrivilegedIntentsRequired" error, enable Message Content Intent in Discord Portal
- See `SETUP_INSTRUCTIONS.md` for detailed setup guide

## File Structure
- `main.py` - Main bot code with all commands and game logic
- `data.json` - User data storage (monsters, shards, stats)
- `.gitignore` - Python and virtual environment files ignored

## Recent Changes
- 2025-10-11: Added Flask keep-alive web server for 24/7 uptime support
- 2025-10-11: Configured multi-threading to run Discord bot and web server simultaneously
- 2025-10-10: Added train feature - monsters can level up and gain attack power
- 2025-10-10: Initial bot implementation with all core features
- All commands tested and working
- Persistent data storage implemented
- Hunger system with DM alerts functional
- Battle system with elemental advantages working

## User Preferences
- Owo-style cute messaging (Nyaa~, UwU, etc.)
- Emoji-rich responses
- No slash commands - prefix-based only
- Anime-themed content
