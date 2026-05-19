#!/bin/bash
set -a
source .env
set +a
export PYTHONPATH=/app

echo "Running migrations..."
for script in scripts/migrate_*.py; do
    echo "Running $script"
    python $script
done

echo "Running seed scripts..."
python scripts/seed_data.py
python scripts/seed_garment_retail_pro.py
python scripts/seed_inventory.py
python scripts/seed_tenants.py
python scripts/seed_users.py
