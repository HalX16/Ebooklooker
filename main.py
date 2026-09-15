# main.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot import database as db
from bot import translations
from bot import handlers
from bot import download
from bot import donations
from bot import share

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def open_don_callback(update: Update, context):
    """Redirige le bouton 'Faire un don' vers le menu de dons."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"
    await query.message.reply_text(
        translations.t(lang, "don_message"),
        parse_mode="Markdown",
        reply_markup=donations.donation_keyboard(lang),
    )


async def open_share_callback(update: Update, context):
    """Redirige le bouton 'Partager' vers la commande share."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"
    me = await context.bot.get_me()
    share_url = f"https://t.me/{me.username}"
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [[
        InlineKeyboardButton(
            translations.t(lang, "share_button"),
            url=f"https://t.me/share/url?url={share_url}&text={translations.t(lang, 'share_text')}"
        )
    ]]
    await query.message.reply_text(
        translations.t(lang, "share_message", bot=me.username),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
    )


def main():
    if not TOKEN:
        print("❌ ERREUR : Token Telegram manquant dans le fichier .env")
        return

    print("📦 Initialisation de la base de données...")
    db.init_db()

    print("🌍 Chargement des traductions...")
    translations.load_translations()

    print("🚀 Démarrage de Ebooklooker...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.help_command))
    app.add_handler(CommandHandler("lang", handlers.lang_command))
    app.add_handler(CommandHandler("search", handlers.search_command))
    app.add_handler(CommandHandler("don", donations.don_command))
    app.add_handler(CommandHandler("share", share.share_command))

    # Callbacks
    app.add_handler(CallbackQueryHandler(handlers.language_callback, pattern=r"^lang_"))
    app.add_handler(CallbackQueryHandler(download.download_callback, pattern=r"^dl\|"))
    app.add_handler(CallbackQueryHandler(donations.donation_callback, pattern=r"^don_\d+$"))
    app.add_handler(CallbackQueryHandler(open_don_callback, pattern=r"^open_don$"))
    app.add_handler(CallbackQueryHandler(open_share_callback, pattern=r"^open_share$"))

    # Paiements Stars
    app.add_handler(PreCheckoutQueryHandler(donations.precheckout_callback))
    app.add_handler(MessageHandler(
        filters.SUCCESSFUL_PAYMENT,
        donations.successful_payment_callback
    ))

    # Message texte libre → recherche
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_message))

    print("✅ Bot en ligne ! Appuie sur Ctrl+C pour l'arrêter.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()