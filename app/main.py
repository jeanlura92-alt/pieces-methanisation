from fastapi import FastAPI, Request, HTTPException, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import stripe
import json

from . import db
from . import config

app = FastAPI(title="Pieces Methanisation Pro")

# Configure Stripe
if config.STRIPE_SECRET_KEY:
    stripe.api_key = config.STRIPE_SECRET_KEY

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ==================== Helper Functions ====================

def get_draft_from_cookie(draft_id: Optional[str]) -> Optional[dict]:
    """Get draft listing from database"""
    if not draft_id:
        return None
    return db.get_listing(draft_id)


def format_price_display(price_amount: Optional[int]) -> str:
    """Format price amount (in cents) to display string"""
    if price_amount is None:
        return "Sur devis"
    return f"{price_amount // 100:,} €".replace(",", " ")


# ==================== Home ====================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Home page with featured listings from database"""
    featured = db.get_published_listings(limit=6)
    
    # Add image URLs for listings that have media
    for listing in featured:
        media = db.get_listing_media(listing["id"])
        if media and len(media) > 0:
            listing["image"] = media[0]["url"]
        else:
            # Fallback to default image
            listing["image"] = "https://images.unsplash.com/photo-1581092918484-8313e1f7e8d6?w=1200&q=80"
    
    count = len(featured)  # In production, you'd query the count separately
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "featured": featured, "count": count},
    )


# ==================== Listings ====================

@app.get("/annonces", response_class=HTMLResponse)
def listings(request: Request):
    """List all published listings"""
    all_listings = db.get_published_listings(limit=100)
    
    # Add image URLs for listings
    for listing in all_listings:
        media = db.get_listing_media(listing["id"])
        if media and len(media) > 0:
            listing["image"] = media[0]["url"]
        else:
            listing["image"] = "https://images.unsplash.com/photo-1581092918484-8313e1f7e8d6?w=1200&q=80"
    
    return templates.TemplateResponse(
        "listing.html",
        {"request": request, "listings": all_listings},
    )


@app.get("/annonces/{listing_id}", response_class=HTMLResponse)
def listing_detail(request: Request, listing_id: str):
    """Listing detail page"""
    listing = db.get_listing(listing_id)
    if not listing or listing["status"] != "published":
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    
    # Get media
    media = db.get_listing_media(listing_id)
    if media and len(media) > 0:
        listing["image"] = media[0]["url"]
    else:
        listing["image"] = "https://images.unsplash.com/photo-1581092918484-8313e1f7e8d6?w=1200&q=80"
    
    # Get similar listings (same category)
    similar = db.get_published_listings(limit=100)
    similar = [l for l in similar if l["category"] == listing["category"] and l["id"] != listing_id][:3]
    
    # Add images to similar listings
    for sim in similar:
        sim_media = db.get_listing_media(sim["id"])
        if sim_media and len(sim_media) > 0:
            sim["image"] = sim_media[0]["url"]
        else:
            sim["image"] = "https://images.unsplash.com/photo-1581092918484-8313e1f7e8d6?w=1200&q=80"
    
    return templates.TemplateResponse(
        "detail.html",
        {"request": request, "listing": listing, "listings": similar},
    )


@app.post("/annonces/{listing_id}/inquiry")
async def submit_inquiry(
    request: Request,
    listing_id: str,
    buyer_name: str = Form(...),
    buyer_email: str = Form(...),
    buyer_phone: str = Form(""),
    message: str = Form(...),
):
    """Submit an inquiry for a listing"""
    listing = db.get_listing(listing_id)
    if not listing or listing["status"] != "published":
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    
    inquiry_data = {
        "buyer_name": buyer_name,
        "buyer_email": buyer_email,
        "buyer_phone": buyer_phone,
        "message": message,
    }
    
    db.create_inquiry(listing_id, inquiry_data)
    
    # Redirect back to listing with success message
    return RedirectResponse(
        url=f"/annonces/{listing_id}?inquiry=success",
        status_code=303
    )


# ==================== Wizard Flow ====================

@app.get("/deposer")
async def deposer_redirect():
    """Redirect to wizard step 1"""
    return RedirectResponse(url="/deposer/step1", status_code=302)


@app.get("/deposer/step1", response_class=HTMLResponse)
def wizard_step1(request: Request, listing_id: Optional[str] = None):
    """Wizard step 1: Type & Category"""
    draft = None
    if listing_id:
        draft = db.get_listing(listing_id)
    
    return templates.TemplateResponse(
        "wizard_step1.html",
        {
            "request": request,
            "current_step": 1,
            "draft": draft,
            "listing_types": config.LISTING_TYPES,
            "categories": config.CATEGORIES,
        },
    )


