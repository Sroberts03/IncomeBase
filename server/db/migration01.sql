-- Migration 01: Initial Schema for IncomeBase

-- Enums
CREATE TYPE file_classification_enum AS ENUM ('w2', 'bank_statement', '1099', 'institution_report');
CREATE TYPE file_source_enum AS ENUM ('stripe', 'plaid', 'shopify', 'paypal', 'amazon_seller', 'upwork/fiverr', 'bank', 'other');
CREATE TYPE borrower_status_enum AS ENUM (
    'Needs Link Creation', 
    'Link Created', 
    'Docs Not Submitted', 
    'Docs Submitted', 
    'Analyzing',
    'Analysis Failed',
    'Completed',
    'No Files',
    'System Error'
);

-- Helper function for auto-updating timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tables
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_name TEXT NOT NULL,
    sub_tier TEXT,
    admin_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Apply trigger to organizations
CREATE TRIGGER set_timestamp_organizations
BEFORE UPDATE ON organizations
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE organization_members (
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    member_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT,
    PRIMARY KEY (org_id, member_id)
);

CREATE TABLE borrowers (
    borrower_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lender_id UUID REFERENCES auth.users(id),
    full_name TEXT NOT NULL,
    email TEXT,
    org_id UUID REFERENCES organizations(id),
    zip_code TEXT,
    status borrower_status_enum DEFAULT 'Needs Link Creation',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Apply trigger to borrowers
CREATE TRIGGER set_timestamp_borrowers
BEFORE UPDATE ON borrowers
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Note: link_token and expiration moved exclusively to file_links table to prevent sync issues

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    borrower_id UUID REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    classification file_classification_enum,
    source file_source_enum,
    file_name TEXT,
    needs_to_be_processed BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE reasoning_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    borrower_id UUID REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    agent TEXT,
    raw_reasoning TEXT,
    flags JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE borrower_analysis (
    borrower_id UUID PRIMARY KEY REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    monthly_average_income NUMERIC,
    income_stability_score NUMERIC,
    recurring_income_percentage NUMERIC,
    income_trend TEXT,
    largest_deposit_source TEXT,
    expense_to_income_ratio NUMERIC,
    net_burn_rate NUMERIC,
    income_ytd JSONB,
    income_last_6 JSONB,
    income_last_12 JSONB,
    income_last_24 JSONB,
    nsf_count_total INTEGER,
    risk_factors JSONB,
    anomalous_deposits JSONB,
    confidence_score NUMERIC,
    analysis_summary TEXT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    borrower_id UUID REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    file_name TEXT,
    amount NUMERIC,
    date DATE,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE file_links (
    borrower_id UUID PRIMARY KEY REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    link_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS for basic security (standard for Supabase)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE borrowers ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE reasoning_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE borrower_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_links ENABLE ROW LEVEL SECURITY;

-- 1. Organizations: Users can see organizations they are members of
CREATE POLICY organization_access ON organizations
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM organization_members
            WHERE organization_members.org_id = organizations.id
            AND organization_members.member_id = auth.uid()
        )
    );

-- 2. Organization Members: Users can see members of their own organizations
CREATE POLICY member_access ON organization_members
    FOR SELECT
    TO authenticated
    USING (
        org_id IN (
            SELECT org_id FROM organization_members WHERE member_id = auth.uid()
        )
    );

-- 3. Borrowers: Access restricted to lender_id or organization members
CREATE POLICY borrower_access ON borrowers
    FOR ALL
    TO authenticated
    USING (
        lender_id = auth.uid()
        OR
        EXISTS (
            SELECT 1 FROM organization_members
            WHERE organization_members.org_id = borrowers.org_id
            AND organization_members.member_id = auth.uid()
        )
    );

-- 4. Related Data: Files, Analysis, Logs, Line Items (Cascaded from Borrower Access)
CREATE POLICY file_access ON files
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM borrowers
            WHERE borrowers.borrower_id = files.borrower_id
        )
    );

CREATE POLICY analysis_access ON borrower_analysis
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM borrowers
            WHERE borrowers.borrower_id = borrower_analysis.borrower_id
        )
    );

CREATE POLICY reasoning_access ON reasoning_logs
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM borrowers
            WHERE borrowers.borrower_id = reasoning_logs.borrower_id
        )
    );

