from fastapi import FastAPI, Request, HTTPException, Form, Cookie, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import stripe
import json
import logging

from . import db
from . import config
from . import storage

# Configure logging
logger = logging.getLogger(__name__)

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
    user = db.get_or_create_user("contact@pieces-methanisation.fr")
    
    listing_data = {
        "listing_type": listing_type,
        "category": category,
        "title": title,
        "contact_email": "contact@pieces-methanisation.fr",
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
    draft["photos"] = media  # Add photos list to draft
    
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
    photos: List[UploadFile] = File(...),
):
    """Save step 3 (upload photos) and redirect to step 4"""
    
    # Server-side validation: max 3 photos
    if len(photos) > config.MAX_PHOTOS_PER_LISTING:
        raise HTTPException(
            status_code=400, 
            detail=f"Vous ne pouvez télécharger que {config.MAX_PHOTOS_PER_LISTING} photos maximum."
        )
    
    # Server-side validation: at least 1 photo
    if len(photos) == 0:
        raise HTTPException(
            status_code=400,
            detail="Veuillez télécharger au moins une photo."
        )
    
    # Validate file types
    for photo in photos:
        if photo.content_type not in config.ALLOWED_PHOTO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non autorisé: {photo.content_type}. Utilisez JPG, PNG, WEBP ou GIF."
            )
    
    # Check if Supabase is configured
    if not db.supabase:
        # Mock mode - skip upload but continue
        logger.warning("Supabase not configured - skipping photo upload in mock mode")
        return RedirectResponse(url=f"/deposer/step4?listing_id={listing_id}", status_code=303)
    
    try:
        # Delete existing media for this listing
        existing_media = db.get_listing_media(listing_id)
        for media_item in existing_media:
            # Extract storage path and delete from storage
            storage_path = storage.extract_storage_path(media_item["url"], config.SUPABASE_STORAGE_BUCKET)
            if storage_path:
                storage.delete_file(db.supabase, config.SUPABASE_STORAGE_BUCKET, storage_path)
        
        # Delete media records from database
        db.delete_listing_media(listing_id)
        
        # Upload new photos
        uploaded_count = 0
        for idx, photo in enumerate(photos):
            # Read file content
            file_content = await photo.read()
            
            # Generate unique filename
            filename = storage.generate_filename(listing_id, photo.filename)
            
            # Get content type
            content_type = storage.get_content_type(photo.filename)
            
            # Upload to Supabase Storage
            public_url = storage.upload_file(
                db.supabase,
                config.SUPABASE_STORAGE_BUCKET,
                filename,
                file_content,
                content_type
            )
            
            if public_url:
                # Save media record to database
                db.add_media(
                    listing_id=listing_id,
                    media_type="photo",
                    url=public_url,
                    filename=photo.filename,
                    display_order=idx
                )
                uploaded_count += 1
            else:
                # Upload failed
                logger.error(f"Failed to upload photo: {photo.filename}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Échec du téléchargement de la photo: {photo.filename}"
                )
        
        logger.info(f"Successfully uploaded {uploaded_count} photos for listing {listing_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du téléchargement des photos. Veuillez réessayer."
        )
    
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
    price_amount: Optional[str] = Form(None),
    location: str = Form(...),
):
    """Save step 4 and redirect to step 5"""
    if price_type == "quote":
        price_amount_cents = None
        price_display = "Sur devis"
    else:
        try:
            # Convert string to float, then to cents
            amount = float(price_amount) if price_amount else 0
            price_amount_cents = int(amount * 100)
            price_display = format_price_display(price_amount_cents)
        except (ValueError, TypeError):
            price_amount_cents = None
            price_display = "Prix non défini"
    
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
    consent_public_contact: Optional[str] = Form(None),
):
    """Save step 5 and create Stripe checkout session"""
    
    # GDPR consent validation
    if not consent_public_contact:
        draft = db.get_listing(listing_id)
        return templates.TemplateResponse(
            "wizard_step5.html",
            {
                "request": request,
                "current_step": 5,
                "draft": draft,
                "listing_price": config.LISTING_PRICE_AMOUNT / 100,
                "error": "Vous devez accepter que vos coordonnées soient publiquement visibles."
            }
        )
    
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
        logger.error(f"Stripe error: {e}")
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


# ==================== Contact ====================

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse(
        "contact.html",
        {"request": request},
    )


