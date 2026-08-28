import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import pandas as pd
import pandas_ta as ta

# Récupération du TOKEN sécurisé depuis Render
TOKEN = os.getenv("TOKEN")

user_sessions = {}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"pair": "EUR/USD OTC", "tf": "1m"}

    keyboard = [
        [InlineKeyboardButton("📊 Paire de devises", callback_data="menu_pair")],
        [InlineKeyboardButton("⏱️ Expiration", callback_data="menu_tf")],
        [InlineKeyboardButton("🚀 Lancer le Scan Joe Gem", callback_data="run_scan")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💎 **BOT VIP JOE GEM TRADING** 💎\n\n"
        "Configurez vos paramètres pour démarrer l'analyse automatique du marché.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "menu_pair":
        keyboard = [
            [InlineKeyboardButton("EUR/USD OTC", callback_data="pair_EUR/USD OTC"),
             InlineKeyboardButton("AUD/CAD OTC", callback_data="pair_AUD/CAD OTC")],
            [InlineKeyboardButton("EUR/CHF OTC", callback_data="pair_EUR/CHF OTC"),
             InlineKeyboardButton("GBP/USD OTC", callback_data="pair_GBP/USD OTC")]
        ]
        await query.edit_message_text("Sélectionnez la paire à analyser :", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("pair_"):
        pair = query.data.replace("pair_", "")
        user_sessions[user_id]["pair"] = pair
        await query.edit_message_text(f"✅ Paire sélectionnée : **{pair}**", 
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("⏱️ Expiration", callback_data="menu_tf")],
                                          [InlineKeyboardButton("🚀 Lancer le Scan", callback_data="run_scan")]
                                      ]), parse_mode="Markdown")

    elif query.data == "menu_tf":
        keyboard = [
            [InlineKeyboardButton("1 Minute (M1)", callback_data="tf_1m")],
            [InlineKeyboardButton("5 Minutes (M5)", callback_data="tf_5m")]
        ]
        await query.edit_message_text("Sélectionnez la durée d'expiration :", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("tf_"):
        tf = query.data.replace("tf_", "")
        user_sessions[user_id]["tf"] = tf
        await query.edit_message_text(f"✅ Expiration : **{tf}**", 
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🚀 Lancer le Scan", callback_data="run_scan")]
                                      ]), parse_mode="Markdown")

    elif query.data == "run_scan":
        session = user_sessions.get(user_id, {"pair": "EUR/USD OTC", "tf": "1m"})
        await query.edit_message_text(
            f"🔎 **SCAN JOE GEM EN COURS...**\n"
            f"• Paire : `{session['pair']}`\n"
            f"• Expiration : `{session['tf']}`\n\n"
            f"_Le bot analyse les graphiques. L'alerte sera envoyée ici dès confirmation des critères._",
            parse_mode="Markdown"
        )

def main():
    if not TOKEN:
        print("ERREUR: Le Token Telegram est manquant dans Render !")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Bot Joe Gem démarré avec succès !")
    app.run_polling()

if __name__ == "__main__":
    main()
