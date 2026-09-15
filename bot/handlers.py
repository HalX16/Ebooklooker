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


def main_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_new_search"), callback_data="new_search")],
        [
            InlineKeyboardButton(t(lang, "btn_donate"), callback_data="open_don"),
            InlineKeyboardButton(t(lang, "btn_share"), callback_data="open_share"),
        ],
    ])


def close_keyboard(lang):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "btn_close"), callback_data="close_msg"),
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
            reply_markup=main_menu_keyboard(lang),
            disable_web_page_preview=True,
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id) or "fr"
    await update.message.reply_text(
        t(lang, "help"),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(lang),
        disable_web_page_preview=True,
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
        reply_markup=main_menu_keyboard(lang),
        disable_web_page_preview=True,
    )


async def new_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"
    await query.message.reply_text(
        t(lang, "new_search_prompt"),
        parse_mode="Markdown",
        reply_markup=close_keyboard(lang),
    )


async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        pass


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        user = update.effective_user
        lang = db.get_user_language(user.id) or "fr"
        await update.message.reply_text(
            t(lang, "search_usage"),
            parse_mode="Markdown",
            reply_markup=close_keyboard(lang),
        )
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

    # On reconstruit TOUJOURS un nouveau clavier à partir de zéro.
    # Comme ça on ne touche JAMAIS à markup.inline_keyboard
    new_keyboard = []

    # 1) Récupère les boutons existants si markup est bien un clavier
    if isinstance(markup, InlineKeyboardMarkup):
        for row in markup.inline_keyboard:
            new_keyboard.append(list(row))

    # 2) Ajoute les boutons du bas
    new_keyboard.append([
        InlineKeyboardButton(t(lang, "btn_new_search"), callback_data="new_search")
    ])
    new_keyboard.append([
        InlineKeyboardButton(t(lang, "btn_donate"), callback_data="open_don"),
        InlineKeyboardButton(t(lang, "btn_share"), callback_data="open_share"),
    ])

    final_markup = InlineKeyboardMarkup(new_keyboard)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=final_markup
    )