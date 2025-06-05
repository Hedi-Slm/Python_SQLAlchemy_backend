from sqlalchemy.orm import Session
from app.models.user import User, UserRole
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


def list_users(db: Session):
    return db.query(User).all()
