#!/usr/bin/env python3
"""
run_migrations.py
Simple migration runner for UMC database schema

Usage:
    python3 scripts/run_migrations.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from middleware.database import engine, Base
from sqlalchemy import text


def run_sql_migration(filepath: Path):
    """Run a .sql migration file"""
    print(f"Running migration: {filepath.name}")

    with open(filepath, 'r') as f:
        sql = f.read()

    with engine.begin() as conn:
        # Split on semicolons and execute each statement
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    conn.execute(text(statement))
                except Exception as e:
                    print(f"   ⚠️  Warning: {e}")

    print(f"   ✅ Complete")


def main():
    print("="*80)
    print("UMC Database Migration Runner")
    print("="*80)
    print()

    # Get migrations directory
    migrations_dir = Path(__file__).parent.parent / "migrations"

    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    # Find all .sql files
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print(f"❌ No .sql files found in {migrations_dir}")
        sys.exit(1)

    print(f"Found {len(migration_files)} migration file(s):")
    for f in migration_files:
        print(f"  - {f.name}")
    print()

    # Run each migration
    for migration_file in migration_files:
        run_sql_migration(migration_file)
        print()

    print("="*80)
    print("✅ All migrations complete!")
    print("="*80)
    print()

    # Verify tables exist
    print("Verifying tables...")
    from middleware.database import check_db_health

    health = check_db_health()

    if health["status"] == "healthy":
        print(f"✅ Database: {health['database_url']}")
        print(f"✅ Latency: {health['latency_ms']}ms")
        print()
        print("Table counts:")
        for table, count in health["tables"].items():
            print(f"  - {table}: {count} rows")
    else:
        print(f"❌ Database check failed: {health.get('error', 'unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
