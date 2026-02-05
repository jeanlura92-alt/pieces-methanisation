"""
Application configuration
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "listing-photos")

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_LISTING_PRICE_ID = os.getenv("STRIPE_LISTING_PRICE_ID", "")

# Application Configuration
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
LISTING_PRICE_AMOUNT = int(os.getenv("LISTING_PRICE_AMOUNT", "4900"))  # 49.00 EUR in cents

# Categories for listings
CATEGORIES = [
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
]

# Conditions for equipment
CONDITIONS = [
    "Neuf",
    "Comme neuf",
    "Très bon état",
    "Bon état",
    "Révisé",
    "Reconditionné",
]

# Listing types
LISTING_TYPES = [
    {"value": "equipment", "label": "Équipement complet"},
    {"value": "part", "label": "Pièce détachée"},
]
