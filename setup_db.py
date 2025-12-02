#!/usr/bin/env python
# =============================================================================
# Database Setup Script
# =============================================================================
# Initialize the database with required tables and default roles.
# Run this script before starting the application: python setup_db.py
#
# As described in the article:
# "Now you need to create the initial roles in your database."
# =============================================================================

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal, engine, Base
from app.models import User, Role, Seat, SeatType
from app.services import get_role_by_name, create_role, get_seat_count, create_seat


def init_database() -> None:
    """
    Initialize the database.

    Creates all tables defined in SQLAlchemy models and sets up
    the default roles required for the application.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def init_roles() -> None:
    """
    Initialize default roles.

    As described in the article:
    "# Create roles if they don't exist
    if not crud.get_role_by_name(db, "user"):
        crud.create_role(db, "user", "Regular user")

    if not crud.get_role_by_name(db, "admin"):
        crud.create_role(db, "admin", "Administrator")

    if not crud.get_role_by_name(db, "moderator"):
        crud.create_role(db, "moderator", "Moderator")"
    """
    db = SessionLocal()

    try:
        # Default roles as specified in the article
        default_roles = [
            ("user", "Regular user with basic permissions"),
            ("admin", "Administrator with full access"),
            ("moderator", "Moderator with content management permissions"),
        ]

        for role_name, role_description in default_roles:
            existing_role = get_role_by_name(db, role_name)
            if not existing_role:
                create_role(db, role_name, role_description)
                print(f"✓ Created role: {role_name}")
            else:
                print(f"- Role already exists: {role_name}")

        print("\n✓ Roles initialized successfully!")

    finally:
        db.close()


def init_seats() -> None:
    """
    Initialize theater seats.

    Creates a theater layout with:
    - Rows A, B, C: Standard seats at 10 Taka each
    - Rows D, E: VIP seats at 20 Taka each
    - 10 seats per row = 50 total seats
    """
    db = SessionLocal()

    try:
        # Check if seats already exist
        existing_count = get_seat_count(db)
        if existing_count > 0:
            print(f"- Seats already exist: {existing_count} seats found")
            return

        print("Creating theater seats...")

        # Define seat configuration
        seat_config = [
            # (row, seat_type, price)
            ("A", SeatType.STANDARD.value, 10.0),
            ("B", SeatType.STANDARD.value, 10.0),
            ("C", SeatType.STANDARD.value, 10.0),
            ("D", SeatType.VIP.value, 20.0),
            ("E", SeatType.VIP.value, 20.0),
        ]

        seats_per_row = 10
        created_count = 0

        for row, seat_type, price in seat_config:
            for number in range(1, seats_per_row + 1):
                create_seat(
                    db, row=row, number=number, seat_type=seat_type, price=price
                )
                created_count += 1
            print(
                f"✓ Created row {row}: {seats_per_row} {seat_type} seats at {price} Taka each"
            )

        print(f"\n✓ Created {created_count} total seats!")

    finally:
        db.close()


def main() -> None:
    """Main setup function."""
    print("=" * 60)
    print("FastAPI Authentication - Database Setup")
    print("=" * 60)
    print()

    try:
        init_database()
        print()
        init_roles()
        print()
        init_seats()
        print()
        print("=" * 60)
        print("Database initialized successfully!")
        print("You can now start the server with: python run.py")
        print("Visit /booking to access the Movie Ticket Booking System")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
