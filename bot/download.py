# bot/download.py
import os
import requests
from telegram import Update
from telegram.ext import ContextTypes
from bot import database as db
from bot import cache
from bot.translations import t

TEMP_DIR = "data/tmp"


def ensure_temp_dir():
    os.makedirs(TEMP_DIR, exist_ok=True)


async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    callback_data : 'dl|<id_cache>'
    Ex: 'dl|a17'
    """
    query = update.callback_query
    await query.answer("📥 Téléchargement en cours...")

    user = query.from_user
    lang = db.get_user_language(user.id) or "fr"

    # On récupère les infos depuis le cache
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

    # Vérifie que le fichier n'est pas vide / pas du HTML d'erreur
    if not os.path.exists(filepath) or os.path.getsize(filepath) < 500:
        os.remove(filepath) if os.path.exists(filepath) else None
        await query.message.reply_text(t(lang, "download_error"))
        return

    try:
        await query.message.reply_document(
            document=open(filepath, "rb"),
            filename=filename,
            caption=f"📚 {title}"
        )
    except Exception as e:
        print(f"Erreur envoi: {e}")
        await query.message.reply_text(t(lang, "download_error"))
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass