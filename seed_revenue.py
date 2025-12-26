#!/usr/bin/env python3
"""
FPT Branch Revenue Data Seeder

Generates realistic monthly revenue data for FPT's 3 branches:
- Ho Chi Minh (HCM): Largest branch
- Ha Noi (HN): Medium branch
- Da Nang (DN): Smaller branch

Data patterns:
- Branch size hierarchy: HCM > HN > DN
- Seasonal variations: Q4 boost, Q1 slowdown
- Year-over-year growth: 8% from 2024 to 2025
- Random noise: ±10% variation
"""

import os
import random
import calendar
from datetime import date
from decimal import Decimal

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Branch definitions with size multipliers
BRANCHES = {
    "HCM": {"name": "Ho Chi Minh", "multiplier": 1.0},    # Largest
    "HN": {"name": "Ha Noi", "multiplier": 0.85},         # Medium
    "DN": {"name": "Da Nang", "multiplier": 0.6},         # Smaller
}

# Quarterly seasonal multipliers
QUARTERLY_MULTIPLIERS = {
    1: 0.90,  # Q1: Post-holiday slowdown
    2: 1.00,  # Q2: Normal
    3: 1.05,  # Q3: Mid-year push
    4: 1.15,  # Q4: Holiday season boost
}

# Year-over-year growth
YEAR_MULTIPLIERS = {
    2024: 1.0,    # Baseline
    2025: 1.08,   # 8% growth
}

# Revenue range (in VND)
BASE_REVENUE_MIN = 12_000_000_000  # 12 billion VND
BASE_REVENUE_MAX = 20_000_000_000  # 20 billion VND

# Random variation (±10%)
NOISE_RANGE = 0.10


def get_quarter(month: int) -> int:
    """Get quarter number (1-4) from month (1-12)."""
    return (month - 1) // 3 + 1


def get_last_day_of_month(year: int, month: int) -> date:
    """Get the last day of the given month."""
    _, last_day = calendar.monthrange(year, month)
    return date(year, month, last_day)


def generate_revenue(
    branch_multiplier: float,
    quarter: int,
    year: int,
    seed: int = None
) -> int:
    """
    Generate realistic revenue with all multipliers applied.

    Args:
        branch_multiplier: Size factor for the branch (0.6 - 1.0)
        quarter: Quarter number (1-4) for seasonal adjustment
        year: Year for YoY growth factor
        seed: Optional random seed for reproducibility

    Returns:
        Revenue in VND, rounded to millions
    """
    if seed is not None:
        random.seed(seed)

    # Start with random base revenue
    base = random.uniform(BASE_REVENUE_MIN, BASE_REVENUE_MAX)

    # Apply multipliers
    revenue = base * branch_multiplier
    revenue *= QUARTERLY_MULTIPLIERS[quarter]
    revenue *= YEAR_MULTIPLIERS[year]

    # Add random noise (±10%)
    noise = random.uniform(1 - NOISE_RANGE, 1 + NOISE_RANGE)
    revenue *= noise

    # Round to nearest million
    revenue = round(revenue / 1_000_000) * 1_000_000

    return int(revenue)


def create_table(cursor):
    """Create the branch_revenue table if it doesn't exist."""
    cursor.execute("""
        DROP TABLE IF EXISTS branch_revenue;

        CREATE TABLE branch_revenue (
            id SERIAL PRIMARY KEY,
            branch_code VARCHAR(3) NOT NULL,
            branch_name VARCHAR(50) NOT NULL,
            report_date DATE NOT NULL,
            revenue_vnd BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(branch_code, report_date)
        );

        CREATE INDEX idx_branch_revenue_date ON branch_revenue(report_date);
        CREATE INDEX idx_branch_revenue_branch ON branch_revenue(branch_code);
    """)
    print("✓ Table 'branch_revenue' created successfully")


def seed_data(cursor):
    """Generate and insert all revenue data."""
    records = []

    for year in [2024, 2025]:
        for month in range(1, 13):
            quarter = get_quarter(month)
            report_date = get_last_day_of_month(year, month)

            for branch_code, branch_info in BRANCHES.items():
                revenue = generate_revenue(
                    branch_multiplier=branch_info["multiplier"],
                    quarter=quarter,
                    year=year,
                )

                records.append((
                    branch_code,
                    branch_info["name"],
                    report_date,
                    revenue,
                ))

    # Bulk insert all records
    cursor.executemany(
        """
        INSERT INTO branch_revenue (branch_code, branch_name, report_date, revenue_vnd)
        VALUES (%s, %s, %s, %s)
        """,
        records
    )

    print(f"✓ Inserted {len(records)} revenue records")
    return records


def print_sample_data(records):
    """Print a sample of the generated data."""
    print("\n📊 Sample Data (first and last 3 records):\n")
    print(f"{'Branch':<5} {'Name':<15} {'Date':<12} {'Revenue (VND)':>20}")
    print("-" * 55)

    for record in records[:3] + records[-3:]:
        branch_code, name, report_date, revenue = record
        revenue_formatted = f"{revenue:,}"
        print(f"{branch_code:<5} {name:<15} {report_date} {revenue_formatted:>20}")

    print("\n" + "-" * 55)

    # Summary statistics
    total_2024 = sum(r[3] for r in records if r[2].year == 2024)
    total_2025 = sum(r[3] for r in records if r[2].year == 2025)
    growth = ((total_2025 - total_2024) / total_2024) * 100

    print(f"\n📈 Summary:")
    print(f"   Total 2024: {total_2024:,} VND")
    print(f"   Total 2025: {total_2025:,} VND")
    print(f"   YoY Growth: {growth:.1f}%")


def main():
    """Main entry point."""
    print("🚀 FPT Revenue Data Seeder\n")

    try:
        # Connect to database
        print(f"Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to database\n")

        # Create table and seed data
        create_table(cursor)
        records = seed_data(cursor)

        # Commit changes
        conn.commit()
        print("✓ Changes committed\n")

        # Show sample data
        print_sample_data(records)

        # Cleanup
        cursor.close()
        conn.close()
        print("\n✅ Done! Database seeded successfully.")

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
