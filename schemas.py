from pydantic import BaseModel, Field
from typing import Optional

# Travel app schemas map directly to MongoDB collections by lowercase class name

class Search(BaseModel):
    type: str = Field(..., description="flights | hotels | trains")
    origin: Optional[str] = Field(None)
    destination: Optional[str] = Field(None)
    date: Optional[str] = Field(None, description="YYYY-MM-DD")
    city: Optional[str] = Field(None)
    checkin: Optional[str] = Field(None)
    checkout: Optional[str] = Field(None)

class BookingIntent(BaseModel):
    kind: str = Field(..., description="flight | hotel | train")
    reference: str = Field(..., description="human-readable reference/number")
    traveler_name: str
    contact_email: str
    price: float
    meta: Optional[dict] = Field(default_factory=dict)
