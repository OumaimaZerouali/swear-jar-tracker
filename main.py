from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, CallbackContext
import json
import os

PRIJS_PER_SCHELDWOORD = 0.20
BESTAND = "jar.json"

# Laden of initialiseren
if os.path.exists(BESTAND):
    with open(BESTAND) as f:
        jar = json.load(f)
else:
    jar = {"Oumaima": 0, "Maarten": 0}

def save_jar():
    with open(BESTAND, "w") as f:
        json.dump(jar, f)

def toetsenbord():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Oumaima heeft gescholden", callback_data='swear_Oumaima')],
        [InlineKeyboardButton("Maarten heeft gescholden", callback_data='swear_Maarten')],
        [InlineKeyboardButton("Bekijk potje", callback_data='status')],
        [InlineKeyboardButton("Betaald / Reset potje", callback_data='reset')]
    ])

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welkom bij het Scheldpotje.\nDruk op een knop:",
        reply_markup=toetsenbord()
    )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith("swear_"):
        persoon = query.data.replace("swear_", "")
        jar[persoon] += 1
        save_jar()

    elif query.data == "reset":
        jar["Oumaima"] = 0
        jar["Maarten"] = 0
        save_jar()

    totaal = sum(jar.values()) * PRIJS_PER_SCHELDWOORD

    tekst = (
        f"Oumaima: {jar['Oumaima']} keer\n"
        f"Maarten: {jar['Maarten']} keer\n\n"
        f"💰 Totaal in potje: €{totaal:.2f}"
    )

    if query.data == "reset":
        tekst += "\n\nPotje is gereset omdat er betaald is."

    query.edit_message_text(tekst, reply_markup=toetsenbord())

def main():
    updater = Updater("BOT_TOKEN")
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()