import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CallbackQueryHandler, CommandHandler
from telegram import Bot

bot = Bot(os.environ["BOT_TOKEN"])

# Load jar
JAR_FILE = "/tmp/jar.json"

if os.path.exists(JAR_FILE):
    with open(JAR_FILE) as f:
        jar = json.load(f)
else:
    jar = {"oumi": 0, "maarten": 0}

def save():
    with open(JAR_FILE, "w") as f:
        json.dump(jar, f)

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Ik vloekte", callback_data="swear_oumi")],
        [InlineKeyboardButton("Maarten vloekte", callback_data="swear_maarten")],
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Betaald – reset", callback_data="reset")]
    ]
    update.message.reply_text("💰 Scheldpotje", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update, context):
    q = update.callback_query
    q.answer()

    if q.data.startswith("swear_"):
        p = q.data.split("_")[1]
        jar[p] += 1
        save()
        q.edit_message_text(f"{p.capitalize()} vloekte. Totaal: {jar[p]}")

    elif q.data == "status":
        totaal = sum(jar.values()) * 0.20
        msg = "\n".join([f"{k}: {v}" for k,v in jar.items()])
        q.edit_message_text(f"{msg}\nTotaal: €{totaal:.2f}")

    elif q.data == "reset":
        jar["oumi"] = 0
        jar["maarten"] = 0
        save()
        q.edit_message_text("Potje gereset.")

dispatcher = Dispatcher(bot, None, workers=1, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button))

def handler(request):
    update = Update.de_json(request.json, bot)
    dispatcher.process_update(update)
    return ("ok", 200)
