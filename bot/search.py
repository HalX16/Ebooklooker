# bot/search.py
from apis import open_library, gutenberg, internet_archive
from bot.translations import t
from bot import cache
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _clean(text):
    if not isinstance(text, str):
        return str(text)
    for ch in ["*", "_", "`", "[", "]", "(", ")", "~", ">", "#", "+", "=", "|", "{", "}"]:
        text = text.replace(ch, "")
    return text.strip()


def search_all(query, limit=5):
    results = []

    for b in internet_archive.search_books(query, limit=limit):
        b["title"] = _clean(b.get("title", ""))
        results.append(b)

    for b in gutenberg.search_books(query, limit=limit):
        b["source"] = "Gutenberg"
        b["title"] = _clean(b.get("title", ""))
        results.append(b)

    for b in open_library.search_books(query, limit=limit):
        results.append({
            "title": _clean(b["title"]),
            "authors": b["authors"],
            "languages": b["languages"],
            "epub_url": None,
            "pdf_url": None,
            "source": "OpenLibrary",
            "url": f"https://openlibrary.org{b['key']}",
            "year": b["year"],
        })

    seen = set()
    unique = []
    for r in results:
        key = r["title"].lower().strip()
        if key in seen or not key:
            continue
        seen.add(key)
        unique.append(r)

    return unique[:limit]


def format_results(lang, query, results):
    """Retourne (texte, clavier) — clavier peut être None si pas de résultats."""
    if not results:
        return t(lang, "no_results", query=query), None

    lines = [t(lang, "results_header", query=query), ""]
    keyboard = []

    for i, book in enumerate(results, 1):
        authors = _clean(", ".join(book["authors"][:3]))
        lines.append(f"📖 {i}. {book['title']}")
        lines.append(f"👤 {authors}")
        if book.get("year") and book["year"] != "—":
            lines.append(f"📅 {book['year']}")
        lines.append(f"📥 {book['source']}")
        lines.append("")

        row = []
        title_short = _clean(book["title"])[:40]

        if book.get("epub_url"):
            key = cache.store(book["epub_url"], "epub", title_short)
            row.append(InlineKeyboardButton(f"📥 EPUB #{i}", callback_data=f"dl|{key}"))
        if book.get("pdf_url"):
            key = cache.store(book["pdf_url"], "pdf", title_short)
            row.append(InlineKeyboardButton(f"📥 PDF #{i}", callback_data=f"dl|{key}"))
        if not row and book.get("url"):
            row.append(InlineKeyboardButton(f"🔗 Voir #{i}", url=book["url"]))
        if row:
            keyboard.append(row)

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:3990] + "\n\n…(tronqué)"

    # 🔒 On retourne TOUJOURS un tuple (texte, clavier_ou_None)
    if keyboard:
        return text, InlineKeyboardMarkup(keyboard)
    return text, None


def search(query, limit=5):
    return search_all(query, limit=limit)