@app.post("/deposer/step1")
async def wizard_step1_post(
    request: Request,
    listing_type: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    draft_id: Optional[str] = Cookie(None),
):
    """Save step 1 and redirect to step 2"""
    # Get or create user (simplified - in production you'd have auth)
    user = db.get_or_create_user("anonymous@example.com")
    
    listing_data = {
        "listing_type": listing_type,
        "category": category,
        "title": title,
        "contact_email": "anonymous@example.com",
        "contact_phone": "+33000000000",
        "location": "Non défini",
    }
    
    if draft_id:
        # Update existing draft
        draft = db.update_listing(draft_id, listing_data)
        listing_id = draft_id
    else:
        # Create new draft
        draft = db.create_listing(user["id"], listing_data)
        listing_id = draft["id"]
    
    response = RedirectResponse(url=f"/deposer/step2?listing_id={listing_id}", status_code=303)
    response.set_cookie(key="draft_id", value=listing_id, max_age=86400)
    return response


@app.get("/deposer/step2", response_class=HTMLResponse)
def wizard_step2(request: Request, listing_id: str):
    """Wizard step 2: Technical Details"""
    draft = db.get_listing(listing_id)
    if not draft:
        return RedirectResponse(url="/deposer/step1", status_code=302)
    
    return templates.TemplateResponse(
        "wizard_step2.html",
        {
            "request": request,
            "current_step": 2,
            "draft": draft,
            "conditions": config.CONDITIONS,
        },
    )


@app.post("/deposer/step2")
async def wizard_step2_post(
    request: Request,
    listing_id: str = Form(...),
    condition: str = Form(...),
    year: str = Form(""),
    manufacturer: str = Form(""),
    summary: str = Form(...),
    description: str = Form(...),
):
    """Save step 2 and redirect to step 3"""
    updates = {
        "condition": condition,
        "year": year if year else None,
        "manufacturer": manufacturer if manufacturer else None,
        "summary": summary,
        "description": description,
    }
    
    db.update_listing(listing_id, updates)
    
    return RedirectResponse(url=f"/deposer/step3?listing_id={listing_id}", status_code=303)


@app.get("/deposer/step3", response_class=HTMLResponse)
def wizard_step3(request: Request, listing_id: str):
    """Wizard step 3: Media"""
    draft = db.get_listing(listing_id)
    if not draft:
        return RedirectResponse(url="/deposer/step1", status_code=302)
    
    # Get existing media
    media = db.get_listing_media(listing_id)
    if media and len(media) > 0:
        draft["image_url"] = media[0]["url"]
    
    return templates.TemplateResponse(
        "wizard_step3.html",
        {
            "request": request,
            "current_step": 3,
            "draft": draft,
        },
    )


@app.post("/deposer/step3")
async def wizard_step3_post(
    request: Request,
    listing_id: str = Form(...),
    image_url: str = Form(""),
):
    """Save step 3 and redirect to step 4"""
    # If image URL provided, save it as media
    if image_url:
        # Remove existing media first
        existing_media = db.get_listing_media(listing_id)
        # Note: In production, you'd implement delete_media function
        
        # Add new media
        db.add_media(listing_id, "photo", image_url, display_order=0)
    
    return RedirectResponse(url=f"/deposer/step4?listing_id={listing_id}", status_code=303)


@app.get("/deposer/step4", response_class=HTMLResponse)
def wizard_step4(request: Request, listing_id: str):
    """Wizard step 4: Price & Location"""
    draft = db.get_listing(listing_id)
    if not draft:
        return RedirectResponse(url="/deposer/step1", status_code=302)
    
    return templates.TemplateResponse(
        "wizard_step4.html",
        {
            "request": request,
            "current_step": 4,
            "draft": draft,
        },
    )


@app.post("/deposer/step4")
async def wizard_step4_post(
    request: Request,
    listing_id: str = Form(...),
    price_type: str = Form(...),
    price_amount: Optional[int] = Form(None),
    location: str = Form(...),
):
    """Save step 4 and redirect to step 5"""
    if price_type == "quote":
        price_amount_cents = None
        price_display = "Sur devis"
    else:
        price_amount_cents = price_amount * 100 if price_amount else None
        price_display = format_price_display(price_amount_cents)
    
    updates = {
        "price_amount": price_amount_cents,
        "price_display": price_display,
        "location": location,
    }
    
    db.update_listing(listing_id, updates)
    
    return RedirectResponse(url=f"/deposer/step5?listing_id={listing_id}", status_code=303)


