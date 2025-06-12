from app.models.base import Base
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.db.connection import engine

Base.metadata.create_all(bind=engine)
print("✅ Database and tables created")



