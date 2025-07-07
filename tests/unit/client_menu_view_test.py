import pytest
from unittest.mock import patch, Mock
from app.views.client_menu_view import ClientMenuView
from app.models.user import UserRole


@pytest.mark.usefixtures("mock_user")
class TestClientMenuView:
    @pytest.fixture
    def client_menu_view(self):
        return ClientMenuView()

    @patch("click.prompt")
    @patch("click.echo")
    @patch("click.clear")
    def test_show_clients_menu_commercial_user(self, mock_clear, mock_echo, mock_prompt, client_menu_view, mock_user):
        mock_user.role = UserRole.COMMERCIAL
        mock_prompt.return_value = "1"

        result = client_menu_view.show_clients_menu(mock_user)

        mock_clear.assert_called_once()
        mock_prompt.assert_called_once()
        assert result == "1"

        output = " ".join(str(call.args[0]) for call in mock_echo.call_args_list if call.args)
        assert "Créer un nouveau client" in output
        assert "Modifier un client" in output

    @patch("click.prompt")
    @patch("click.echo")
    @patch("click.clear")
    def test_show_clients_menu_support_user(self, mock_clear, mock_echo, mock_prompt, client_menu_view, mock_support_user):
        mock_support_user.role = UserRole.SUPPORT
        mock_prompt.return_value = "1"

        result = client_menu_view.show_clients_menu(mock_support_user)

        output = " ".join(str(call.args[0]) for call in mock_echo.call_args_list if call.args)
        assert "Créer un nouveau client" not in output
        assert "Modifier un client" not in output
        assert result == "1"

    @patch("click.prompt")
    @patch("click.echo")
    @patch("click.clear")
    def test_show_clients_menu_gestion_user(self, mock_clear, mock_echo, mock_prompt, client_menu_view, mock_gestion_user):
        mock_gestion_user.role = UserRole.GESTION
        mock_prompt.return_value = "1"

        result = client_menu_view.show_clients_menu(mock_gestion_user)

        output = " ".join(str(call.args[0]) for call in mock_echo.call_args_list if call.args)
        assert "Créer un nouveau client" not in output
        assert "Modifier un client" not in output
        assert result == "1"

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_data_success(self, mock_echo, mock_prompt, mock_confirm, client_menu_view, sample_client_data):
        mock_prompt.side_effect = [
            sample_client_data["full_name"],
            sample_client_data["email"],
            sample_client_data["phone"],
            sample_client_data["company_name"]
        ]
        mock_confirm.return_value = True

        result = client_menu_view.get_client_data()

        assert result == sample_client_data

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_data_invalid_cases(self, mock_echo, mock_prompt, mock_confirm, client_menu_view):
        cases = [
            (["", "email", "phone", "company"], "❌ Le nom complet est obligatoire."),
            (["Name", "", "phone", "company"], "❌ L'email est obligatoire."),
            (["Name", "invalid", "phone", "company"], "❌ Format d'email invalide."),
        ]
        for side_effects, expected_error in cases:
            mock_prompt.side_effect = side_effects
            result = client_menu_view.get_client_data()
            assert result is None
            mock_echo.assert_any_call(expected_error)

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_data_cancelled_by_user(self, mock_echo, mock_prompt, mock_confirm, client_menu_view, sample_client_data):
        mock_prompt.side_effect = [
            sample_client_data["full_name"],
            sample_client_data["email"],
            sample_client_data["phone"],
            sample_client_data["company_name"]
        ]
        mock_confirm.return_value = False

        result = client_menu_view.get_client_data()
        assert result is None

    @patch("click.echo")
    def test_display_clients_list_empty(self, mock_echo, client_menu_view):
        client_menu_view.display_clients_list([])
        mock_echo.assert_any_call("Aucun client trouvé.")

    @patch('click.echo')
    def test_display_clients_list_with_clients(self, mock_echo, client_menu_view, mock_client):
        """Test displaying clients list with clients"""
        # Create a mock commercial for the client
        mock_commercial = Mock()
        mock_commercial.name = "Commercial Name"
        mock_client.commercial = mock_commercial

        clients = [mock_client]
        client_menu_view.display_clients_list(clients)

        # Build expected echoed lines
        expected_lines = [
            "📋 LISTE DES CLIENTS",
            "=" * 100,
            f"1. ID: {mock_client.id}",
            f"   👤 {mock_client.full_name}",
            f"   🏢 {mock_client.company_name or 'Entreprise non renseignée'}",
            f"   📧 {mock_client.email}",
            f"   📞 {mock_client.phone or 'Téléphone non renseigné'}",
            f"   👨‍💼 Commercial: {mock_commercial.name}",
            f"\n Total: {len(clients)} client(s)"
        ]

        # Extract actual echoed text
        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]

        # Assert each expected line is in the echoed output
        for line in expected_lines:
            assert any(line in echoed for echoed in echo_calls), f"Expected line not found: {line}"

    @patch("click.echo")
    def test_display_clients_list_missing_fields(self, mock_echo, client_menu_view):
        mock_client = Mock()
        mock_client.id = 1
        mock_client.full_name = "Client"
        mock_client.email = "client@example.com"
        mock_client.phone = None
        mock_client.company_name = None
        mock_client.commercial = None

        client_menu_view.display_clients_list([mock_client])

        mock_echo.assert_any_call("   🏢 Entreprise non renseignée")
        mock_echo.assert_any_call("   📞 Téléphone non renseigné")
        mock_echo.assert_any_call("   👨‍💼 Commercial: Non assigné")

    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_selection_valid(self, mock_echo, mock_prompt, client_menu_view, mock_client):
        mock_prompt.return_value = 1
        result = client_menu_view.get_client_selection([mock_client])
        assert result == mock_client

    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_selection_cancel_and_invalid(self, mock_echo, mock_prompt, client_menu_view, mock_client):
        mock_prompt.side_effect = [0, 99, ValueError("bad"), KeyboardInterrupt()]

        for _ in range(4):
            result = client_menu_view.get_client_selection([mock_client])
            assert result is None
        assert mock_echo.call_count >= 4

    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_selection_empty(self, mock_echo, mock_prompt, client_menu_view):
        result = client_menu_view.get_client_selection([])
        assert result is None
        mock_echo.assert_any_call("Aucun client disponible.")

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_update_data_valid(self, mock_echo, mock_prompt, mock_confirm, client_menu_view, mock_client):
        mock_prompt.side_effect = ["New Name", "new@email.com", "987654", "NewCorp"]
        mock_confirm.return_value = True

        result = client_menu_view.get_client_update_data(mock_client)
        assert result == {
            "full_name": "New Name",
            "email": "new@email.com",
            "phone": "987654",
            "company_name": "NewCorp",
        }

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_update_data_no_changes(self, mock_echo, mock_prompt, mock_confirm, client_menu_view, mock_client):
        mock_prompt.side_effect = [
            mock_client.full_name,
            mock_client.email,
            mock_client.phone,
            mock_client.company_name,
        ]
        mock_confirm.return_value = False

        result = client_menu_view.get_client_update_data(mock_client)
        assert result is None
        mock_echo.assert_any_call("Aucune modification détectée.")

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_update_data_invalid_email_or_empty_name(self, mock_echo, mock_prompt, mock_confirm, client_menu_view, mock_client):
        # Invalid email
        mock_prompt.side_effect = ["Updated", "wrong_email", "phone", "corp"]
        result = client_menu_view.get_client_update_data(mock_client)
        assert result is None
        mock_echo.assert_any_call("❌ Format d'email invalide.")

        # Empty name
        mock_prompt.side_effect = ["", mock_client.email, mock_client.phone, mock_client.company_name]
        result = client_menu_view.get_client_update_data(mock_client)
        assert result is None
        mock_echo.assert_any_call("❌ Le nom complet ne peut pas être vide.")

    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_data_keyboard_interrupt(self, mock_echo, mock_prompt, client_menu_view):
        mock_prompt.side_effect = KeyboardInterrupt()
        result = client_menu_view.get_client_data()
        assert result is None

    @patch("click.prompt")
    @patch("click.echo")
    def test_get_client_update_data_keyboard_interrupt(self, mock_echo, mock_prompt, client_menu_view, mock_client):
        mock_prompt.side_effect = KeyboardInterrupt()
        result = client_menu_view.get_client_update_data(mock_client)
        assert result is None
