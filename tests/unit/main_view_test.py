import pytest
from unittest.mock import patch
from app.views.main_view import MainView


@pytest.mark.usefixtures("mock_user", "mock_support_user", "mock_gestion_user")
class TestMainView:
    def setup_method(self):
        self.main_view = MainView()

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_commercial_user(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "1"

        result = self.main_view.show_main_menu(mock_user)

        mock_clear.assert_called_once()
        assert mock_echo.call_count > 0
        assert result == "1"

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert not any("🔑 Gestion des utilisateurs" in str(call) for call in echo_calls)

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_support_user(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_support_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "2"

        result = self.main_view.show_main_menu(mock_support_user)

        mock_clear.assert_called_once()
        assert mock_echo.call_count > 0
        assert result == "2"

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert not any("🔑 Gestion des utilisateurs" in str(call) for call in echo_calls)

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_gestion_user(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_gestion_user):
        """Test main menu display for gestion user, ensuring user management is shown"""
        # Setup
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "4"

        # Execute
        result = self.main_view.show_main_menu(mock_gestion_user)

        # Verify screen was cleared and result returned
        mock_clear.assert_called_once()
        assert mock_echo.call_count > 0
        assert result == "4"

        # Check that user management option IS shown (using correct emoji)
        assert any("👤 Gestion des utilisateurs" in str(arg) for call in mock_echo.call_args_list for
                   arg in call.args), "Expected '👤 Gestion des utilisateurs' in echo output for GESTION user"

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_basic_options_always_shown(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "1"

        self.main_view.show_main_menu(mock_user)

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        echo_text = " ".join(str(call) for call in echo_calls)

        assert "👥 Gestion des clients" in echo_text
        assert "📄 Gestion des contrats" in echo_text
        assert "🎉 Gestion des événements" in echo_text
        assert "🚪 Se déconnecter" in echo_text

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_user_info_displayed(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "0"

        self.main_view.show_main_menu(mock_user)

        mock_style.assert_any_call(f"EPIC EVENTS CRM - {mock_user.name}")
        mock_style.assert_any_call(f"Rôle: {mock_user.role.value.upper()}")

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_prompt_styling(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "1"

        self.main_view.show_main_menu(mock_user)

        mock_prompt.assert_called_once_with("Votre choix", type=str)

    @patch('app.views.main_view.click.clear')
    @patch('app.views.main_view.click.echo')
    @patch('app.views.main_view.click.prompt')
    @patch('app.views.main_view.click.style')
    def test_show_main_menu_return_value_stripped(self, mock_style, mock_prompt, mock_echo, mock_clear, mock_user):
        mock_style.side_effect = lambda x: x
        mock_prompt.return_value = "  2  "

        result = self.main_view.show_main_menu(mock_user)

        assert result == "2"
