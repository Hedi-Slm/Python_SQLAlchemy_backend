from app.services.auth_service import login_user
from app.views.auth_view import AuthView
from app.models.user import User


class AuthController:
    def __init__(self):
        self.view = AuthView()
        self.current_user = None

    def login(self) -> User:
        """Handle user login process"""
        while True:
            self.view.show_welcome()

            choice = self.view.show_login_menu()

            if choice == "1":
                # Login
                email, password = self.view.get_login_credentials()

                if not email or not password:
                    self.view.show_error("Email et mot de passe requis.")
                    continue

                user = login_user(email, password)

                if user:
                    self.current_user = user
                    self.view.show_success(f"Connexion réussie ! Bienvenue {user.name}")
                    return user
                else:
                    self.view.show_error("Email ou mot de passe incorrect.")

            elif choice == "2":
                # Exit
                self.view.show_goodbye()
                return None

            else:
                self.view.show_error("Choix invalide. Veuillez sélectionner 1 ou 2.")

    def logout(self):
        """Handle user logout"""
        if self.current_user:
            self.view.show_success(f"Au revoir {self.current_user.name} !")
            self.current_user = None

    def get_current_user(self) -> User:
        """Get the current user"""
        return self.current_user