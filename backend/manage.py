#!/usr/bin/env python
"""
Database migration management script using Flask-Migrate
"""
from flask_migrate import Migrate, init, migrate as migrate_cmd, upgrade, downgrade
from src.app import create_app

app = create_app()

if __name__ == '__main__':
    import sys

    with app.app_context():
        if len(sys.argv) < 2:
            print("Usage: python manage.py [init|migrate|upgrade|downgrade|seed]")
            print("\nCommands:")
            print("  init      - Initialize migrations directory")
            print("  migrate   - Create a new migration")
            print("  upgrade   - Apply migrations to database")
            print("  downgrade - Revert last migration")
            print("  seed      - Seed database with demo data")
            sys.exit(1)

        command = sys.argv[1]

        if command == 'init':
            print("Initializing migrations...")
            from flask_migrate import init
            init(directory='migrations')
            print("Migrations initialized!")

        elif command == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
            print(f"Creating migration: {message}")
            from flask_migrate import migrate
            migrate(directory='migrations', message=message)
            print("Migration created!")

        elif command == 'upgrade':
            print("Applying migrations...")
            from flask_migrate import upgrade
            upgrade(directory='migrations')
            print("Migrations applied!")

        elif command == 'downgrade':
            print("Reverting last migration...")
            from flask_migrate import downgrade
            downgrade(directory='migrations')
            print("Migration reverted!")

        elif command == 'seed':
            print("Seeding database with demo data...")
            from src.database.models import db_drop_and_create_all
            db_drop_and_create_all()
            print("Database seeded successfully!")

        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, migrate, upgrade, downgrade, seed")
            sys.exit(1)