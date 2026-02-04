"""
Database access layer for Supabase
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Warning: Supabase credentials not configured. Using mock mode.")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(supabase_url, supabase_key)


# ==================== Users ====================

def get_or_create_user(email: str, phone: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get existing user or create new one"""
    if not supabase:
        return {"id": "mock-user-id", "email": email}
    
    # Try to get existing user
    result = supabase.table("users").select("*").eq("email", email).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    
    # Create new user
    user_data = {"email": email}
    if phone:
        user_data["phone"] = phone
    if name:
        user_data["name"] = name
    
    result = supabase.table("users").insert(user_data).execute()
    return result.data[0] if result.data else None


# ==================== Listings ====================

def create_listing(user_id: str, listing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a new listing (draft by default)"""
    if not supabase:
        return {"id": "mock-listing-id", **listing_data}
    
    data = {
        "user_id": user_id,
        "status": "draft",
        **listing_data
    }
    
    result = supabase.table("listings").insert(data).execute()
    return result.data[0] if result.data else None


def update_listing(listing_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing listing"""
    if not supabase:
        return {"id": listing_id, **updates}
    
    updates["updated_at"] = datetime.utcnow().isoformat()
    result = supabase.table("listings").update(updates).eq("id", listing_id).execute()
    return result.data[0] if result.data else None


def get_listing(listing_id: str) -> Optional[Dict[str, Any]]:
    """Get a single listing by ID"""
    if not supabase:
        return None
    
    result = supabase.table("listings").select("*").eq("id", listing_id).execute()
    return result.data[0] if result.data and len(result.data) > 0 else None


def get_published_listings(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get all published listings"""
    if not supabase:
        return []
    
    result = (
        supabase.table("listings")
        .select("*")
        .eq("status", "published")
        .order("published_at", desc=True)
        .limit(limit)
        .offset(offset)
        .execute()
    )
    return result.data if result.data else []


def get_user_listings(user_id: str) -> List[Dict[str, Any]]:
    """Get all listings for a user"""
    if not supabase:
        return []
    
    result = (
        supabase.table("listings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data if result.data else []


def publish_listing(listing_id: str) -> Optional[Dict[str, Any]]:
    """Publish a listing (set status to published and set published_at)"""
    if not supabase:
        return {"id": listing_id, "status": "published"}
    
    updates = {
        "status": "published",
        "published_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("listings").update(updates).eq("id", listing_id).execute()
    return result.data[0] if result.data else None


# ==================== Media ====================

def add_media(listing_id: str, media_type: str, url: str, filename: Optional[str] = None, display_order: int = 0) -> Optional[Dict[str, Any]]:
    """Add media to a listing"""
    if not supabase:
        return {"id": "mock-media-id", "listing_id": listing_id, "url": url}
    
    data = {
        "listing_id": listing_id,
        "media_type": media_type,
        "url": url,
        "filename": filename,
        "display_order": display_order
    }
    
    result = supabase.table("media").insert(data).execute()
    return result.data[0] if result.data else None


def get_listing_media(listing_id: str) -> List[Dict[str, Any]]:
    """Get all media for a listing"""
    if not supabase:
        return []
    
    result = (
        supabase.table("media")
        .select("*")
        .eq("listing_id", listing_id)
        .order("display_order")
        .execute()
    )
    return result.data if result.data else []


# ==================== Inquiries ====================

def create_inquiry(listing_id: str, inquiry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a new inquiry for a listing"""
    if not supabase:
        return {"id": "mock-inquiry-id", "listing_id": listing_id, **inquiry_data}
    
    data = {
        "listing_id": listing_id,
        "status": "new",
        **inquiry_data
    }
    
    result = supabase.table("inquiries").insert(data).execute()
    return result.data[0] if result.data else None


def get_listing_inquiries(listing_id: str) -> List[Dict[str, Any]]:
    """Get all inquiries for a listing"""
    if not supabase:
        return []
    
    result = (
        supabase.table("inquiries")
        .select("*")
        .eq("listing_id", listing_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data if result.data else []


def count_listing_inquiries(listing_id: str) -> int:
    """Count inquiries for a listing"""
    if not supabase:
        return 0
    
    result = supabase.table("inquiries").select("id", count="exact").eq("listing_id", listing_id).execute()
    return result.count if result.count is not None else 0


# ==================== Payments ====================

def create_payment(listing_id: str, user_id: str, amount: int, stripe_session_id: str) -> Optional[Dict[str, Any]]:
    """Create a payment record"""
    if not supabase:
        return {"id": "mock-payment-id", "listing_id": listing_id}
    
    data = {
        "listing_id": listing_id,
        "user_id": user_id,
        "amount": amount,
        "currency": "EUR",
        "status": "pending",
        "stripe_checkout_session_id": stripe_session_id
    }
    
    result = supabase.table("payments").insert(data).execute()
    return result.data[0] if result.data else None


def update_payment_status(stripe_session_id: str, status: str, payment_intent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Update payment status"""
    if not supabase:
        return {"stripe_checkout_session_id": stripe_session_id, "status": status}
    
    updates = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if payment_intent_id:
        updates["stripe_payment_intent_id"] = payment_intent_id
    
    result = (
        supabase.table("payments")
        .update(updates)
        .eq("stripe_checkout_session_id", stripe_session_id)
        .execute()
    )
    return result.data[0] if result.data else None


def get_payment_by_session(stripe_session_id: str) -> Optional[Dict[str, Any]]:
    """Get payment by Stripe session ID"""
    if not supabase:
        return None
    
    result = (
        supabase.table("payments")
        .select("*")
        .eq("stripe_checkout_session_id", stripe_session_id)
        .execute()
    )
    return result.data[0] if result.data and len(result.data) > 0 else None
