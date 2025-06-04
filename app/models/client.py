from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company_name = Column(String)
    date_created = Column(Date)
    last_contact = Column(Date)

    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User")
