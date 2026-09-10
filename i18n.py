import json
import logging
import os

SUPPORTED_LANGUAGES = ("pt_BR", "en")
DEFAULT_LANGUAGE = "pt_BR"

_LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
_cache = {}


def _load(lang_code):
    if lang_code in _cache:
        return _cache[lang_code]
    path = os.path.join(_LOCALES_DIR, f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load locale '{lang_code}' from {path}: {e}")
        data = {}
    _cache[lang_code] = data
    return data


def normalize_language(lang_code):
    """Maps loose user input ('pt', 'pt-br', 'português', 'inglês', 'en-us')
    to one of SUPPORTED_LANGUAGES, falling back to the default."""
    if not lang_code:
        return DEFAULT_LANGUAGE
    key = lang_code.strip().lower().replace('-', '_')
    aliases = {
        "pt": "pt_BR", "pt_br": "pt_BR", "ptbr": "pt_BR",
        "portugues": "pt_BR", "português": "pt_BR", "portuguese": "pt_BR",
        "en": "en", "en_us": "en", "english": "en", "ingles": "en", "inglês": "en",
    }
    return aliases.get(key, DEFAULT_LANGUAGE if key not in ("en",) else "en")


def t(key, lang=None, **kwargs):
    """Looks up `key` in the given language's locale file (falling back to
    DEFAULT_LANGUAGE, then to the key itself if truly missing), formatting
    any {placeholders} with kwargs."""
    lang = lang or DEFAULT_LANGUAGE
    data = _load(lang)
    text = data.get(key)
    if text is None and lang != DEFAULT_LANGUAGE:
        text = _load(DEFAULT_LANGUAGE).get(key)
    if text is None:
        logging.warning(f"Missing i18n key '{key}' for language '{lang}'.")
        text = key
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception as e:
        logging.warning(f"Error formatting i18n key '{key}': {e}")
        return text
