import os
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CallbackQueryHandler, CommandHandler

# Initialize bot
bot = Bot(os.environ["BOT_TOKEN"])

# In-memory jar (will be replaced with persistent storage)
jar = {"Oumaima": 0, "Maarten": 0}

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Ik vloekte", callback_data="swear_Oumaima")],
        [InlineKeyboardButton("Maarten vloekte", callback_data="swear_Maarten")],
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Betaald – reset", callback_data="reset")]
    ]
    update.message.reply_text("💰 Scheldpotje", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update, context):
    q = update.callback_query
    q.answer()

    if q.data.startswith("swear_"):
        p = q.data.split("_")[1]
        jar[p] = jar.get(p, 0) + 1
        q.edit_message_text(f"{p} vloekte. Totaal: {jar[p]}")

    elif q.data == "status":
        totaal = sum(jar.values()) * 0.20
        msg = "\n".join([f"{k}: {v}" for k, v in jar.items()])
        q.edit_message_text(f"{msg}\nTotaal: €{totaal:.2f}")

    elif q.data == "reset":
        for key in jar:
            jar[key] = 0
        q.edit_message_text("Potje gereset.")

# Initialize dispatcher
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Process update
            update = Update.de_json(data, bot)
            dispatcher.process_update(update)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')