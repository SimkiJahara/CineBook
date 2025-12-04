"""Screening draft schema."""

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .user import Theaterowner


class ScreeningdraftBase(BaseModel):
    ownerid: int
    draftdata: Optional[dict] = None


class ScreeningdraftCreate(ScreeningdraftBase):
    pass


class Screeningdraft(ScreeningdraftBase):
    id: int
    createdat: Optional[datetime] = None
    theaterowner: Optional["Theaterowner"] = None

    model_config = ConfigDict(from_attributes=True)