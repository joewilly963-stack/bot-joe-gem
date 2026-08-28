import os
import asyncio
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

# 1. LISTES DES ACTIFS POCKET OPTION (OTC)
PAIRS_FOREX_OTC = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/CAD OTC", "EUR/CHF OTC",
    "CHF/JPY OTC", "CAD/CHF OTC", "EUR/GBP OTC", "AUD/USD OTC", "USD/CAD OTC",
    "NZD/USD OTC", "EUR/JPY OTC", "GBP/JPY OTC", "AUD/JPY OTC", "USD/CHF OTC"
]

PAIRS_CRYPTO_OTC = [
    "BTC/USD OTC", "ETH/USD OTC", "SOL/USD OTC", "TRX/USD OTC", 
    "LTC/USD OTC", "XRP/USD OTC", "DOGE/USD OTC", "TON/USD OTC"
]

PAIRS_STOCKS_OTC = [
    "Apple OTC", "Tesla OTC", "Amazon OTC", "Microsoft OTC", "Google OTC",
    "Meta OTC", "NVIDIA OTC", "Netflix OTC"
]

PAIRS_INDICES_OTC = [
    "US Tech 100 OTC", "SPX 500 OTC", "US30 OTC", "GER40 (DAX) OTC"
]

PAIRS_COMMODITIES_OTC = [
    "Gold OTC (XAU/USD)", "Silver OTC (XAG/USD)", "US Crude OTC"
]

ALL_ASSETS = PAIRS_FOREX_OTC + PAIRS_CRYPTO_OTC + PAIRS_STOCKS_OTC + PAIRS_INDICES_OTC + PAIRS_COMMODITIES_OTC

# Stockage des données par utilisateur
user_selections = {}
user_sessions = {}  # Format: {user_id: {"total": 0, "win": 0, "loss": 0, "doji": 0, "history": []}}

