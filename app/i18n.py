"""
Internationalization (i18n) utilities for the application.
Provides translation functions and locale management.
"""
import os
from pathlib import Path
from typing import Optional
import gettext
from fastapi import Request
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

# Supported locales
SUPPORTED_LOCALES = ["fr", "en"]
DEFAULT_LOCALE = "fr"

# Path to translations
LOCALES_DIR = Path(__file__).parent.parent / "locales"

# Cache for translation objects
_translations = {}


def get_hreflang_url(url: str, lang: Optional[str] = None) -> str:
    """
    Construct URL with proper language parameter.
    
    Args:
        url: The current URL
        lang: Language code to add (None for default/fr)
    
    Returns:
        URL with proper lang parameter
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove existing lang parameter
    query_params.pop('lang', None)
    
    # Add new lang parameter if not default
    if lang and lang != DEFAULT_LOCALE:
        query_params['lang'] = [lang]
    
    # Reconstruct query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))


def get_translation(locale: str):
    """Get gettext translation object for the given locale."""
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE
    
    if locale not in _translations:
        try:
            translation = gettext.translation(
                'messages',
                localedir=str(LOCALES_DIR),
                languages=[locale],
                fallback=True
            )
            _translations[locale] = translation
        except Exception as e:
            # Fallback to NullTranslations if translation files don't exist yet
            _translations[locale] = gettext.NullTranslations()
    
    return _translations[locale]


def get_locale_from_request(request: Request) -> str:
    """
    Determine the user's preferred locale from:
    1. Query parameter (?lang=en)
    2. Cookie (locale)
    3. Accept-Language header
    4. Default locale
    """
    # Check query parameter
    lang = request.query_params.get("lang")
    if lang in SUPPORTED_LOCALES:
        return lang
    
    # Check cookie
    locale_cookie = request.cookies.get("locale")
    if locale_cookie in SUPPORTED_LOCALES:
        return locale_cookie
    
    # Check Accept-Language header
    accept_language = request.headers.get("Accept-Language", "")
    for lang in SUPPORTED_LOCALES:
        if lang in accept_language.lower():
            return lang
    
    return DEFAULT_LOCALE


def get_translator(locale: str):
    """Get translation function for the given locale."""
    translation = get_translation(locale)
    return translation.gettext


def format_currency(amount_cents: Optional[int], locale: str = "fr") -> str:
    """Format currency amount according to locale."""
    if amount_cents is None:
        return get_translator(locale)("On quote")
    
    amount = amount_cents / 100
    if locale == "en":
        # English format: €49,000.00
        # First format with thousands separator and 2 decimals
        formatted = f"{amount:,.2f}"
        # In English: thousands=comma, decimal=period (already correct)
        return f"€{formatted}"
    else:
        # French format: 49 000,00 €
        # Format as integer part and decimal part separately
        int_part = int(amount)
        dec_part = int(round((amount - int_part) * 100))
        # French uses space for thousands, comma for decimal
        int_formatted = f"{int_part:,}".replace(",", " ")
        return f"{int_formatted},{dec_part:02d} €"


def format_date(date_str: str, locale: str = "fr") -> str:
    """Format date string according to locale."""
    # This is a simple implementation. For production, use babel.dates
    # TODO: Implement proper date formatting with babel
    return date_str


def get_localized_config(locale: str) -> dict:
    """Get localized configuration data (categories, conditions, etc.)."""
    _ = get_translator(locale)
    
    categories = {
        "fr": [
            "Agitation",
            "Pompage",
            "Épuration",
            "Sécurité",
            "Thermique",
            "Automatisme",
            "Compression",
            "Stockage",
            "Séparation",
            "Cogénération",
            "Analyse",
            "Prétraitement",
            "Instrumentation",
        ],
        "en": [
            "Agitation",
            "Pumping",
            "Purification",
            "Safety",
            "Thermal",
            "Automation",
            "Compression",
            "Storage",
            "Separation",
            "Cogeneration",
            "Analysis",
            "Pretreatment",
            "Instrumentation",
        ]
    }
    
    conditions = {
        "fr": [
            "Neuf",
            "Comme neuf",
            "Très bon état",
            "Bon état",
            "Révisé",
            "Reconditionné",
        ],
        "en": [
            "New",
            "Like new",
            "Very good condition",
            "Good condition",
            "Refurbished",
            "Reconditioned",
        ]
    }
    
    listing_types = {
        "fr": [
            {"value": "equipment", "label": "Équipement complet"},
            {"value": "part", "label": "Pièce détachée"},
        ],
        "en": [
            {"value": "equipment", "label": "Complete equipment"},
            {"value": "part", "label": "Spare part"},
        ]
    }
    
    return {
        "categories": categories.get(locale, categories["fr"]),
        "conditions": conditions.get(locale, conditions["fr"]),
        "listing_types": listing_types.get(locale, listing_types["fr"]),
    }
