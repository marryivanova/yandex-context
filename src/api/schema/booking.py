from pydantic import BaseModel, Field, field_serializer
from datetime import datetime


class BookingCreate(BaseModel):
    user_id: int
    place_id: int
    time_from: datetime
    time_to: datetime

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    id: int
    user_id: int
    place_id: int
    from_: datetime = Field(..., alias="from")
    to_: datetime = Field(..., alias="to")

    @field_serializer("from_", "to_")
    def serialize_dt(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    class Config:
        populate_by_name = True


class BookingListResponse(BaseModel):
    bookings: list[BookingResponse]
