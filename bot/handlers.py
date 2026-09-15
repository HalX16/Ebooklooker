# bot/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot import database as db
from bot import search as search_module
from bot.translations import t


def language_keyboard():
    keyboard = [[
        InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
    ]]
    return InlineKeyboardMarkup(keyboard)


def actions_keyboard(lang):
    """Boutons Don + Partage, réutilisables."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "btn_donate"), callback_data="open_don"),
        InlineKeyboardButton(t(lang, "btn_share"), callback_data="open_share"),
    ]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.save_user(user.id, user.username, user.first_name)
    lang = db.get_user_language(user.id)

    if lang is None:
        await update.message.reply_text(
            "🌍 Choose your language / Choisis ta langue / اختر لغتك :",
            reply_markup=language_keyboard()
        )
    else:
        await update.message.reply_text(
            t(lang, "welcome", name=user.first_name),
            parse_mode="Markdown",
            reply_markup=actions_keyboard(lang)
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"
    await update.message.reply_text(
        t(lang, "help"),
        parse_mode="Markdown",
        reply_markup=actions_keyboard(lang)
    )


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Choose your language / Choisis ta langue / اختر لغتك :",
        reply_markup=language_keyboard()
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    user = query.from_user
    db.save_user(user.id, user.username, user.first_name, language=lang)
    await query.edit_message_text(
        t(lang, "language_set") + "\n\n" + t(lang, "welcome", name=user.first_name),
        parse_mode="Markdown",
        reply_markup=actions_keyboard(lang)
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        user = update.effective_user
        lang = db.get_user_language(user.id) or "fr"
        await update.message.reply_text(t(lang, "search_usage"))
        return
    query = " ".join(context.args)
    await _do_search(update, context, query)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return
    await _do_search(update, context, text)


async def _do_search(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"

    await update.message.reply_text(
        t(lang, "searching", query=query),
        parse_mode="Markdown"
    )

    results = search_module.search(query, limit=5)
    text, markup = search_module.format_results(lang, query, results)

    # On ajoute une ligne Don + Partage en bas des boutons de résultats
    extra = [
        [
            InlineKeyboardButton(t(lang, "btn_donate"), callback_data="open_don"),
            InlineKeyboardButton(t(lang, "btn_share"), callback_data="open_share"),
        ]
    ]
    if markup:
        for row in extra:
            markup.inline_keyboard.append(row)
    else:
        markup = InlineKeyboardMarkup(extra)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=markup
    )