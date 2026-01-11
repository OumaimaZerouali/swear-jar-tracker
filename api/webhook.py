import json
import os
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"
JAR_FILE = "/tmp/jar.json"
PRICE = 0.20

def load():
    if os.path.exists(JAR_FILE):
        return json.load(open(JAR_FILE))
    return {"Oumaima": 0, "Maarten": 0}

def save(data):
    json.dump(data, open(JAR_FILE, "w"))

def keyboard():
    return {
        "inline_keyboard": [
            [{"text": "Oumaima heeft gescholden", "callback_data": "Oumaima"}],
            [{"text": "Maarten heeft gescholden", "callback_data": "Maarten"}],
            [{"text": "Bekijk potje", "callback_data": "status"}],
            [{"text": "Betaald / Reset potje", "callback_data": "reset"}],
        ]
    }

def send(chat_id, text, reply_markup=None):
    requests.post(API + "/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    })

def edit(chat_id, msg_id, text):
    requests.post(API + "/editMessageText", json={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "reply_markup": keyboard()
    })

def handler(req):
    update = json.loads(req.get_data())
    jar = load()

    if "message" in update:
        chat = update["message"]["chat"]["id"]
        send(chat, "Welkom bij het scheldpotje", keyboard())
        return "ok"

    cb = update["callback_query"]
    chat = cb["message"]["chat"]["id"]
    msg = cb["message"]["message_id"]
    data = cb["data"]

    if data in jar:
        jar[data] += 1
    elif data == "reset":
        jar = {"Oumaima": 0, "Maarten": 0}

    save(jar)
    total = sum(jar.values()) * PRICE

    text = f"Oumaima: {jar['Oumaima']}\nMaarten: {jar['Maarten']}\n\n💰 €{total:.2f}"
    edit(chat, msg, text)
    return "ok"
