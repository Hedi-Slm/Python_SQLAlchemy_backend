from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.user import User, UserRole


def create_client(db: Session, commercial_id: int, **data) -> Client:
    client = Client(**data, commercial_id=commercial_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, client_id: int, updater: User, **fields) -> Client:
    client = db.query(Client).filter_by(id=client_id).first()
    if updater.role == UserRole.COMMERCIAL and client.commercial_id != updater.id:
        raise PermissionError("You can only update your own clients.")
    for key, value in fields.items():
        setattr(client, key, value)
    db.commit()
    return client


def get_clients_by_user(db: Session, user: User):
    if user.role == UserRole.COMMERCIAL:
        return db.query(Client).filter_by(commercial_id=user.id).all()
    return db.query(Client).all()
