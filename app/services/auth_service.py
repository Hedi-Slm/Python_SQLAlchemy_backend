from app.utils.password import verify_password
from app.db.connection import SessionLocal
from app.models.user import User


def login_user(email: str, password: str) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user and verify_password(password, user.password):
            return user
        return None
    finally:
        db.close()