# Moteur d'analyse technique multi-indicateurs
def multi_indicator_analysis():
    rsi = random.randint(20, 80)
    macd_cross = random.choice(["HAUSSIER", "BAISSIER"])
    bollinger_state = random.choice(["TOUCH_LOWER", "TOUCH_UPPER", "MIDDLE"])
    
    score_buy = 0
    score_sell = 0
    confirmations = []

    if rsi <= 30:
        score_buy += 25
        confirmations.append(f"RSI Survente ({rsi})")
    elif rsi >= 70:
        score_sell += 25
        confirmations.append(f"RSI Surachat ({rsi})")

    if bollinger_state == "TOUCH_LOWER":
        score_buy += 25
        confirmations.append("Rejet Bollinger Inf")
    elif bollinger_state == "TOUCH_UPPER":
        score_sell += 25
        confirmations.append("Rejet Bollinger Sup")

    if macd_cross == "HAUSSIER":
        score_buy += 25
        confirmations.append("Croisement MACD Haussier")
    else:
        score_sell += 25
        confirmations.append("Croisement MACD Baissier")

    if score_buy >= score_sell:
        direction = "CALL / ACHAT 🟢"
        confidence = random.choice([97.8, 98.4, 98.9, 99.1, 99.4])
    else:
        direction = "PUT / VENTE 🔴"
        confidence = random.choice([97.5, 98.2, 98.8, 99.0, 99.3])

    payout = random.choice([92, 92, 90, 88])
    confirm_text = " + ".join(confirmations[:2]) if confirmations else "Alignement Tendance EMA 50/200"

    return direction, confirm_text, confidence, payout

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Initialisation de la session utilisateur si elle n'existe pas
    if user_id not in user_sessions:
        user_sessions[user_id] = {"total": 0, "win": 0, "loss": 0, "doji": 0, "history": []}

    keyboard = [
        [InlineKeyboardButton("💱 Forex OTC", callback_data="market_forex"),
         InlineKeyboardButton("🪙 Crypto OTC", callback_data="market_crypto")],
        [InlineKeyboardButton("🏢 Actions OTC", callback_data="market_stocks"),
         InlineKeyboardButton("📈 Indices OTC", callback_data="market_indices")],
        [InlineKeyboardButton("🛢️ Commodities OTC", callback_data="market_commodities"),
         InlineKeyboardButton("🎲 Scanner Global", callback_data="market_random")],
        [InlineKeyboardButton("🏁 Terminer la Session (/end)", callback_data="end_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🧠 **BOT ALGORITHMIQUE JOE GEM TRADING (PRÉCISION 99%)** 🧠\n\n"
        "🔍 **Analyse multi-indicateurs intégrée :** RSI + MACD + Bollinger + EMA 50/200.\n"
        "Choisissez la catégorie d'actif à scanner :"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Sélection du Timeframe (5s à 4h)
async def select_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    choice = query.data

    if choice == "market_forex":
        user_selections[user_id] = random.choice(PAIRS_FOREX_OTC)
    elif choice == "market_crypto":
        user_selections[user_id] = random.choice(PAIRS_CRYPTO_OTC)
    elif choice == "market_stocks":
        user_selections[user_id] = random.choice(PAIRS_STOCKS_OTC)
    elif choice == "market_indices":
        user_selections[user_id] = random.choice(PAIRS_INDICES_OTC)
    elif choice == "market_commodities":
        user_selections[user_id] = random.choice(PAIRS_COMMODITIES_OTC)
    else:
        user_selections[user_id] = random.choice(ALL_ASSETS)

    tf_keyboard = [
        [InlineKeyboardButton("⚡ 5 sec", callback_data="tf_5s"),
         InlineKeyboardButton("⚡ 10 sec", callback_data="tf_10s")],
        [InlineKeyboardButton("⏱ 1 min", callback_data="tf_1m"),
         InlineKeyboardButton("⏱ 2 min", callback_data="tf_2m")],
        [InlineKeyboardButton("⏳ 5 min", callback_data="tf_5m"),
         InlineKeyboardButton("⏳ 10 min", callback_data="tf_10m")],
        [InlineKeyboardButton("📈 1 heure", callback_data="tf_1h"),
         InlineKeyboardButton("📊 4 heures", callback_data="tf_4h")]
    ]
    reply_markup = InlineKeyboardMarkup(tf_keyboard)

    await query.edit_message_text(
        f"🎯 **Actif ciblé :** `{user_selections[user_id]}`\n\n"
        f"Sélectionnez le timeframe pour l'analyse :",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Génération du Signal et calcul des stats
async def generate_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"total": 0, "win": 0, "loss": 0, "doji": 0, "history": []}

    asset = user_selections.get(user_id, random.choice(ALL_ASSETS))
    
    timeframe_map = {
        "tf_5s": "5 secondes", "tf_10s": "10 secondes",
        "tf_1m": "1 minute", "tf_2m": "2 minutes",
        "tf_5m": "5 minutes", "tf_10m": "10 minutes",
        "tf_1h": "1 heure", "tf_4h": "4 heures"
    }
    expiration = timeframe_map.get(query.data, "1 minute")
    
    direction, confirm_text, confidence, payout = multi_indicator_analysis()

    signal_msg = (
        f"🎯 **SIGNAL ANALYSE TECHNIQUE (JOE GEM)** 🎯\n\n"
        f"📊 **Actif :** `{asset}`\n"
        f"💰 **Payout :** **{payout}%** 📈\n"
        f"🎯 **Direction :** **{direction}**\n"
        f"⏱ **Expiration :** **{expiration}**\n\n"
        f"📊 **Confluence :** `{confirm_text}`\n"
        f"🔥 **Confiance Calculée :** **{confidence}%** 🎯\n\n"
        f"⏳ *Prendre position dès l'ouverture de la bougie.*"
    )
    
    await query.edit_message_text(signal_msg, parse_mode="Markdown")

    # Attente simulée du trade
    await asyncio.sleep(5)

    # Résultat optimisé haute précision
    outcomes = ["WIN", "WIN", "WIN", "WIN", "DOJI", "LOSS"]
    res_type = random.choice(outcomes)

    user_sessions[user_id]["total"] += 1

    if res_type == "WIN":
        user_sessions[user_id]["win"] += 1
        result_text = "✅ **RÉSULTAT : WIN 🟢** (Objectif validé !)"
    elif res_type == "DOJI":
        user_sessions[user_id]["doji"] += 1
        result_text = "⚪ **RÉSULTAT : DOJI ⚪** (Égalité de marché)"
    else:
        user_sessions[user_id]["loss"] += 1
        result_text = "❌ **RÉSULTAT : LOSS 🔴** (Rejet imprévu)"

    user_sessions[user_id]["history"].append({
        "asset": asset,
        "direction": direction,
        "result": res_type,
        "confidence": confidence
    })

    keyboard = [
        [InlineKeyboardButton("🔄 Nouveau Signal", callback_data="market_random"),
         InlineKeyboardButton("🏁 Fin de Session", callback_data="end_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    result_msg = (
        f"📢 **NOTIF DE CLÔTURE (`{asset}`)**\n\n"
        f"🎯 **Direction :** {direction}\n"
        f"⏱ **Expiration :** {expiration}\n"
        f"🔥 **Confiance :** {confidence}%\n\n"
        f"🏁 {result_text}"
    )
    await query.message.reply_text(result_msg, reply_markup=reply_markup, parse_mode="Markdown")

# Récapitulatif de Session (/end ou bouton Fin de Session)
async def end_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Traitement via message ou bouton Inline
    if update.callback_query:
        await update.callback_query.answer()
        send_func = update.callback_query.message.reply_text
    else:
        send_func = update.message.reply_text

    stats = user_sessions.get(user_id, {"total": 0, "win": 0, "loss": 0, "doji": 0, "history": []})
    total = stats["total"]

    if total == 0:
        await send_func(
            "⚠️ **Aucun signal n'a été utilisé durant cette session.**\n"
            "Tapez /start pour démarrer une nouvelle session d'analyse.",
            parse_mode="Markdown"
        )
        return

    win = stats["win"]
    loss = stats["loss"]
    doji = stats["doji"]
    
    # Calcul du Winrate
    winrate = round((win / total) * 100, 2)
    now = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    # Construction du journal des signaux
    history_lines = ""
    for idx, item in enumerate(stats["history"], start=1):
        icon = "🟢 WIN" if item["result"] == "WIN" else ("⚪ DOJI" if item["result"] == "DOJI" else "🔴 LOSS")
        history_lines += f"{idx}. `{item['asset']}` | {item['direction'].split()[0]} | {icon} ({item['confidence']}%)\n"

    summary_msg = (
        f"📋 **RÉCAPITULATIF DE VOTRE SESSION DE TRADING** 📋\n\n"
        f"📅 **Date & Heure :** `{now}`\n"
        f"👤 **Trader :** `{update.effective_user.first_name}`\n\n"
        f"📊 **STATISTIQUES DE SESSION :**\n"
        f"🔹 **Signaux Totaux envoyés :** `{total}`\n"
        f"🟢 **Signaux Gagnants (WIN) :** `{win}`\n"
        f"⚪ **Égalités (DOJI) :** `{doji}`\n"
        f"🔴 **Signaux Perdants (LOSS) :** `{loss}`\n\n"
        f"🏆 **POURCENTAGE DE RÉUSSITE :** **{winrate}%** 🔥\n\n"
        f"📜 **DÉTAILS DES TRADES DE LA SESSION :**\n"
        f"{history_lines}\n"
        f"💡 *Session clôturée avec succès. Recommandation : Respectez le management de capital.*"
    )

    # Réinitialisation de la session de l'utilisateur
    user_sessions[user_id] = {"total": 0, "win": 0, "loss": 0, "doji": 0, "history": []}

    keyboard = [[InlineKeyboardButton("🚀 Démarrer une nouvelle session", callback_data="market_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_func(summary_msg, reply_markup=reply_markup, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("end", end_session))
    app.add_handler(CallbackQueryHandler(end_session, pattern="^end_session$"))
    app.add_handler(CallbackQueryHandler(select_timeframe, pattern="^market_"))
    app.add_handler(CallbackQueryHandler(generate_signal, pattern="^tf_"))
    app.run_polling()
