import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# Initialize bot application
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# In-memory jar (will be replaced with persistent storage)
jar = {"Oumaima": 0, "Maarten": 0}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ik vloekte", callback_data="swear_Oumaima")],
        [InlineKeyboardButton("Maarten vloekte", callback_data="swear_Maarten")],
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Betaald – reset", callback_data="reset")]
    ]
    await update.message.reply_text("💰 Scheldpotje", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data.startswith("swear_"):
        p = q.data.split("_")[1]
        jar[p] = jar.get(p, 0) + 1
        await q.edit_message_text(f"{p} vloekte. Totaal: {jar[p]}")

    elif q.data == "status":
        totaal = sum(jar.values()) * 0.20
        msg = "\n".join([f"{k}: {v}" for k, v in jar.items()])
        await q.edit_message_text(f"{msg}\nTotaal: €{totaal:.2f}")

    elif q.data == "reset":
        for key in jar:
            jar[key] = 0
        await q.edit_message_text("Potje gereset.")

async def process_update(data):
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    await application.initialize()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    await application.shutdown()

@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            asyncio.run(process_update(data))
            return jsonify({"ok": True})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"ok": False, "error": str(e)}), 500
    else:
        return "Bot is running!", 200