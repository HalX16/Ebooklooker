# apis/internet_archive.py
import requests

SEARCH_URL = "https://archive.org/advancedsearch.php"


def search_books(query, limit=5):
    params = {
        "q": f"{query} AND mediatype:texts",
        "fl[]": ["identifier", "title", "creator", "year", "language"],
        "rows": limit,
        "page": 1,
        "output": "json",
    }
    try:
        r = requests.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[Internet Archive] indisponible. ({type(e).__name__})")
        return []

    results = []
    for doc in data.get("response", {}).get("docs", []):
        identifier = doc.get("identifier")
        if not identifier:
            continue

        title = doc.get("title", "Titre inconnu")
        if isinstance(title, list):
            title = title[0]

        creator = doc.get("creator", "Auteur inconnu")
        if isinstance(creator, list):
            creator = creator[0]

        epub_url = f"https://archive.org/download/{identifier}/{identifier}.epub"
        pdf_url = f"https://archive.org/download/{identifier}/{identifier}.pdf"

        lang = doc.get("language", "")
        if not isinstance(lang, list):
            lang = [lang] if lang else []

        results.append({
            "title": title,
            "authors": [creator],
            "languages": lang,
            "year": doc.get("year", "—"),
            "epub_url": epub_url,
            "pdf_url": pdf_url,
            "source": "Internet Archive",
            "url": f"https://archive.org/details/{identifier}",
        })
    return results