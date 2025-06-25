from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # ADD THIS LINE
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    support_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(Text)

    contract = relationship("Contract")
    client = relationship("Client")
    support_contact = relationship("User")
