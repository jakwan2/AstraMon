# 🐾 Astramon Bot Setup Instructions

## ⚠️ IMPORTANT: Discord Developer Portal Setup Required

Your bot is crashing because it needs the **Message Content Intent** enabled in Discord. This is a required privileged intent for prefix-based commands.

## Step-by-Step Setup Guide

### 1. Go to Discord Developer Portal
Visit: https://discord.com/developers/applications/

### 2. Select Your Application
- Click on your bot application from the list

### 3. Enable Message Content Intent
- Go to the **"Bot"** section in the left sidebar
- Scroll down to **"Privileged Gateway Intents"**
- **Enable** the toggle for **"MESSAGE CONTENT INTENT"**
- Click **"Save Changes"** at the bottom

### 4. Get Your Bot Token (if you don't have it)
- Still in the **"Bot"** section
- Click **"Reset Token"** or **"View Token"**
- Copy the token

### 5. Add Token to Replit Secrets
- In Replit, click the **🔒 Secrets** tab (Tools → Secrets)
- Add a new secret:
  - **Key**: `DISCORD_BOT_TOKEN`
  - **Value**: Paste your Discord bot token
- Click **"Add Secret"**

### 6. Run Your Bot
- The bot should now start automatically!
- You should see: **"Astramon is online! 🐾"** in the console

## ✅ Quick Checklist

- [ ] Message Content Intent enabled in Discord Developer Portal
- [ ] Bot token copied from Discord Developer Portal  
- [ ] Secret `DISCORD_BOT_TOKEN` added in Replit
- [ ] Bot shows "Astramon is online! 🐾" in console

## 🆘 Troubleshooting

**Bot still crashes with "PrivilegedIntentsRequired"?**
- Make sure you clicked "Save Changes" in Discord Developer Portal
- Try resetting your bot token and updating the secret in Replit

**Bot says "DISCORD_BOT_TOKEN not found"?**
- Check the secret name is exactly: `DISCORD_BOT_TOKEN` (all caps)
- Make sure you clicked "Add Secret" in Replit

**Bot doesn't respond to commands?**
- Make sure the bot is invited to your server with proper permissions
- Use the correct prefix: `astramon ` (with a space)
- Example: `astramon catch`

## 📝 Important Notes

- **Message Content Intent** is REQUIRED for prefix commands to work
- Without this intent enabled, the bot cannot read message content
- This is a Discord requirement, not a Replit limitation

## 🔗 Useful Links

- Discord Developer Portal: https://discord.com/developers/applications/
- Discord Intents Guide: https://discord.com/developers/docs/topics/gateway#gateway-intents
