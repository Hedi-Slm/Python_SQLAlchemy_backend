from app.services.user_service import create_user
from app.models.user import UserRole
from app.db.connection import SessionLocal


try:
    user = create_user(
        db=SessionLocal(),
        name="Gestion",
        email="gestion@mail.com",
        role=UserRole.GESTION,
        password="gestion"
    )
    print(f"✅ Utilisateur créé : {user}")
except Exception as e:
    print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
