from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_theatre_owner
from app.models.user import User

router = APIRouter(prefix="/owner", tags=["Owner"])

@router.get("/")
async def owner_dashboard(
    current_user: Annotated[User, Depends(get_current_theatre_owner)]
):
    """
    Protected endpoint accessible only to Theatre Owners.
    """
    return {"message": "Welcome Owner"}