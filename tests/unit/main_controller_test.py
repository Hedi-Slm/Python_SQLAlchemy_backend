import pytest
from unittest.mock import Mock, patch
from app.controllers.main_controller import MainController


@pytest.fixture

def main_controller():
    return MainController()


@pytest.mark.usefixtures("mock_user", "mock_gestion_user")
class TestMainController:

    def setup_method(self):
        self.main_controller = MainController()

    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_init(self, mock_main_view, mock_auth_controller):
        controller = MainController()
        mock_auth_controller.assert_called_once()
        mock_main_view.assert_called_once()
        assert controller.current_user is None

    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_user_exits_on_login(self, mock_main_view, mock_auth_controller):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = None
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController()
        controller.run()

        mock_auth_instance.login.assert_called_once()

    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_successful_login_and_logout(self, mock_main_view, mock_auth_controller, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view_instance = Mock()
        mock_view_instance.show_main_menu.return_value = "0"
        mock_main_view.return_value = mock_view_instance

        controller = MainController()
        controller.run()

        mock_auth_instance.login.assert_called_once()
        mock_view_instance.show_main_menu.assert_called_once_with(mock_user)
        mock_auth_instance.logout.assert_called_once()
        assert controller.current_user == mock_user

    @patch('app.controllers.main_controller.ClientMenuController')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_client_menu_choice(self, mock_main_view, mock_auth_controller, mock_client_controller, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["1", "0"]
        mock_main_view.return_value = mock_view

        mock_client_instance = Mock()
        mock_client_controller.return_value = mock_client_instance

        controller = MainController()
        controller.run()

        mock_client_controller.assert_called_once_with(mock_user)
        mock_client_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.ContractMenuController')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_contract_menu_choice(self, mock_main_view, mock_auth_controller, mock_contract_controller, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["2", "0"]
        mock_main_view.return_value = mock_view

        mock_contract_instance = Mock()
        mock_contract_controller.return_value = mock_contract_instance

        controller = MainController()
        controller.run()

        mock_contract_controller.assert_called_once_with(mock_user)
        mock_contract_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.EventMenuController')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_event_menu_choice(self, mock_main_view, mock_auth_controller, mock_event_controller, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["3", "0"]
        mock_main_view.return_value = mock_view

        mock_event_instance = Mock()
        mock_event_controller.return_value = mock_event_instance

        controller = MainController()
        controller.run()

        mock_event_controller.assert_called_once_with(mock_user)
        mock_event_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.UserMenuController')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_user_menu_choice_gestion_user(self, mock_main_view, mock_auth_controller, mock_user_controller, mock_gestion_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_gestion_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["4", "0"]
        mock_main_view.return_value = mock_view

        mock_user_instance = Mock()
        mock_user_controller.return_value = mock_user_instance

        controller = MainController()
        controller.run()

        mock_user_controller.assert_called_once_with(mock_gestion_user)
        mock_user_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.show_error')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_user_menu_choice_non_gestion_user(self, mock_main_view, mock_auth_controller, mock_show_error, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["4", "0"]
        mock_main_view.return_value = mock_view

        controller = MainController()
        controller.run()

        mock_show_error.assert_called_once_with("Choix invalide.")

    @patch('app.controllers.main_controller.show_error')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_invalid_choice(self, mock_main_view, mock_auth_controller, mock_show_error, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = ["99", "0"]
        mock_main_view.return_value = mock_view

        controller = MainController()
        controller.run()

        mock_show_error.assert_called_once_with("Choix invalide.")

    @patch('app.controllers.main_controller.show_info')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_keyboard_interrupt(self, mock_main_view, mock_auth_controller, mock_show_info, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        mock_view = Mock()
        mock_view.show_main_menu.side_effect = KeyboardInterrupt()
        mock_main_view.return_value = mock_view

        controller = MainController()
        controller.run()

        mock_show_info.assert_called_once_with("Déconnexion en cours...")
        mock_auth_instance.logout.assert_called_once()

    @patch('app.controllers.main_controller.sentry_sdk')
    @patch('app.controllers.main_controller.show_error')
    @patch('app.controllers.main_controller.AuthController')
    @patch('app.controllers.main_controller.MainView')
    def test_run_generic_exception(self, mock_main_view, mock_auth_controller, mock_show_error, mock_sentry, mock_user):
        mock_auth_instance = Mock()
        mock_auth_instance.login.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance

        exception_instance = Exception("Test error")
        mock_view = Mock()
        mock_view.show_main_menu.side_effect = [exception_instance, "0"]
        mock_main_view.return_value = mock_view

        controller = MainController()
        controller.run()

        mock_show_error.assert_called_once_with("Une erreur s'est produite: Test error")
        mock_sentry.capture_exception.assert_called_once_with(exception_instance)

    @patch('app.controllers.main_controller.ClientMenuController')
    def test_client_menu(self, mock_client_controller, mock_user):
        mock_client_instance = Mock()
        mock_client_controller.return_value = mock_client_instance

        controller = MainController()
        controller.current_user = mock_user
        controller.client_menu()

        mock_client_controller.assert_called_once_with(mock_user)
        mock_client_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.ContractMenuController')
    def test_contract_menu(self, mock_contract_controller, mock_user):
        mock_contract_instance = Mock()
        mock_contract_controller.return_value = mock_contract_instance

        controller = MainController()
        controller.current_user = mock_user
        controller.contract_menu()

        mock_contract_controller.assert_called_once_with(mock_user)
        mock_contract_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.EventMenuController')
    def test_event_menu(self, mock_event_controller, mock_user):
        mock_event_instance = Mock()
        mock_event_controller.return_value = mock_event_instance

        controller = MainController()
        controller.current_user = mock_user
        controller.event_menu()

        mock_event_controller.assert_called_once_with(mock_user)
        mock_event_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.UserMenuController')
    def test_user_menu_gestion_user(self, mock_user_controller, mock_gestion_user):
        mock_user_instance = Mock()
        mock_user_controller.return_value = mock_user_instance

        controller = MainController()
        controller.current_user = mock_gestion_user
        controller.user_menu()

        mock_user_controller.assert_called_once_with(mock_gestion_user)
        mock_user_instance.handle_menu.assert_called_once()

    @patch('app.controllers.main_controller.show_error')
    def test_user_menu_non_gestion_user(self, mock_show_error, mock_user):
        controller = MainController()
        controller.current_user = mock_user
        controller.user_menu()

        mock_show_error.assert_called_once_with("Accès non autorisé.")
