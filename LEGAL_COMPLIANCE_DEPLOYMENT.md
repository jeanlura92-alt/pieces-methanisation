# Legal Compliance Implementation - Deployment Guide

This document provides instructions for deploying the legal compliance features to production.

## Overview

This implementation adds comprehensive legal compliance for the B2B marketplace covering:
- ✅ LCEN (French digital economy law)
- ✅ Code de Commerce (B2B terms)
- ✅ RGPD/GDPR (data protection)
- ✅ ePrivacy (cookie management)
- ✅ DSA (Digital Services Act)

## Pre-Deployment Checklist

### 1. Update Placeholder Information

All legal pages contain placeholder values marked with `[BRACKETS]`. You **MUST** replace these with your actual company information:

**In `app/templates/mentions_legales.html`:**
- `[NOM DE LA SOCIÉTÉ]` - Your company legal name
- `[SARL / SAS / SA / Auto-entrepreneur / etc.]` - Your legal structure
- `[ADRESSE COMPLÈTE]` - Complete registered address
- `[XXX XXX XXX XXXXX]` - SIRET number
- `[XXX XXX XXX]` - SIREN number
- `[Ville d'immatriculation]` - RCS registration city
- `[FR XX XXXXXXXXX]` - VAT number
- `[MONTANT]` - Share capital amount
- `[+33 X XX XX XX XX]` - Phone number
- `[NOM DU DIRECTEUR DE PUBLICATION]` - Director name
- `[Gérant / Président / etc.]` - Director title

**In `app/templates/cgv.html`:**
- `[NOM DE LA SOCIÉTÉ]` - Your company name

**In `app/templates/politique_confidentialite.html`:**
- `[NOM DE LA SOCIÉTÉ]` - Your company name
- `[ADRESSE COMPLÈTE]` - Complete address

### 2. Database Migration

Run the SQL migration to create the reports table:

```bash
# In Supabase SQL Editor, execute:
cat MIGRATION_REPORTS.sql
```

Or manually create the table:

```sql
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE SET NULL,
    listing_url TEXT NOT NULL,
    reason TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter_email TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_listing_id ON reports(listing_id);
CREATE INDEX idx_reports_created_at ON reports(created_at);
```

### 3. Configure Email Addresses

Set up the following email addresses for legal compliance:

- `privacy@pieces-methanisation.fr` - For GDPR/RGPD requests
- `legal@pieces-methanisation.fr` - For legal inquiries
- `contact@pieces-methanisation.fr` - For general contact

These emails are referenced in:
- Privacy policy
- Legal notices
- Terms and conditions
- Contact page

### 4. Implement Admin Authentication (CRITICAL)

**⚠️ SECURITY WARNING:** The admin dashboard (`/admin/reports`) is currently accessible without authentication. This is a **critical security vulnerability** that MUST be fixed before production deployment.

**Recommended solutions:**

#### Option A: FastAPI Basic Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("ADMIN_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("ADMIN_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Add to admin routes:
@app.get("/admin/reports")
async def admin_reports(request: Request, username: str = Depends(verify_admin)):
    # ... existing code
```

#### Option B: JWT Authentication
```python
# Implement JWT-based authentication for admin users
# See: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
```

#### Option C: Supabase Auth
```python
# Use Supabase authentication with admin role
# See: https://supabase.com/docs/guides/auth
```

**Environment variables to add:**
```bash
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

### 5. Configure Email Notifications

Update the reporting system to send email notifications when reports are submitted:

```python
# In app/main.py, update signaler_post function:
@app.post("/signaler")
async def signaler_post(...):
    # ... existing code
    
    # Send email notification to admin
    # TODO: Implement email sending
    # Options:
    # - SendGrid: https://sendgrid.com/
    # - AWS SES: https://aws.amazon.com/ses/
    # - Mailgun: https://www.mailgun.com/
    
    return templates.TemplateResponse(...)
```

### 6. Test Cookie Consent Banner

