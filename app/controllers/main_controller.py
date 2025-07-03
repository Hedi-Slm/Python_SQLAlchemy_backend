import sentry_sdk

from app.controllers.auth_controller import AuthController
from app.controllers.client_menu_controller import ClientMenuController
from app.controllers.contract_menu_controller import ContractMenuController
from app.controllers.event_menu_controller import EventMenuController
from app.controllers.user_menu_controller import UserMenuController
from app.views.main_view import MainView
from app.models.user import UserRole
from app.views.utils_view import show_error, show_info


class MainController:
    def __init__(self):
        self.auth_controller = AuthController()
        self.view = MainView()
        self.current_user = None

    def run(self):
        """Main application loop"""
        # Handle login
        user = self.auth_controller.login()

        if not user:
            return  # User chose to exit

        self.current_user = user

        while True:
            try:
                choice = self.view.show_main_menu(user)

                if choice == "1":
                    self.client_menu()
                elif choice == "2":
                    self.contract_menu()
                elif choice == "3":
                    self.event_menu()
                elif choice == "4" and user.role == UserRole.GESTION:
                    self.user_menu()
                elif choice == "0":
                    self.auth_controller.logout()
                    break
                else:
                    show_error("Choix invalide.")

            except KeyboardInterrupt:
                show_info("Déconnexion en cours...")
                self.auth_controller.logout()
                break
            except Exception as e:
                show_error(f"Une erreur s'est produite: {str(e)}")
                sentry_sdk.capture_exception(e)

    def client_menu(self):
        """Handle clients menu navigation"""
        client_controller = ClientMenuController(self.current_user)
        client_controller.handle_menu()

    def contract_menu(self):
        """Handle contracts menu navigation"""
        contract_controller = ContractMenuController(self.current_user)
        contract_controller.handle_menu()

    def event_menu(self):
        """Handle events menu navigation"""
        event_controller = EventMenuController(self.current_user)
        event_controller.handle_menu()

    def user_menu(self):
        """Handle users menu navigation (GESTION only)"""
        if self.current_user.role == UserRole.GESTION:
            user_controller = UserMenuController(self.current_user)
            user_controller.handle_menu()
        else:
            show_error("Accès non autorisé.")
