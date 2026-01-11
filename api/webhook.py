import os
import json
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

def handler(event, context):
    try:
        # Parse the incoming request
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            data = event
        
        # Process the Telegram update
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }