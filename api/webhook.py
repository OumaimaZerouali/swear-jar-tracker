import os
import asyncio
import json
import requests as req
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# Initialize bot application
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize Upstash Redis REST API
UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def redis_get(key):
    """Get value from Upstash Redis"""
    try:
        if not UPSTASH_URL or not UPSTASH_TOKEN:
            print("Upstash credentials not set")
            return None
        response = req.get(
            f"{UPSTASH_URL}/get/{key}",
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}
        )
        print(f"GET Response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            result = response.json().get("result")
            return result
        return None
    except Exception as e:
        print(f"Redis GET error: {e}")
        return None

def redis_set(key, value):
    """Set value in Upstash Redis"""
    try:
        if not UPSTASH_URL or not UPSTASH_TOKEN:
            print("Upstash credentials not set")
            return False
        # Upstash REST API expects the command as URL path
        response = req.post(
            f"{UPSTASH_URL}/set/{key}/{value}",
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}
        )
        print(f"SET Response: {response.status_code}, {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Redis SET error: {e}")
        return False

def get_jar():
    """Get jar data from Redis"""
    try:
        data = redis_get("swear_jar")
        if data:
            return json.loads(data)
        else:
            # Initialize if doesn't exist
            initial = {"Oumaima": 0, "Maarten": 0}
            redis_set("swear_jar", json.dumps(initial))
            return initial
    except:
        # Fallback to default if Redis fails
        return {"Oumaima": 0, "Maarten": 0}

def save_jar(jar):
    """Save jar data to Redis"""
    try:
        redis_set("swear_jar", json.dumps(jar))
    except Exception as e:
        print(f"Error saving to Redis: {e}")

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
    
    print("Button pressed:", q.data)
    jar = get_jar()
    print("Current jar:", jar)
    
    # Create keyboard for all responses
    keyboard = [
        [InlineKeyboardButton("Ik vloekte", callback_data="swear_Oumaima")],
        [InlineKeyboardButton("Maarten vloekte", callback_data="swear_Maarten")],
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Betaald – reset", callback_data="reset")]
    ]

    if q.data.startswith("swear_"):
        p = q.data.split("_")[1]
        jar[p] = jar.get(p, 0) + 1
        print(f"Incrementing {p} to {jar[p]}")
        save_jar(jar)
        print("After save, reading back:", get_jar())
        await q.edit_message_text(
            f"{p} vloekte. Totaal: {jar[p]}\n\n💰 Scheldpotje", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif q.data == "status":
        totaal = sum(jar.values()) * 0.20
        msg = "\n".join([f"{k}: {v}" for k, v in jar.items()])
        await q.edit_message_text(
            f"{msg}\nTotaal: €{totaal:.2f}\n\n💰 Scheldpotje",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif q.data == "reset":
        for key in jar:
            jar[key] = 0
        save_jar(jar)
        await q.edit_message_text(
            "Potje gereset.\n\n💰 Scheldpotje",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

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