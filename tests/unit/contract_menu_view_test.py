from unittest.mock import patch

from app.views.contract_menu_view import ContractMenuView
from app.models.user import UserRole


class TestContractMenuView:
    """Test suite for ContractMenuView"""

    def test_show_contracts_menu_gestion(self, mock_gestion_user):
        view = ContractMenuView()

        with patch('click.clear'), patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "1"
            result = view.show_contracts_menu(mock_gestion_user)
            assert result == "1"

    def test_show_contracts_menu_commercial(self, mock_user):
        mock_user.role = UserRole.COMMERCIAL
        view = ContractMenuView()

        with patch('click.clear'), patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "3"
            result = view.show_contracts_menu(mock_user)
            assert result == "3"

    def test_get_contract_data_success(self, mock_client):
        view = ContractMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt, \
             patch('click.confirm') as mock_confirm, \
             patch.object(view, 'get_client_selection') as mock_get_client:
            mock_get_client.return_value = mock_client
            mock_prompt.side_effect = [10000.0, 5000.0]
            mock_confirm.return_value = False

            result = view.get_contract_data([mock_client])

            assert result['client_id'] == mock_client.id
            assert result['total_amount'] == 10000.0
            assert result['amount_due'] == 5000.0
            assert result['is_signed'] is False

    def test_get_contract_data_cancelled(self, mock_client):
        view = ContractMenuView()

        with patch.object(view, 'get_client_selection') as mock_get_client:
            mock_get_client.return_value = None

            result = view.get_contract_data([mock_client])
            assert result is None

    def test_display_contracts_list_empty(self):
        view = ContractMenuView()

        with patch('click.echo') as mock_echo:
            view.display_contracts_list([])
            mock_echo.assert_any_call("Aucun contrat trouvé.")

    def test_display_contracts_list_with_data(self, mock_contract, mock_client, mock_user):
        view = ContractMenuView()
        mock_contract.client = mock_client
        mock_contract.commercial = mock_user

        with patch('click.echo') as mock_echo:
            view.display_contracts_list([mock_contract])
            mock_echo.assert_any_call(f"ID: {mock_contract.id} | Client: {mock_contract.client.full_name}")

    def test_get_contract_selection_success(self, mock_contract, mock_client):
        view = ContractMenuView()
        mock_contract.client = mock_client

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = 1
            result = view.get_contract_selection([mock_contract])
            assert result == mock_contract

    def test_get_contract_selection_cancelled(self, mock_contract):
        view = ContractMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = 0
            result = view.get_contract_selection([mock_contract])
            assert result is None

    def test_get_contract_filter(self):
        view = ContractMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "1"
            result = view.get_contract_filter()
            assert result == "unsigned"

    def test_get_client_selection_empty(self):
        view = ContractMenuView()

        with patch('click.echo') as mock_echo:
            result = view.get_client_selection([])
            assert result is None
            mock_echo.assert_called_with("Aucun client disponible.")
