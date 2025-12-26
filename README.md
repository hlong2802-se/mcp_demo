How to Run

  # 1. Start PostgreSQL (if not running)
  docker-compose up -d

  # 2. Install Python dependencies
  pip install -r requirements.txt

  # 3. Run the seeder script
  python seed_revenue.py

  Expected Output

  🚀 FPT Revenue Data Seeder

  Connecting to PostgreSQL at localhost:5432...
  ✓ Connected to database

  ✓ Table 'branch_revenue' created successfully
  ✓ Inserted 72 revenue records
  ✓ Changes committed

  📊 Sample Data (first and last 3 records):

  Branch Name            Date         Revenue (VND)
  -------------------------------------------------------
  HCM    Ho Chi Minh    2024-01-31   14,235,000,000
  HN     Ha Noi         2024-01-31   12,100,000,000
  DN     Da Nang        2024-01-31    8,541,000,000
  ...

  📈 Summary:
     Total 2024: ~380B VND
     Total 2025: ~410B VND
     YoY Growth: ~8%

  ✅ Done! Database seeded successfully.
