from app.utils.password import verify_password
from app.db.connection import SessionLocal
from app.models.user import User


def login_user(email: str, password: str) -> User:
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()

    if user and verify_password(password, user.password):
        return user
    return None