 # bot/cache.py
# Petit cache en mémoire pour stocker les URLs de téléchargement
# Telegram limite les callback_data à 64 caractères → on contourne

_links = {}
_counter = 0


def store(url, fmt, title):
    """Stocke un lien et retourne un ID court (ex: 'a1', 'a2'...)."""
    global _counter
    _counter += 1
    key = f"a{_counter}"
    _links[key] = {"url": url, "fmt": fmt, "title": title}
    return key


def get(key):
    """Récupère un lien stocké par son ID."""
    return _links.get(key)
