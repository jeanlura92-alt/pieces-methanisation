# Database Schema

This document describes the database schema for the Pièces Méthanisation Pro marketplace.

## Tables

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### listings
```sql
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- 'draft', 'published', 'expired', 'sold'
    published_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,  -- Auto-set to published_at + 30 days when published
    
    -- Basic Info
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    listing_type VARCHAR(50) NOT NULL DEFAULT 'equipment', -- 'equipment' or 'part'
    
    -- Technical Details (stored as JSONB for flexibility)
    technical_specs JSONB,
    
    -- Pricing & Location
    price_amount INTEGER, -- in cents, null for "sur devis"
    price_display VARCHAR(100), -- "12 900 €" or "Sur devis"
    location VARCHAR(255) NOT NULL,
    
    -- Description
    summary VARCHAR(255),
    description TEXT,
    
    -- Additional info
    condition VARCHAR(50),
    year VARCHAR(10),
    manufacturer VARCHAR(255),
    
    -- Contact (displayed publicly on listing detail page)
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50) NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_category ON listings(category);
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_published_at ON listings(published_at);
CREATE INDEX idx_listings_expires_at ON listings(expires_at);
```

**Important Notes:**
- Listings automatically expire 30 days after publication (`expires_at = published_at + 30 days`)
- Expired listings are filtered out from public views
- Contact information (email and phone) is displayed publicly on listing detail pages

### media
```sql
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    media_type VARCHAR(20) NOT NULL, -- 'photo', 'pdf'
    url TEXT NOT NULL,
    filename VARCHAR(255),
    file_size INTEGER,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_media_listing_id ON media(listing_id);
```

**Important Note:** Each listing can have a maximum of **1 photo**.

### payments
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Stripe info
    stripe_checkout_session_id VARCHAR(255) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),
    
    -- Payment details
    amount INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payments_listing_id ON payments(listing_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_stripe_checkout_session_id ON payments(stripe_checkout_session_id);
CREATE INDEX idx_payments_status ON payments(status);
```

## Removed Tables (V2 Simplification)

The following table has been removed to simplify the application:

### ~~inquiries~~ (REMOVED)
- **Reason:** Direct contact information is now displayed on listing pages
- **Alternative:** Buyers contact sellers directly via email or phone
- **See:** `MIGRATION_V2.sql` for migration script

## Automatic Expiration

Listings automatically expire after 30 days. To mark expired listings:

### Option 1: Manual Execution
```python
from app.db import expire_old_listings
expired_count = expire_old_listings()
```

### Option 2: PostgreSQL Function (via pg_cron)
```sql
-- Create the function
CREATE OR REPLACE FUNCTION expire_old_listings()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE listings
    SET status = 'expired', updated_at = NOW()
    WHERE status = 'published' AND expires_at < NOW();
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule it to run daily at 2 AM (Supabase with pg_cron)
SELECT cron.schedule('expire-listings-daily', '0 2 * * *', 'SELECT expire_old_listings();');
```

### Option 3: System Cron Job
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/app && python -c "from app.db import expire_old_listings; expire_old_listings()"
```

## Setup Instructions

### 1. Create a Supabase Project
1. Go to https://supabase.com
2. Create a new project
3. Note your project URL and anon key

### 2. Run the SQL Schema
1. Go to the SQL Editor in your Supabase dashboard
2. Copy and paste the SQL statements above
3. Execute them to create the tables

### 3. Migrate from V1 (if applicable)
1. If you have an existing database, run `MIGRATION_V2.sql` to:
   - Drop the `inquiries` table
   - Update existing listings with `expires_at` dates
   - Create the `expire_old_listings()` function

### 4. Enable Row Level Security (Optional but Recommended)
Add RLS policies as needed for your security requirements.

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Supabase credentials.

### 6. Set Up Automatic Expiration (Recommended)
Choose one of the options above to automatically expire old listings.

