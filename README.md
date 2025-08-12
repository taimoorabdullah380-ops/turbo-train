# turbo-train
Maker
# MEXC Futures Telegram Bot

This bot connects to the MEXC Futures WebSocket and:
- Sends **instant alerts** when a coin moves 1–1.5% in the last minute
- Sends a **summary every minute** of all coins that had such moves
- Shows move direction (📈 UP / 📉 DOWN) and current price

## Deployment (Railway)
1. Fork this repo
2. Go to [Railway.app](https://railway.app/)
3. Create a New Project → Deploy from GitHub
4. Set Environment Variables:
   - `TELEGRAM_TOKEN` → Your Telegram bot token from BotFather
   - `CHAT_ID` → Your Telegram numeric chat ID
5. Deploy and enjoy real-time alerts!
