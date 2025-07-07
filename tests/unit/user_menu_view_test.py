import pytest
from unittest.mock import Mock, patch
from app.views.user_menu_view import UserMenuView
from app.models.user import UserRole


class TestUserMenuView:
    def setup_method(self):
        self.user_menu_view = UserMenuView()

    def create_mock_user(self, user_id, name, email, role):
        user = Mock()
        user.id = user_id
        user.name = name
        user.email = email
        user.role = role
        return user

    @patch('app.views.user_menu_view.click.clear')
    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_show_users_menu(self, mock_prompt, mock_echo, mock_clear):
        mock_prompt.return_value = "1"
        result = self.user_menu_view.show_users_menu()
        mock_clear.assert_called_once()
        assert mock_echo.call_count > 0
        assert result == "1"

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_data_success(self, mock_prompt, mock_echo):
        mock_prompt.side_effect = ["John Doe", "john@example.com", "password123", "password123"]
        with patch.object(self.user_menu_view, 'get_role_selection', return_value=UserRole.COMMERCIAL):
            result = self.user_menu_view.get_user_data()
            assert result['name'] == "John Doe"
            assert result['email'] == "john@example.com"
            assert result['password'] == "password123"
            assert result['role'] == UserRole.COMMERCIAL

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_data_password_mismatch(self, mock_prompt, mock_echo):
        mock_prompt.side_effect = ["John Doe", "john@example.com", "pass1", "pass2"]
        result = self.user_menu_view.get_user_data()
        assert result is None
        mock_echo.assert_any_call("❌ Les mots de passe ne correspondent pas.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_data_role_selection_cancelled(self, mock_prompt, mock_echo):
        mock_prompt.side_effect = ["John Doe", "john@example.com", "password123", "password123"]
        with patch.object(self.user_menu_view, 'get_role_selection', return_value=None):
            result = self.user_menu_view.get_user_data()
            assert result is None

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    @patch('app.views.user_menu_view.click.confirm')
    def test_get_user_update_data_no_changes(self, mock_confirm, mock_prompt, mock_echo, mock_user):
        mock_prompt.side_effect = ["John Updated", "updated@example.com"]
        mock_confirm.side_effect = [False, False]
        result = self.user_menu_view.get_user_update_data(mock_user)
        assert result['name'] == "John Updated"
        assert result['email'] == "updated@example.com"
        assert result['password'] is None
        assert result['role'] == mock_user.role

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    @patch('app.views.user_menu_view.click.confirm')
    def test_get_user_update_data_with_password_change(self, mock_confirm, mock_prompt, mock_echo, mock_user):
        mock_prompt.side_effect = ["John Updated", "updated@example.com", "newpass", "newpass"]
        mock_confirm.side_effect = [True, False]
        result = self.user_menu_view.get_user_update_data(mock_user)
        assert result['password'] == "newpass"

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    @patch('app.views.user_menu_view.click.confirm')
    def test_get_user_update_data_password_mismatch(self, mock_confirm, mock_prompt, mock_echo, mock_user):
        mock_prompt.side_effect = ["John Updated", "updated@example.com", "pass1", "pass2"]
        mock_confirm.side_effect = [True]
        result = self.user_menu_view.get_user_update_data(mock_user)
        assert result is None
        mock_echo.assert_any_call("❌ Les mots de passe ne correspondent pas.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    @patch('app.views.user_menu_view.click.confirm')
    def test_get_user_update_data_with_role_change(self, mock_confirm, mock_prompt, mock_echo, mock_user):
        mock_prompt.side_effect = ["John Updated", "updated@example.com"]
        mock_confirm.side_effect = [False, True]
        with patch.object(self.user_menu_view, 'get_role_selection', return_value=UserRole.SUPPORT):
            result = self.user_menu_view.get_user_update_data(mock_user)
            assert result['role'] == UserRole.SUPPORT

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    @patch('app.views.user_menu_view.click.confirm')
    def test_get_user_update_data_role_change_cancelled(self, mock_confirm, mock_prompt, mock_echo, mock_user):
        mock_prompt.side_effect = ["John Updated", "updated@example.com"]
        mock_confirm.side_effect = [False, True]
        with patch.object(self.user_menu_view, 'get_role_selection', return_value=None):
            result = self.user_menu_view.get_user_update_data(mock_user)
            assert result is None

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_role_selection_valid_choice(self, mock_prompt, mock_echo):
        mock_prompt.return_value = 1
        result = self.user_menu_view.get_role_selection()
        assert result == UserRole.COMMERCIAL

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_role_selection_cancel(self, mock_prompt, mock_echo):
        mock_prompt.return_value = 0
        result = self.user_menu_view.get_role_selection()
        assert result is None

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_role_selection_invalid_choice(self, mock_prompt, mock_echo):
        mock_prompt.return_value = 99
        result = self.user_menu_view.get_role_selection()
        assert result is None
        mock_echo.assert_any_call("Choix invalide.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_role_selection_value_error(self, mock_prompt, mock_echo):
        mock_prompt.side_effect = ValueError("Invalid input")
        result = self.user_menu_view.get_role_selection()
        assert result is None
        mock_echo.assert_any_call("Veuillez entrer un nombre valide.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.pause')
    def test_display_users_list_with_users(self, mock_pause, mock_echo):
        users = [
            self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL),
            self.create_mock_user(2, "Jane Smith", "jane@example.com", UserRole.SUPPORT)
        ]
        self.user_menu_view.display_users_list(users)
        assert mock_echo.call_count > 0
        mock_pause.assert_called_once()

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.pause')
    def test_display_users_list_empty(self, mock_pause, mock_echo):
        self.user_menu_view.display_users_list([])
        mock_echo.assert_any_call("Aucun utilisateur trouvé.")
        mock_pause.assert_not_called()

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_selection_valid_choice(self, mock_prompt, mock_echo):
        users = [self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL)]
        mock_prompt.return_value = 1
        result = self.user_menu_view.get_user_selection(users)
        assert result == users[0]

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_selection_cancel(self, mock_prompt, mock_echo):
        users = [self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL)]
        mock_prompt.return_value = 0
        result = self.user_menu_view.get_user_selection(users)
        assert result is None

    @patch('app.views.user_menu_view.click.echo')
    def test_get_user_selection_empty_list(self, mock_echo):
        result = self.user_menu_view.get_user_selection([])
        assert result is None
        mock_echo.assert_any_call("Aucun utilisateur disponible.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_selection_invalid_choice(self, mock_prompt, mock_echo):
        users = [self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL)]
        mock_prompt.return_value = 99
        result = self.user_menu_view.get_user_selection(users)
        assert result is None
        mock_echo.assert_any_call("Choix invalide.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_selection_value_error(self, mock_prompt, mock_echo):
        users = [self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL)]
        mock_prompt.side_effect = ValueError("Invalid input")
        result = self.user_menu_view.get_user_selection(users)
        assert result is None
        mock_echo.assert_any_call("Veuillez entrer un nombre valide.")

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.prompt')
    def test_get_user_selection_custom_action(self, mock_prompt, mock_echo):
        users = [self.create_mock_user(1, "John Doe", "john@example.com", UserRole.COMMERCIAL)]
        mock_prompt.return_value = 1
        result = self.user_menu_view.get_user_selection(users, action="modifier")
        assert result == users[0]
        mock_prompt.assert_called_with("Sélectionnez un utilisateur à modifier", type=int)

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.confirm')
    def test_confirm_user_deletion_confirmed(self, mock_confirm, mock_echo):
        user = self.create_mock_user(1, "John Doe", "john@example.com", UserRole.SUPPORT)
        mock_confirm.return_value = True
        result = self.user_menu_view.confirm_user_deletion(user)
        assert result is True

    @patch('app.views.user_menu_view.click.echo')
    @patch('app.views.user_menu_view.click.confirm')
    def test_confirm_user_deletion_cancelled(self, mock_confirm, mock_echo):
        user = self.create_mock_user(1, "John Doe", "john@example.com", UserRole.SUPPORT)
        mock_confirm.return_value = False
        result = self.user_menu_view.confirm_user_deletion(user)
        assert result is False

    @patch('app.views.user_menu_view.click.echo')
    def test_show_user_details(self, mock_echo):
        user = self.create_mock_user(1, "John Doe", "john@example.com", UserRole.SUPPORT)
        self.user_menu_view.show_user_details(user)
        mock_echo.assert_any_call("👤 DÉTAILS DE L'UTILISATEUR")
        mock_echo.assert_any_call(f"Nom: {user.name}")
        mock_echo.assert_any_call(f"Email: {user.email}")
        mock_echo.assert_any_call(f"Rôle: {user.role.value.title()}")
