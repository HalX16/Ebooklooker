# apis/open_library.py
import requests

BASE_URL = "https://openlibrary.org/search.json"


def search_books(query, limit=5):
    params = {
        "q": query,
        "limit": limit,
        "fields": "title,author_name,first_publish_year,language,key,edition_key,ia,ebook_access",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[Open Library] indisponible. ({type(e).__name__})")
        return []

    results = []
    for doc in data.get("docs", []):
        results.append({
            "title": doc.get("title", "Titre inconnu"),
            "authors": doc.get("author_name", ["Auteur inconnu"]),
            "year": doc.get("first_publish_year", "—"),
            "languages": doc.get("language", []),
            "key": doc.get("key", ""),
            "ia": doc.get("ia", []),
            "ebook_access": doc.get("ebook_access", ""),
        })
    return results