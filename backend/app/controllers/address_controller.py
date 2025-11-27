from sqlalchemy.orm import Session

from app.models.location import Address
from app.schemas.location import AddressCreate


def create_address(db: Session, address_in: AddressCreate) -> Address:
    """
    Create and save a new address.
    """
    address = Address(
        street=address_in.street,
        area=address_in.area,
        postal_code=address_in.postal_code
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def get_all_addresses(db: Session) -> list[Address]:
    """
    Get all addresses from the database.
    """
    return db.query(Address).all()
