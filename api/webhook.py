import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CallbackQueryHandler, CommandHandler

app = Flask(__name__)

# Initialize bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(BOT_TOKEN)

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

@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return jsonify({"ok": True})
    else:
        return "Bot is running!", 200

# For Vercel
def handler(event, context):
    with app.request_context(event):
        return app.full_dispatch_request()