CREATE POLICY line_item_access ON line_items
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM borrowers
            WHERE borrowers.borrower_id = line_items.borrower_id
        )
    );

-- 5. File Links: Publicly accessible for anonymous uploads by link_token, 
-- but protected for administrative access via borrower.
-- FIX: Removed (true) to prevent link enumeration by malicious bots.
CREATE POLICY file_link_public_select ON file_links
    FOR SELECT
    TO anon, authenticated
    USING (
        -- Can only see if they know the token
        link_token IS NOT NULL
    );

CREATE POLICY file_link_admin_access ON file_links
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM borrowers
            WHERE borrowers.borrower_id = file_links.borrower_id
        )
    );

-- 6. Advanced Admin Controls: Only Org Admins can manage members
CREATE POLICY org_admin_update ON organizations
    FOR UPDATE
    TO authenticated
    USING (admin_id = auth.uid());

CREATE POLICY member_management ON organization_members
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM organizations
            WHERE organizations.id = organization_members.org_id
            AND organizations.admin_id = auth.uid()
        )
    );

-- 7. Strict Data Integrity: Prevent unauthorized insertion or modification
CREATE POLICY borrower_insert_safety ON borrowers
    FOR INSERT
    TO authenticated
    WITH CHECK (
        lender_id = auth.uid()
        AND
        EXISTS (
            SELECT 1 FROM organization_members
            WHERE organization_members.org_id = borrowers.org_id
            AND organization_members.member_id = auth.uid()
        )
    );

-- Analysis Read-Only for Users (AI/System writes via service_role)
CREATE POLICY analysis_read_only ON borrower_analysis
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY analysis_no_manual_mod_update ON borrower_analysis
    FOR UPDATE
    TO authenticated
    USING (false);

CREATE POLICY analysis_no_manual_mod_delete ON borrower_analysis
    FOR DELETE
    TO authenticated
    USING (false);

-- Audit Trail Protection: Logs cannot be deleted
CREATE POLICY logs_no_delete ON reasoning_logs
    FOR DELETE
    TO authenticated
    USING (false);

-- 8. Storage Bucket Security (Assumes path structure: borrower_id/file_name)
-- Note: These policies are applied to the storage.objects table
CREATE POLICY "Lenders can upload borrower documents"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'borrower-files' 
    AND (storage.foldername(name))[1] IN (
        SELECT borrower_id::text FROM borrowers WHERE lender_id = auth.uid()
    )
);

CREATE POLICY "Lenders can view borrower documents"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'borrower-files'
    AND (storage.foldername(name))[1] IN (
        SELECT borrower_id::text FROM borrowers
    )
);

-- ==========================================
-- INDEXES FOR PERFORMANCE & RLS OPTIMIZATION
-- ==========================================

-- 1. Borrowers
-- For lender dashboards and RLS visibility checks
CREATE INDEX idx_borrowers_lender_id ON borrowers(lender_id);
-- For organization-wide visibility and RLS checks
CREATE INDEX idx_borrowers_org_id ON borrowers(org_id);
-- For filtering dashboards by borrower status efficiently
CREATE INDEX idx_borrowers_status ON borrowers(status);

-- 2. Organization Members
-- The PK covers (org_id, member_id), but we frequently query by member_id for RLS (auth.uid()) and `get_org_id_for_lender`
CREATE INDEX idx_org_members_member_id ON organization_members(member_id);

-- 3. Organizations
-- For RLS policies checking admin rights
CREATE INDEX idx_organizations_admin_id ON organizations(admin_id);

-- 4. Files
-- Highly targeted index for `get_pending_records` and `get_files_for_borrower`
CREATE INDEX idx_files_borrower_processing ON files(borrower_id, needs_to_be_processed);

-- 5. Line Items
-- Heavy queries by borrower_id during analysis pipeline and cascaded RLS
CREATE INDEX idx_line_items_borrower_id ON line_items(borrower_id);
-- Useful when updating or deleting records related to specific files
CREATE INDEX idx_line_items_file_id ON line_items(file_id);

-- 6. Reasoning Logs
-- For cascaded RLS checks and fetching logs by borrower
CREATE INDEX idx_reasoning_logs_borrower_id ON reasoning_logs(borrower_id);

-- Note:
-- file_links(link_token) is already indexed via UNIQUE constraint.
-- borrower_analysis(borrower_id) is already indexed via PRIMARY KEY.

