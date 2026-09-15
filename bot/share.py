 # bot/share.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot import database as db
from bot.translations import t


async def share_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /share — propose de partager le bot."""
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"

    # Récupère le username du bot
    me = await context.bot.get_me()
    bot_username = me.username
    share_url = f"https://t.me/{bot_username}"

    # Message + bouton de partage
    keyboard = [[
        InlineKeyboardButton(
            t(lang, "share_button"),
            url=f"https://t.me/share/url?url={share_url}&text={t(lang, 'share_text')}"
        )
    ]]

    await update.message.reply_text(
        t(lang, "share_message", bot=bot_username),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
    )
