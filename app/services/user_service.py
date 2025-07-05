from typing import Type

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.utils.password import hash_password


def create_user(db: Session, name: str, email: str, role: UserRole, password: str) -> User:
    hashed = hash_password(password)
    user = User(name=name, email=email, role=role, password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, **fields) -> User:
    user = db.query(User).filter_by(id=user_id).first()
    for key, value in fields.items():
        setattr(user, key, value)
    db.commit()
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = db.query(User).filter_by(id=user_id).first()
    db.delete(user)
    db.commit()


def list_all_users(db: Session):
    return db.query(User).all()


def get_user_by_email(db: Session, email: str) -> Type[User] | None:
    return db.query(User).filter_by(email=email).first()


def get_user_by_id(db: Session, user_id: int) -> Type[User] | None:
    return db.query(User).filter_by(id=user_id).first()


def check_user_associations(db: Session, user_id: int) -> dict:
    """Check if user has associated data (clients, contracts, events)"""
    clients_count = db.query(Client).filter_by(commercial_id=user_id).count()
    contracts_count = db.query(Contract).filter_by(commercial_id=user_id).count()
    events_count = db.query(Event).filter_by(support_id=user_id).count()

    return {
        'clients_count': clients_count,
        'contracts_count': contracts_count,
        'events_count': events_count,
        'has_associations': clients_count > 0 or contracts_count > 0 or events_count > 0
    }


def email_exists_for_different_user(db: Session, email: str, user_id: int) -> bool:
    """Check if email exists for a different user (used for updates)"""
    existing_user = db.query(User).filter_by(email=email).first()
    return existing_user is not None and existing_user.id != user_id