@app.get("/deposer/step5", response_class=HTMLResponse)
def wizard_step5(request: Request, listing_id: str):
    """Wizard step 5: Contact & Recap"""
    draft = db.get_listing(listing_id)
    if not draft:
        return RedirectResponse(url="/deposer/step1", status_code=302)
    
    return templates.TemplateResponse(
        "wizard_step5.html",
        {
            "request": request,
            "current_step": 5,
            "draft": draft,
            "listing_price": config.LISTING_PRICE_AMOUNT / 100,
        },
    )


@app.post("/deposer/step5")
async def wizard_step5_post(
    request: Request,
    listing_id: str = Form(...),
    contact_email: str = Form(...),
    contact_phone: str = Form(...),
):
    """Save step 5 and create Stripe checkout session"""
    updates = {
        "contact_email": contact_email,
        "contact_phone": contact_phone,
    }
    
    draft = db.update_listing(listing_id, updates)
    
    # Update or create user with email
    user = db.get_or_create_user(contact_email, contact_phone)
    
    # Create Stripe Checkout Session
    if not config.STRIPE_SECRET_KEY:
        # Mock mode - just publish immediately
        db.publish_listing(listing_id)
        return RedirectResponse(url=f"/payment/success?session_id=mock&listing_id={listing_id}", status_code=303)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": "Publication d'annonce",
                        "description": draft["title"],
                    },
                    "unit_amount": config.LISTING_PRICE_AMOUNT,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{config.APP_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{config.APP_URL}/payment/cancel?listing_id={listing_id}",
            metadata={
                "listing_id": listing_id,
                "user_id": user["id"],
            }
        )
        
        # Create payment record
        db.create_payment(
            listing_id=listing_id,
            user_id=user["id"],
            amount=config.LISTING_PRICE_AMOUNT,
            stripe_session_id=checkout_session.id
        )
        
        return RedirectResponse(url=checkout_session.url, status_code=303)
    
    except Exception as e:
        print(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la session de paiement")


# ==================== Payment ====================

@app.get("/payment/success", response_class=HTMLResponse)
def payment_success(request: Request, session_id: str, listing_id: Optional[str] = None):
    """Payment success page"""
    # In mock mode, listing_id is passed directly
    if session_id == "mock" and listing_id:
        return templates.TemplateResponse(
            "payment_success.html",
            {"request": request, "listing_id": listing_id},
        )
    
    # Get payment and publish listing
    payment = db.get_payment_by_session(session_id)
    if payment:
        listing_id = payment["listing_id"]
        
        # Update payment status
        db.update_payment_status(session_id, "completed")
        
        # Publish listing
        db.publish_listing(listing_id)
    
    return templates.TemplateResponse(
        "payment_success.html",
        {"request": request, "listing_id": listing_id},
    )


@app.get("/payment/cancel", response_class=HTMLResponse)
def payment_cancel(request: Request, listing_id: str):
    """Payment cancelled page"""
    return templates.TemplateResponse(
        "payment_cancel.html",
        {"request": request, "listing_id": listing_id},
    )


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not config.STRIPE_WEBHOOK_SECRET:
        return {"status": "webhook disabled"}
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Get payment
        payment = db.get_payment_by_session(session["id"])
        if payment:
            # Update payment status
            db.update_payment_status(
                session["id"],
                "completed",
                session.get("payment_intent")
            )
            
            # Publish listing
            db.publish_listing(payment["listing_id"])
    
    return {"status": "success"}


# ==================== Dashboard ====================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user_email: Optional[str] = Cookie(None)):
    """Seller dashboard"""
    # In a real app, you'd get user from session/auth
    # For now, we'll get all listings (simplified)
    
    if not user_email:
        user_email = "anonymous@example.com"
    
    # Get user
    user = db.get_or_create_user(user_email)
    
    # Get user's listings
    user_listings = db.get_user_listings(user["id"])
    
    # Add inquiry counts
    for listing in user_listings:
        listing["inquiry_count"] = db.count_listing_inquiries(listing["id"])
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "listings": user_listings},
    )


# ==================== Contact ====================

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse(
        "contact.html",
        {"request": request},
    )