1. Open the site in a new incognito window
2. Verify the cookie banner appears at the bottom
3. Test all three buttons:
   - "Accepter tout" - Should set consent and hide banner
   - "Refuser tout" - Should reject non-essential cookies
   - "Personnaliser" - Should open customization modal
4. Check localStorage for cookie consent value
5. Refresh page and verify banner doesn't reappear

### 7. Test All Legal Pages

Visit each page and verify:
- ✅ `/mentions-legales` - Legal notices loads correctly
- ✅ `/cgv` - Terms and conditions loads correctly
- ✅ `/politique-confidentialite` - Privacy policy loads correctly
- ✅ `/cookies` - Cookie management loads correctly
- ✅ `/comment-ca-marche` - Transparency page loads correctly
- ✅ `/signaler` - Report form loads correctly
- ✅ Footer links all work correctly

### 8. Test GDPR Consent Checkbox

1. Go to `/deposer/step1`
2. Complete steps 1-4
3. On step 5, verify the GDPR consent checkbox appears
4. Try submitting without checking - should show error
5. Check the box and submit - should proceed to payment

### 9. Test Reporting System

1. Go to `/signaler`
2. Fill out the form with test data
3. Submit and verify success page appears
4. Check database to ensure report was saved
5. Visit `/admin/reports` to see the report (after adding auth)

### 10. Mobile Responsiveness

Test all pages on:
- Mobile (< 768px)
- Tablet (768px - 1024px)
- Desktop (> 1024px)

Key areas to test:
- Cookie banner (should stack vertically on mobile)
- Legal page tables (should be responsive)
- Admin dashboard table (should adapt for mobile)
- Footer links (should wrap properly)

## Production Environment Variables

Add these to your production environment (Render.com):

```bash
# Existing
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret
APP_URL=https://pieces-methanisation.onrender.com

# New for legal compliance
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

## Post-Deployment Verification

1. **CNIL Compliance Check**
   - Cookie banner appears on first visit
   - Users can refuse non-essential cookies
   - Consent is stored and persists
   - Privacy policy is accessible

2. **RGPD Compliance Check**
   - Privacy policy is complete and accurate
   - User rights are clearly explained
   - GDPR consent checkbox works on wizard step 5
   - Contact form has RGPD option

3. **DSA Compliance Check**
   - Transparency page explains ranking algorithm
   - Reporting system is functional
   - Reports are stored in database
   - Admin can review and manage reports

4. **Legal Pages Accessibility**
   - All pages are linked in footer
   - All pages load without errors
   - Content is readable and properly formatted
   - Mobile responsive

## Maintenance

### Annual Review
Review and update legal pages annually or when:
- Company information changes (address, legal form, etc.)
- New data processing activities are added
- Regulations change
- New features are added that collect data

### Report Management
- Review new reports within 48-72 hours
- Update report status (new → reviewed → resolved)
- Take action on legitimate reports (remove listings, contact users)
- Keep records of actions taken

### Cookie Policy Updates
- Update cookie list if new cookies are added
- Ensure Stripe cookies are documented
- Add analytics cookies if implemented (with consent)

## Support

For questions about this implementation:
- Technical issues: Create a GitHub issue
- Legal questions: Consult with a French legal professional
- CNIL compliance: https://www.cnil.fr/

## Important Legal Disclaimers

⚠️ **This implementation provides templates and structure for legal compliance, but:**

1. You MUST customize all placeholder values with your actual information
2. You MUST review content with a legal professional familiar with French law
3. You MUST implement admin authentication before production
4. You MUST keep legal pages updated as your service evolves
5. You MUST designate a DPO (Data Protection Officer) if required by GDPR

**The developer is not responsible for legal compliance. This is a technical implementation that must be reviewed and validated by legal counsel.**

## References

- LCEN: Loi n° 2004-575 du 21 juin 2004
- RGPD: Règlement (UE) 2016/679
- ePrivacy: Directive 2002/58/CE
- Code de Commerce: Article L441-1
- DSA: Règlement (UE) 2022/2065
- CNIL: https://www.cnil.fr/
