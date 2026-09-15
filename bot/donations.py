# bot/donations.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes

from bot import database as db
from bot.translations import t

# Les 4 paliers de dons
DONATION_TIERS = [
    {"emoji": "☕", "key": "don_tier_1", "amount": 5},
    {"emoji": "📚", "key": "don_tier_2", "amount": 20},
    {"emoji": "🎁", "key": "don_tier_3", "amount": 50},
    {"emoji": "⭐", "key": "don_tier_4", "amount": 100},
]


def donation_keyboard(lang):
    """Construit le clavier avec les 4 paliers de dons."""
    keyboard = []
    row = []
    for tier in DONATION_TIERS:
        label = f"{tier['emoji']} {tier['amount']} ⭐"
        row.append(InlineKeyboardButton(label, callback_data=f"don_{tier['amount']}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


async def don_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /don — affiche le menu des dons."""
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"

    text = t(lang, "don_message")
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=donation_keyboard(lang),
        disable_web_page_preview=True,
    )


async def donation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Appelé quand l'utilisateur clique sur un palier de don."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"

    try:
        amount = int(query.data.split("_")[1])
    except (ValueError, IndexError):
        await query.message.reply_text("❌ Erreur.")
        return

    # Envoi de la facture Stars
    try:
        # On construit manuellement les arguments pour éviter le provider_token vide
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=f"Soutenir Ebooklooker — {amount} ⭐",
            description=t(lang, "don_invoice_desc", amount=amount),
            payload=f"donation_{amount}",
            currency="XTR",  # XTR = Telegram Stars
            prices=[LabeledPrice(label=f"Don {amount} Stars", amount=amount)],
            # On force la suppression du provider_token en passant par api_kwargs
            api_kwargs={"provider_token": None}
        )
    except Exception as e:
        print(f"[Donations] Erreur envoi facture : {e}")
        await query.message.reply_text(t(lang, "don_error"))


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram demande si on peut procéder au paiement → on dit oui."""
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Paiement confirmé avec succès."""
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"
    payment = update.message.successful_payment

    amount = payment.total_amount
    db.save_donation(user.id, amount)

    await update.message.reply_text(
        t(lang, "don_thanks", amount=amount),
        parse_mode="Markdown"
    )