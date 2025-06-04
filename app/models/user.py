from sqlalchemy import Column, Integer, String, Enum
from app.models.base import Base
import enum


class UserRole(enum.Enum):
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    GESTION = "gestion"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
    role = Column(Enum(UserRole), nullable=False)
