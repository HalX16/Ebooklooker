# apis/gutenberg.py
import requests

BASE_URL = "https://gutendex.com/books"


def search_books(query, limit=5):
    params = {"search": query}
    try:
        r = requests.get(BASE_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[Gutenberg] indisponible, on passe. ({type(e).__name__})")
        return []

    results = []
    for book in data.get("results", [])[:limit]:
        authors = [a.get("name", "Auteur inconnu") for a in book.get("authors", [])]
        languages = book.get("languages", [])
        formats = book.get("formats", {})

        epub_url = formats.get("application/epub+zip")
        pdf_url = None
        for key, url in formats.items():
            if "pdf" in key.lower():
                pdf_url = url
                break

        results.append({
            "id": book.get("id"),
            "title": book.get("title", "Titre inconnu"),
            "authors": authors or ["Auteur inconnu"],
            "languages": languages,
            "epub_url": epub_url,
            "pdf_url": pdf_url,
            "source": "Gutenberg",
        })
    return results