-- Migration script to add reports table for DSA compliance
-- This script adds the reports table to support the reporting system

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE SET NULL,
    listing_url TEXT NOT NULL,
    reason TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter_email TEXT,
    status TEXT NOT NULL DEFAULT 'new', -- 'new', 'reviewed', 'resolved'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_listing_id ON reports(listing_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);

-- Add comments for documentation
COMMENT ON TABLE reports IS 'User reports for listings (DSA compliance)';
COMMENT ON COLUMN reports.listing_id IS 'Reference to the reported listing (nullable if listing is deleted)';
COMMENT ON COLUMN reports.listing_url IS 'URL of the reported listing';
COMMENT ON COLUMN reports.reason IS 'Reason for the report (e.g., fraudulent, illegal content, spam)';
COMMENT ON COLUMN reports.description IS 'Detailed description from the reporter';
COMMENT ON COLUMN reports.reporter_email IS 'Optional email of the person reporting';
COMMENT ON COLUMN reports.status IS 'Status of the report: new, reviewed, or resolved';
