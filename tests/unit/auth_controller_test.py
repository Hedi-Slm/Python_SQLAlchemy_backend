from unittest.mock import patch, Mock
from app.controllers.auth_controller import AuthController


class TestAuthController:
    """Test cases for authentication controller"""

    def setup_method(self):
        self.auth_controller = AuthController()

    @patch('app.controllers.auth_controller.login_user')
    @patch('app.controllers.auth_controller.show_success')
    def test_login_successful(self, mock_show_success, mock_login_user, mock_user):
        """Test successful login"""
        mock_login_user.return_value = mock_user

        self.auth_controller.view.show_welcome = Mock()
        self.auth_controller.view.show_login_menu = Mock(return_value="1")
        self.auth_controller.view.get_login_credentials = Mock(return_value=(mock_user.email, "password123"))

        result = self.auth_controller.login()

        assert result == mock_user
        assert self.auth_controller.current_user == mock_user
        mock_login_user.assert_called_once_with(mock_user.email, "password123")
        mock_show_success.assert_called_once_with(f"Connexion réussie ! Bienvenue {mock_user.name}")

    @patch('app.controllers.auth_controller.login_user')
    @patch('app.controllers.auth_controller.show_error')
    def test_login_invalid_credentials(self, mock_show_error, mock_login_user):
        """Test login with invalid credentials"""
        mock_login_user.return_value = None

        self.auth_controller.view.show_welcome = Mock()
        self.auth_controller.view.show_login_menu = Mock(side_effect=["1", "2"])
        self.auth_controller.view.get_login_credentials = Mock(return_value=("test@example.com", "wrong_password"))
        self.auth_controller.view.show_goodbye = Mock()

        result = self.auth_controller.login()

        assert result is None
        assert self.auth_controller.current_user is None
        mock_show_error.assert_called_with("Email ou mot de passe incorrect.")

    @patch('app.controllers.auth_controller.show_error')
    def test_login_empty_credentials(self, mock_show_error):
        """Test login with empty credentials"""
        self.auth_controller.view.show_welcome = Mock()
        self.auth_controller.view.show_login_menu = Mock(side_effect=["1", "2"])
        self.auth_controller.view.get_login_credentials = Mock(return_value=("", ""))
        self.auth_controller.view.show_goodbye = Mock()

        result = self.auth_controller.login()

        assert result is None
        mock_show_error.assert_called_with("Email et mot de passe requis.")

    @patch('app.controllers.auth_controller.show_error')
    def test_login_invalid_menu_choice(self, mock_show_error):
        """Test login with invalid menu choice"""
        self.auth_controller.view.show_welcome = Mock()
        self.auth_controller.view.show_login_menu = Mock(side_effect=["3", "2"])
        self.auth_controller.view.show_goodbye = Mock()

        result = self.auth_controller.login()

        assert result is None
        mock_show_error.assert_called_with("Choix invalide. Veuillez sélectionner 1 ou 2.")

    def test_login_exit_choice(self):
        """Test login with exit choice"""
        self.auth_controller.view.show_welcome = Mock()
        self.auth_controller.view.show_login_menu = Mock(return_value="2")
        self.auth_controller.view.show_goodbye = Mock()

        result = self.auth_controller.login()

        assert result is None
        self.auth_controller.view.show_goodbye.assert_called_once()

    @patch('app.controllers.auth_controller.show_success')
    def test_logout_with_user(self, mock_show_success, mock_user):
        """Test logout with logged-in user"""
        self.auth_controller.current_user = mock_user

        self.auth_controller.logout()

        assert self.auth_controller.current_user is None
        mock_show_success.assert_called_once_with(f"Au revoir {mock_user.name} !")

    def test_logout_without_user(self):
        """Test logout without logged-in user"""
        self.auth_controller.current_user = None

        self.auth_controller.logout()

        assert self.auth_controller.current_user is None

    def test_get_current_user(self, mock_user):
        """Test getting current user"""
        self.auth_controller.current_user = mock_user

        result = self.auth_controller.get_current_user()

        assert result == mock_user

    def test_get_current_user_none(self):
        """Test getting current user when none is logged in"""
        result = self.auth_controller.get_current_user()

        assert result is None
