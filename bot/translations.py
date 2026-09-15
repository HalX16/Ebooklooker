# bot/translations.py
import json
import os

_translations = {}
LANGUAGES = ["fr", "en", "ar"]


def load_translations():
    global _translations
    _translations = {}
    for lang in LANGUAGES:
        path = os.path.join("locales", f"{lang}.json")
        with open(path, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)


def t(lang, key, **kwargs):
    if lang not in _translations:
        lang = "fr"
    text = _translations[lang].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text 
