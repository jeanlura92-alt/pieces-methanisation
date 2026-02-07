"""
Database access layer for Supabase
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

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
    """Get all published listings that have not expired"""
    if not supabase:
        return []
    
    result = (
        supabase.table("listings")
        .select("*")
        .eq("status", "published")
        .gte("expires_at", datetime.utcnow().isoformat())  # Include listings expiring at this exact moment
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
    """Publish a listing (set status to published, set published_at, and set expires_at to 30 days later)"""
    if not supabase:
        return {"id": listing_id, "status": "published"}
    
    from datetime import timedelta
    
    now = datetime.utcnow()
    expires_at = now + timedelta(days=30)
    
    updates = {
        "status": "published",
        "published_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "updated_at": now.isoformat()
    }
    
    result = supabase.table("listings").update(updates).eq("id", listing_id).execute()
    return result.data[0] if result.data else None


def expire_old_listings() -> int:
    """
    Mark listings as expired if they are published and past their expiration date.
    Returns the number of listings that were expired.
    
    This function should be called regularly via:
    - A cron job on your server
    - A scheduled task (e.g., GitHub Actions, Cloud Scheduler)
    - A Supabase Edge Function with pg_cron
    
    Example cron setup (runs daily at 2 AM):
    0 2 * * * cd /path/to/app && python -c "from app.db import expire_old_listings; expire_old_listings()"
    
    Example Supabase Edge Function with pg_cron:
    SELECT cron.schedule('expire-listings', '0 2 * * *', $$
      UPDATE listings 
      SET status = 'expired', updated_at = NOW()
      WHERE status = 'published' AND expires_at < NOW()
    $$);
    """
    if not supabase:
        logger.warning("Supabase not configured - cannot expire listings")
        return 0
    
    try:
        now = datetime.utcnow().isoformat()
        
        # Get count of listings to expire before updating
        count_result = (
            supabase.table("listings")
            .select("id", count="exact")
            .eq("status", "published")
            .lt("expires_at", now)
            .execute()
        )
        
        expired_count = count_result.count if count_result.count is not None else 0
        
        if expired_count == 0:
            logger.info("No listings to expire")
            return 0
        
        # Bulk update all expired listings in a single query
        # Note: Supabase Python client doesn't support bulk update without filtering,
        # so we update with the same filter conditions
        update_result = (
            supabase.table("listings")
            .update({
                "status": "expired",
                "updated_at": now
            })
            .eq("status", "published")
            .lt("expires_at", now)
            .execute()
        )
        
        logger.info(f"Expired {expired_count} listings")
        return expired_count
        
    except Exception as e:
        logger.error(f"Error expiring listings: {e}")
        return 0


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


def delete_listing_media(listing_id: str) -> bool:
    """Delete all media for a listing"""
    if not supabase:
        return True
    
    try:
        supabase.table("media").delete().eq("listing_id", listing_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting media: {e}")
        return False


def delete_media_by_id(media_id: str) -> bool:
    """Delete a specific media entry by ID"""
    if not supabase:
        return True
    
    try:
        supabase.table("media").delete().eq("id", media_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting media by ID: {e}")
        return False


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


# ==================== Reports (DSA Compliance) ====================

def create_report(listing_url: str, reason: str, description: str, reporter_email: Optional[str] = None, listing_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Create a new report for a listing (DSA compliance)"""
    if not supabase:
        return {"id": "mock-report-id", "listing_url": listing_url, "reason": reason, "status": "new"}
    
    data = {
        "listing_url": listing_url,
        "reason": reason,
        "description": description,
        "status": "new"
    }
    
    if reporter_email:
        data["reporter_email"] = reporter_email
    
    if listing_id:
        data["listing_id"] = listing_id
    
    result = supabase.table("reports").insert(data).execute()
    return result.data[0] if result.data else None


def get_reports(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get reports, optionally filtered by status"""
    if not supabase:
        return []
    
    query = supabase.table("reports").select("*").order("created_at", desc=True).limit(limit)
    
    if status:
        query = query.eq("status", status)
    
    result = query.execute()
    return result.data if result.data else []


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Get a single report by ID"""
    if not supabase:
        return None
    
    result = supabase.table("reports").select("*").eq("id", report_id).execute()
    return result.data[0] if result.data and len(result.data) > 0 else None


def update_report_status(report_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Update report status (new, reviewed, resolved)"""
    if not supabase:
        return {"id": report_id, "status": status}
    
    updates = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("reports").update(updates).eq("id", report_id).execute()
    return result.data[0] if result.data else None
