# bot/download.py
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import database as db
from bot import cache
from bot.translations import t

TEMP_DIR = "data/tmp"


def ensure_temp_dir():
    os.makedirs(TEMP_DIR, exist_ok=True)


def post_download_keyboard(lang):
    """Boutons proposés après un téléchargement réussi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_new_search"), callback_data="new_search")],
        [InlineKeyboardButton(t(lang, "btn_donate"), callback_data="open_don")],
    ])


async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("📥 Téléchargement en cours...")

    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"

    try:
        _, key = query.data.split("|", 1)
    except ValueError:
        await query.message.reply_text("❌ Lien invalide.")
        return

    info = cache.get(key)
    if not info:
        await query.message.reply_text(t(lang, "download_error"))
        return

    url = info["url"]
    fmt = info["fmt"]
    title = info["title"]

    ensure_temp_dir()
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:40].strip()
    filename = f"{user.id}_{safe_title}.{fmt}"

    try:
        r = requests.get(url, timeout=60, stream=True)
        r.raise_for_status()
    except Exception as e:
        print(f"Erreur téléchargement: {e}")
        await query.message.reply_text(t(lang, "download_error"))
        return

    filepath = os.path.join(TEMP_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Erreur écriture: {e}")
        await query.message.reply_text(t(lang, "download_error"))
        return

    if not os.path.exists(filepath) or os.path.getsize(filepath) < 500:
        try:
            os.remove(filepath)
        except Exception:
            pass
        await query.message.reply_text(t(lang, "download_error"))
        return

    try:
        await query.message.reply_document(
            document=open(filepath, "rb"),
            filename=filename,
            caption=f"📚 {title}"
        )
        # Message de suivi avec boutons
        await query.message.reply_text(
            t(lang, "download_done"),
            parse_mode="Markdown",
            reply_markup=post_download_keyboard(lang),
        )
    except Exception as e:
        print(f"Erreur envoi: {e}")
        await query.message.reply_text(t(lang, "download_error"))
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass