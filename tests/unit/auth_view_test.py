import pytest
from unittest.mock import patch
from app.views.auth_view import AuthView


class TestAuthView:
    """Test cases for AuthView class"""

    @pytest.fixture
    def auth_view(self):
        """Create an AuthView instance for testing"""
        return AuthView()

    @patch('click.clear')
    @patch('click.echo')
    @patch('click.style')
    def test_show_welcome(self, mock_style, mock_echo, mock_clear, auth_view):
        """Test welcome message display"""
        mock_style.return_value = "EPIC EVENTS - SYSTÈME CRM"

        auth_view.show_welcome()

        # Verify clear was called
        mock_clear.assert_called_once()

        # Verify echo was called 4 times
        assert mock_echo.call_count == 4

        # Verify the header lines
        mock_echo.assert_any_call("=" * 50)

        # Verify style was called for the title
        mock_style.assert_called_once_with("EPIC EVENTS - SYSTÈME CRM")

    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_show_login_menu(self, mock_style, mock_echo, mock_prompt, auth_view):
        """Test login menu display and user input"""
        # Mock user input and styling
        mock_prompt.return_value = "1"
        mock_style.return_value = "styled_prompt"

        result = auth_view.show_login_menu()

        # Verify echo was called with menu options
        mock_echo.assert_any_call("📋 MENU PRINCIPAL")
        mock_echo.assert_any_call("-" * 20)
        mock_echo.assert_any_call("1. 🔐 Se connecter")
        mock_echo.assert_any_call("2. 🚪 Quitter")
        mock_echo.assert_any_call()

        # Verify prompt was called
        mock_prompt.assert_called_once()

        # Verify return value
        assert result == "1"

    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_show_login_menu_with_whitespace(self, mock_style, mock_echo, mock_prompt, auth_view):
        """Test login menu strips whitespace from user input"""
        # Mock user input with whitespace
        mock_prompt.return_value = "  2  "
        mock_style.return_value = "styled_prompt"

        result = auth_view.show_login_menu()

        # Verify whitespace is stripped
        assert result == "2"

    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_get_login_credentials(self, mock_style, mock_echo, mock_prompt, auth_view, sample_user_credentials):
        """Test getting login credentials from user"""
        # Mock user inputs and styling
        mock_prompt.side_effect = [
            sample_user_credentials["email"],
            sample_user_credentials["password"]
        ]
        mock_style.side_effect = ["styled_email", "styled_password"]

        email, password = auth_view.get_login_credentials()

        # Verify echo was called with login header
        mock_echo.assert_any_call()
        mock_echo.assert_any_call("🔐 CONNEXION")
        mock_echo.assert_any_call("-" * 15)

        # Verify prompt was called twice
        assert mock_prompt.call_count == 2

        # Verify return values
        assert email == sample_user_credentials["email"]
        assert password == sample_user_credentials["password"]

    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_get_login_credentials_strips_whitespace(self, mock_style, mock_echo, mock_prompt, auth_view):
        """Test that login credentials are stripped of whitespace"""
        # Mock user inputs with whitespace
        mock_prompt.side_effect = ["  user@test.com  ", "  password123  "]
        mock_style.side_effect = ["styled_email", "styled_password"]

        email, password = auth_view.get_login_credentials()

        # Verify whitespace is stripped
        assert email == "user@test.com"
        assert password == "password123"

    @patch('click.clear')
    @patch('click.echo')
    @patch('click.style')
    def test_show_goodbye(self, mock_style, mock_echo, mock_clear, auth_view):
        """Test goodbye message display"""
        mock_style.side_effect = ["styled_goodbye", "styled_farewell"]

        auth_view.show_goodbye()

        # Verify clear was called
        mock_clear.assert_called_once()

        # Verify echo was called 4 times (including empty lines)
        assert mock_echo.call_count == 4

        # Verify empty lines are echoed
        mock_echo.assert_any_call()

        # Verify style was called for goodbye messages
        mock_style.assert_any_call("👋 Merci d'avoir utilisé Epic Events CRM!")
        mock_style.assert_any_call("À bientôt !")



    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_get_login_credentials_empty_inputs(self, mock_style, mock_echo, mock_prompt, auth_view):
        """Test getting login credentials with empty inputs"""
        # Mock empty inputs
        mock_prompt.side_effect = ["", ""]
        mock_style.side_effect = ["styled_email", "styled_password"]

        email, password = auth_view.get_login_credentials()

        # Verify empty strings are returned
        assert email == ""
        assert password == ""

    @patch('click.prompt')
    @patch('click.echo')
    @patch('click.style')
    def test_show_login_menu_invalid_choice(self, mock_style, mock_echo, mock_prompt, auth_view):
        """Test login menu with invalid choice"""
        # Mock invalid input
        mock_prompt.return_value = "invalid_choice"
        mock_style.return_value = "styled_prompt"

        result = auth_view.show_login_menu()

        # Verify the invalid choice is returned
        assert result == "invalid_choice"

