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
    expires_at TIMESTAMP WITH TIME ZONE,
    
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
    
    -- Contact
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
```

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

### inquiries
```sql
CREATE TABLE inquiries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    
    -- Inquiry details
    buyer_name VARCHAR(255) NOT NULL,
    buyer_email VARCHAR(255) NOT NULL,
    buyer_phone VARCHAR(50),
    message TEXT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'new', -- 'new', 'read', 'replied', 'closed'
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_inquiries_listing_id ON inquiries(listing_id);
CREATE INDEX idx_inquiries_status ON inquiries(status);
```

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

## Setup Instructions

### 1. Create a Supabase Project
1. Go to https://supabase.com
2. Create a new project
3. Note your project URL and anon key

### 2. Run the SQL Schema
1. Go to the SQL Editor in your Supabase dashboard
2. Copy and paste the SQL statements above
3. Execute them to create the tables

### 3. Enable Row Level Security (Optional but Recommended)
Add RLS policies as needed for your security requirements.

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Supabase credentials.
