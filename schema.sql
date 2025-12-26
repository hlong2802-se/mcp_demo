-- FPT Branch Revenue Schema
-- PostgreSQL 15+

-- Drop table if exists (for clean re-runs)
DROP TABLE IF EXISTS branch_revenue;

-- Create the revenue table
CREATE TABLE branch_revenue (
    id SERIAL PRIMARY KEY,
    branch_code VARCHAR(3) NOT NULL,       -- HCM, HN, DN
    branch_name VARCHAR(50) NOT NULL,      -- Full branch name
    report_date DATE NOT NULL,             -- Last day of month (e.g., 2024-01-31)
    revenue_vnd BIGINT NOT NULL,           -- Revenue in VND (rounded to millions)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate entries for same branch/month
    UNIQUE(branch_code, report_date)
);

-- Indexes for efficient MCP server queries
CREATE INDEX idx_branch_revenue_date ON branch_revenue(report_date);
CREATE INDEX idx_branch_revenue_branch ON branch_revenue(branch_code);

-- Optional: Add a comment for documentation
COMMENT ON TABLE branch_revenue IS 'Monthly revenue data for FPT branches (2024-2025)';
COMMENT ON COLUMN branch_revenue.report_date IS 'Last day of the reporting month';
COMMENT ON COLUMN branch_revenue.revenue_vnd IS 'Revenue in Vietnamese Dong, rounded to millions';
