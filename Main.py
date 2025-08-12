import time
import json
import websocket
import threading
from telegram import Bot
import os

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WS_URL = "wss://contract.mexc.com/ws"
ALERT_COOLDOWN = 60  # seconds between alerts for same coin
# ===========================================

bot = Bot(token=TELEGRAM_TOKEN)
price_history = {}
last_alert_time = {}

# ================= ALERT FUNCTIONS =================
def send_alert(symbol, pct_change, price):
    """Send instant alert for a coin move."""
    now = time.time()
    if symbol in last_alert_time and now - last_alert_time[symbol] < ALERT_COOLDOWN:
        return  # avoid spamming
    last_alert_time[symbol] = now

    direction = "📈 UP" if pct_change > 0 else "📉 DOWN"
    msg = (
        f"{direction} {symbol}\n"
        f"Change: {pct_change:.2f}%\n"
        f"Current Price: {price}"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg)
    print(f"Instant Alert: {msg}")

def send_summary():
    """Send periodic summary every 60 seconds."""
    while True:
        now = time.time()
        summary_list = []

        for symbol, prices in price_history.items():
            past_prices = [(t, p) for t, p in prices if 59 <= now - t <= 61]
            if not past_prices:
                continue
            past_price = past_prices[0][1]
            current_price = prices[-1][1]
            pct_change = (current_price / past_price - 1) * 100

            if 1.0 <= abs(pct_change) <= 1.5:
                direction = "📈" if pct_change > 0 else "📉"
                summary_list.append(f"{direction} {symbol} {pct_change:.2f}% (Price: {current_price})")

        if summary_list:
            bot.send_message(
                chat_id=CHAT_ID,
                text="⏱ 1-Min Summary — Coins with 1–1.5% change:\n" + "\n".join(summary_list)
            )
            print("Summary sent.")

        time.sleep(60)

# ================= WEBSOCKET FUNCTIONS =================
def on_message(ws, message):
    data = json.loads(message)

    if 'd' in data and isinstance(data['d'], dict) and 'symbol' in data['d']:
        symbol = data['d']['symbol']
        price = float(data['d']['lastPrice'])
        now = time.time()

        if symbol not in price_history:
            price_history[symbol] = []
        price_history[symbol].append((now, price))
        price_history[symbol] = [(t, p) for t, p in price_history[symbol] if now - t <= 120]

        past_prices = [(t, p) for t, p in price_history[symbol] if 59 <= now - t <= 61]
        if past_prices:
            past_price = past_prices[0][1]
            pct_change = (price / past_price - 1) * 100
            if 1.0 <= abs(pct_change) <= 1.5:
                send_alert(symbol, pct_change, price)

def on_open(ws):
    sub_msg = {"method": "sub.ticker", "params": {"symbols": []}, "id": 1}
    ws.send(json.dumps(sub_msg))
    print("✅ Subscribed to MEXC Futures tickers.")

def start_ws():
    ws = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message)
    ws.run_forever()

# ================= MAIN =================
if __name__ == "__main__":
    threading.Thread(target=start_ws).start()
    threading.Thread(target=send_summary).start()
