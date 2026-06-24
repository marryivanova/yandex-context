from sqlalchemy import Column, DateTime, Integer

from src.database.core import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    place_id = Column(Integer, nullable=False)
    time_from = Column(DateTime, nullable=False)
    time_to = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, place_id={self.place_id}, from={self.time_from}, to={self.time_to})>"
