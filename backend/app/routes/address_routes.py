from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import AddressCreate, AddressRead
from app.controllers.address_controller import create_address, get_all_addresses

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressRead)
def create_address_route(address: AddressCreate, db: Session = Depends(get_db)):
    return create_address(db, address)


@router.get("/", response_model=list[AddressRead])
def get_addresses_route(db: Session = Depends(get_db)):
    return get_all_addresses(db)