@app.post("/contact")
async def contact_post(
    request: Request,
    name: str = Form(...),
    company: Optional[str] = Form(None),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    subject: str = Form(...),
    reference: Optional[str] = Form(None),
    message: str = Form(...),
):
    """Handle contact form submission"""
    try:
        # Logger les données (note: sanitize sensitive data in production logs)
        logger.info(f"Contact form submitted by {name} ({email})")
        logger.info(f"Subject: {subject}, Message: {message[:100]}...")
        
        # Sauvegarder dans la base de données (optionnel mais recommandé)
        # TODO: Ajouter une table 'contact_messages' si nécessaire
        
        # Envoyer un email via SMTP
        from . import email as email_module
        email_sent = await email_module.send_contact_email(name, email, phone, company, subject, reference, message)
        
        if not email_sent:
            logger.warning(f"Email not sent for contact form from {email} - SMTP may not be configured")
        
        # Rediriger avec message de succès
        return templates.TemplateResponse(
            "contact.html",
            {
                "request": request,
                "success": True,
                "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais."
            },
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        return templates.TemplateResponse(
            "contact.html",
            {
                "request": request,
                "error": True,
                "message": "Une erreur est survenue lors de l'envoi. Veuillez réessayer."
            },
        )


# ==================== Legal Pages (LCEN, RGPD, ePrivacy, Code de Commerce) ====================

@app.get("/mentions-legales", response_class=HTMLResponse)
async def mentions_legales(request: Request):
    """Legal notices page (LCEN compliance)"""
    return templates.TemplateResponse("mentions_legales.html", {"request": request})


@app.get("/cgv", response_class=HTMLResponse)
async def cgv(request: Request):
    """Terms and conditions page (Code de Commerce B2B compliance)"""
    return templates.TemplateResponse("cgv.html", {"request": request})


@app.get("/politique-confidentialite", response_class=HTMLResponse)
async def politique_confidentialite(request: Request):
    """Privacy policy page (RGPD/GDPR compliance)"""
    return templates.TemplateResponse("politique_confidentialite.html", {"request": request})


@app.get("/cookies", response_class=HTMLResponse)
async def cookies(request: Request):
    """Cookie management page (ePrivacy compliance)"""
    return templates.TemplateResponse("cookies.html", {"request": request})


# ==================== DSA Compliance Pages ====================

@app.get("/comment-ca-marche", response_class=HTMLResponse)
async def comment_ca_marche(request: Request):
    """Transparency page - How the platform works (DSA compliance)"""
    return templates.TemplateResponse("comment_ca_marche.html", {"request": request})


@app.get("/signaler", response_class=HTMLResponse)
async def signaler(request: Request):
    """Report form page (DSA compliance)"""
    return templates.TemplateResponse("signaler.html", {"request": request})


@app.post("/signaler")
async def signaler_post(
    request: Request,
    listing_url: str = Form(...),
    reason: str = Form(...),
    description: str = Form(...),
    reporter_email: str = Form(None),
):
    """Handle report submission (DSA compliance)"""
    # Extract listing_id from URL if possible
    listing_id = None
    if "/annonces/" in listing_url:
        try:
            listing_id = listing_url.split("/annonces/")[1].split("?")[0].split("#")[0]
        except:
            pass
    
    # Save report to database
    report = db.create_report(
        listing_url=listing_url,
        reason=reason,
        description=description,
        reporter_email=reporter_email,
        listing_id=listing_id
    )
    
    # In production, send email notification to admin
    if report:
        logger.info(f"New report created: {report.get('id')} for listing: {listing_url}")
    
    return templates.TemplateResponse(
        "signaler_success.html",
        {"request": request}
    )


# ==================== Admin Dashboard (Reports Management) ====================

@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(request: Request, status: Optional[str] = None):
    """Admin dashboard for managing reports (DSA compliance)"""
    # TODO: Add authentication for admin access
    # For now, this is accessible without auth (should be protected in production)
    
    reports = db.get_reports(status=status, limit=100)
    
    # Get counts by status
    all_reports = db.get_reports(limit=1000)
    status_counts = {
        "new": len([r for r in all_reports if r["status"] == "new"]),
        "reviewed": len([r for r in all_reports if r["status"] == "reviewed"]),
        "resolved": len([r for r in all_reports if r["status"] == "resolved"]),
        "total": len(all_reports)
    }
    
    return templates.TemplateResponse(
        "admin_reports.html",
        {
            "request": request,
            "reports": reports,
            "status_counts": status_counts,
            "current_filter": status
        }
    )


@app.post("/admin/reports/{report_id}/update-status")
async def update_report_status(report_id: str, status: str = Form(...)):
    """Update report status"""
    # TODO: Add authentication for admin access
    
    db.update_report_status(report_id, status)
    return RedirectResponse(url="/admin/reports", status_code=303)
